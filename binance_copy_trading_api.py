"""Utilities for fetching Binance copy trading lead account history data.

This module provides a small client that wraps the Binance Copy Trading API
endpoints required by the user request.  The focus is on lead accounts because
only lead traders have access to their full positions, trade history and daily
return statistics through the authenticated API.

The implementation purposely keeps its external surface minimal so it can be
used both as a library from other scripts as well as a standalone command line
tool.  The command line interface performs three requests and persists the raw
payloads into a JSON file so that subsequent processing can happen offline.

The Binance Copy Trading API is a signed API which means that every request
must include the current timestamp and a signature derived from the private API
secret.  The :class:`BinanceCopyTradingClient` encapsulates the signing logic
and exposes convenience helpers for the required endpoints.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

import ccxt
from ccxt.base.errors import BaseError as CCXTBaseError
from dotenv import load_dotenv
from supabase import Client, create_client


class BinanceAPIError(RuntimeError):
    """Raised when the Binance API returns an error payload."""

    def __init__(
        self,
        message: str,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.payload = payload


def _ensure_utc(dt: datetime) -> datetime:
    """Return a timezone-aware datetime in UTC."""

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def coerce_to_milliseconds(value: Optional[Any]) -> Optional[int]:
    """Convert supported inputs into a millisecond timestamp.

    Parameters
    ----------
    value:
        * ``None`` – returned unchanged.
        * ``int``/``float`` – returned as integers.
        * ``datetime`` – converted to UTC milliseconds.
        * ``str`` – interpreted as ISO-8601 date/datetime or a millisecond
          integer string.
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        return int(_ensure_utc(value).timestamp() * 1000)

    if isinstance(value, (int, float)):
        return int(value)

    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return int(stripped)

        normalised = stripped.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalised)
        except ValueError as exc:  # pragma: no cover - defensive fallback
            raise ValueError(
                f"Unsupported datetime format: {value}"
            ) from exc
        return int(_ensure_utc(parsed).timestamp() * 1000)

    raise TypeError(f"Unsupported timestamp value: {value!r}")


def default_time_range(days: int = 30) -> tuple[int, int]:
    """Return a default time window covering ``days`` days up to now."""

    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=days)
    return (int(start_dt.timestamp() * 1000), int(end_dt.timestamp() * 1000))


@dataclass
class BinanceCopyTradingClient:
    """Minimal client wrapper around the Binance Copy Trading API."""

    api_key: str
    api_secret: str
    recv_window: int = 5000
    _exchange: ccxt.binance = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.api_key:
            raise ValueError("API key is required")
        if not self.api_secret:
            raise ValueError("API secret is required")

        self._exchange = ccxt.binance(
            {
                "apiKey": self.api_key,
                "secret": self.api_secret,
                "options": {
                    "adjustForTimeDifference": True,
                    "recvWindow": self.recv_window,
                },
            }
        )

        try:
            self._exchange.check_required_credentials()
        except CCXTBaseError as exc:  # pragma: no cover - defensive fallback
            raise BinanceAPIError(
                f"Invalid Binance credentials: {exc}"
            ) from exc

    def _call(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        params = dict(params or {})
        params.setdefault("recvWindow", self.recv_window)
        try:
            endpoint = getattr(self._exchange, method)
        except AttributeError as exc:  # pragma: no cover - defensive fallback
            raise ValueError(
                f"Unsupported Binance API method: {method}"
            ) from exc

        try:
            return endpoint(params)
        except CCXTBaseError as exc:
            raise BinanceAPIError(str(exc)) from exc

    def _time_params(
        self, start_time: Optional[Any], end_time: Optional[Any]
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if (start := coerce_to_milliseconds(start_time)) is not None:
            params["startTime"] = start
        if (end := coerce_to_milliseconds(end_time)) is not None:
            params["endTime"] = end
        return params

    # -- public API ------------------------------------------------------

    def positions_history(
        self,
        start_time: Optional[Any] = None,
        end_time: Optional[Any] = None,
        limit: Optional[int] = None,
    ) -> Any:
        params = self._time_params(start_time, end_time)
        if limit is not None:
            params["limit"] = limit
        return self._call("sapi_get_copytrading_lead_positions", params)

    def trade_history(
        self,
        start_time: Optional[Any] = None,
        end_time: Optional[Any] = None,
        limit: Optional[int] = None,
        from_id: Optional[int] = None,
    ) -> Any:
        params = self._time_params(start_time, end_time)
        if limit is not None:
            params["limit"] = limit
        if from_id is not None:
            params["fromId"] = from_id
        return self._call("sapi_get_copytrading_lead_orderhistory", params)

    def daily_returns(
        self,
        start_time: Optional[Any] = None,
        end_time: Optional[Any] = None,
    ) -> Any:
        params = self._time_params(start_time, end_time)
        return self._call("sapi_get_copytrading_lead_dailyreturn", params)


@dataclass
class SupabaseUploader:
    """Tiny helper for inserting rows into Supabase tables."""

    project_url: str
    api_key: str
    client: Optional[Client] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if not self.project_url:
            raise ValueError("Supabase project URL is required")
        if not self.api_key:
            raise ValueError("Supabase API key is required")
        self.project_url = self.project_url.rstrip("/")
        if self.client is None:
            self.client = create_client(self.project_url, self.api_key)

    def insert(self, table: str, rows: Iterable[Mapping[str, Any]]) -> None:
        payload = list(rows)
        if not payload:
            return

        assert self.client is not None  # for type-checkers
        response = self.client.table(table).upsert(payload).execute()
        error = getattr(response, "error", None)
        if error:
            raise RuntimeError(
                "Failed to insert data into Supabase table "
                f"{table}: {error}"
            )


def load_credentials(
    api_key: Optional[str] = None, api_secret: Optional[str] = None
) -> tuple[str, str]:
    """Load API credentials from explicit arguments or the environment."""

    load_dotenv()

    env_candidates = [
        "BINANCE_API_KEY",
        "BINANCE_APIKEY",
        "BINANCE_KEY",
        "API_KEY",
        "api_key",
    ]

    secret_candidates = [
        "BINANCE_API_SECRET",
        "BINANCE_SECRET_KEY",
        "BINANCE_SECRET",
        "API_SECRET",
        "api_secret",
    ]

    resolved_key = api_key or _first_present(env_candidates)
    resolved_secret = api_secret or _first_present(secret_candidates)

    if not resolved_key or not resolved_secret:
        raise ValueError(
            "Binance API credentials are required. Provide them via "
            "command line arguments or environment variables such as "
            "BINANCE_API_KEY and BINANCE_API_SECRET."
        )

    return resolved_key, resolved_secret


def load_supabase_credentials(
    project_url: Optional[str] = None, api_key: Optional[str] = None
) -> tuple[str, str]:
    """Load Supabase credentials from explicit arguments or the environment."""

    load_dotenv()

    url = project_url or _first_present(
        [
            "SUPABASE_PROJECT_URL",
            "SUPABASE_URL",
            "supabase_project_url",
            "supabase_url",
        ]
    )
    key = api_key or _first_present(
        [
            "SUPABASE_API_KEY",
            "SUPABASE_SERVICE_KEY",
            "SUPABASE_KEY",
            "supabase_api_key",
        ]
    )

    if not url or not key:
        raise ValueError(
            "Supabase credentials are required. Provide them via command line "
            "arguments or environment variables such as SUPABASE_PROJECT_URL "
            "and SUPABASE_API_KEY."
        )

    return url, key


def _first_present(names: list[str]) -> Optional[str]:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def _normalise_records(block: Any) -> List[Mapping[str, Any]]:
    """Return a list of mapping rows from various response shapes."""

    if block is None:
        return []

    if isinstance(block, list):
        return [row for row in block if isinstance(row, Mapping)]

    if isinstance(block, Mapping):
        for key in ("data", "rows", "list", "items", "records"):
            candidate = block.get(key)
            if isinstance(candidate, list):
                return _normalise_records(candidate)
        return [block]

    raise TypeError(f"Unsupported record container: {type(block)!r}")


def upload_history_to_supabase(
    uploader: SupabaseUploader,
    history: Mapping[str, Any],
    table_mapping: Mapping[str, str],
) -> None:
    """Upload history payloads to Supabase using the provided table mapping."""

    for key, table in table_mapping.items():
        rows = _normalise_records(history.get(key))
        uploader.insert(table, rows)


def fetch_copy_trading_history(
    client: BinanceCopyTradingClient,
    start_time: Optional[Any] = None,
    end_time: Optional[Any] = None,
    limit: Optional[int] = None,
    from_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Fetch positions, trades and daily return history in a single call."""

    history: Dict[str, Any] = {}

    history["positions"] = client.positions_history(
        start_time, end_time, limit
    )
    history["trades"] = client.trade_history(
        start_time, end_time, limit, from_id
    )
    history["daily_returns"] = client.daily_returns(
        start_time, end_time
    )

    return history


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Binance copy trading lead account history (positions, "
            "trade history and daily returns) and store the raw response as "
            "JSON."
        )
    )

    parser.add_argument(
        "--start-date",
        help=(
            "Start date for history requests. Accepts ISO-8601 strings (e.g. "
            "2024-01-01 or 2024-01-01T00:00:00Z) or millisecond timestamps."
        ),
    )
    parser.add_argument(
        "--end-date",
        help=(
            "End date for history requests. Accepts ISO-8601 strings (e.g. "
            "2024-02-01 or 2024-02-01T23:59:59Z) or millisecond timestamps."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of entries to request for paginated endpoints.",
    )
    parser.add_argument(
        "--from-id",
        type=int,
        help="ID offset for paginated trade history queries.",
    )
    parser.add_argument(
        "--recv-window",
        type=int,
        default=5000,
        help="Custom recvWindow value in milliseconds (default: 5000).",
    )
    parser.add_argument(
        "--api-key",
        help="Binance API key. Overrides environment variables when provided.",
    )
    parser.add_argument(
        "--api-secret",
        help=(
            "Binance API secret. Overrides environment variables "
            "when provided."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("copy_trading_history.json"),
        help="Destination JSON file for the retrieved data.",
    )
    parser.add_argument(
        "--supabase-url",
        help=(
            "Supabase project URL. Overrides environment variables when "
            "provided."
        ),
    )
    parser.add_argument(
        "--supabase-key",
        help=(
            "Supabase API key. Overrides environment variables when provided."
        ),
    )
    parser.add_argument(
        "--positions-table",
        default=os.environ.get(
            "SUPABASE_POSITIONS_TABLE", "copy_trading_positions"
        ),
        help="Supabase table name for positions history data.",
    )
    parser.add_argument(
        "--trades-table",
        default=os.environ.get(
            "SUPABASE_TRADES_TABLE", "copy_trading_trades"
        ),
        help="Supabase table name for trade history data.",
    )
    parser.add_argument(
        "--daily-returns-table",
        default=os.environ.get(
            "SUPABASE_DAILY_RETURNS_TABLE", "copy_trading_daily_returns"
        ),
        help="Supabase table name for daily return data.",
    )

    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.start_date or args.end_date:
        start = (
            coerce_to_milliseconds(args.start_date)
            if args.start_date
            else None
        )
        end = (
            coerce_to_milliseconds(args.end_date)
            if args.end_date
            else None
        )
    else:
        start, end = default_time_range(days=30)

    key, secret = load_credentials(args.api_key, args.api_secret)

    client = BinanceCopyTradingClient(
        api_key=key,
        api_secret=secret,
        recv_window=args.recv_window,
    )

    supabase_url, supabase_key = load_supabase_credentials(
        args.supabase_url, args.supabase_key
    )
    uploader = SupabaseUploader(project_url=supabase_url, api_key=supabase_key)

    try:
        history = fetch_copy_trading_history(
            client,
            start_time=start,
            end_time=end,
            limit=args.limit,
            from_id=args.from_id,
        )
    except BinanceAPIError as exc:
        raise SystemExit(f"Failed to fetch data from Binance: {exc}") from exc

    args.output.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    upload_history_to_supabase(
        uploader,
        history,
        {
            "positions": args.positions_table,
            "trades": args.trades_table,
            "daily_returns": args.daily_returns_table,
        },
    )

    print(f"History saved to {args.output}")


if __name__ == "__main__":
    main()
