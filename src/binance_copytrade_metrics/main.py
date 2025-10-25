"""Command line interface for scraping Binance copy trading data."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Iterable

from .binance_api import BinanceCopyTradeClient
from .brightdata_client import BrightDataProxySession
from .storage import SQLiteStorage
from .transformers import (
    build_balance_history_rows,
    build_copy_trader_rows,
    build_holdings_rows,
    build_overview_row,
    build_performance_row,
    build_trade_history_rows,
)

LOGGER = logging.getLogger(__name__)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "lead_portfolio_id",
        help="Binance lead portfolio identifier to scrape",
    )
    parser.add_argument(
        "--database",
        default="binance_copytrade.db",
        help="Path to the SQLite database file (default: %(default)s)",
    )
    parser.add_argument(
        "--time-ranges",
        nargs="*",
        default=["180D", "90D", "30D", "7D"],
        help="Time ranges to request performance data for",
    )
    parser.add_argument(
        "--dump-json",
        action="store_true",
        help="Print the collected payloads instead of writing to the database",
    )
    return parser.parse_args(argv)


def collect_metrics(lead_portfolio_id: str, time_ranges: Iterable[str]) -> dict:
    proxy_session = BrightDataProxySession()
    client = BinanceCopyTradeClient(proxy_session)

    overview = client.get_overview(lead_portfolio_id)
    performance = {
        time_range: client.get_performance(lead_portfolio_id, time_range)
        for time_range in time_ranges
    }
    holdings = client.get_holdings(lead_portfolio_id)
    trades = client.get_trade_history(lead_portfolio_id)
    balances = client.get_balance_history(lead_portfolio_id)
    copy_traders = client.get_copy_traders(lead_portfolio_id)

    return {
        "overview": overview,
        "performance": performance,
        "holdings": holdings,
        "trade_history": trades,
        "balance_history": balances,
        "copy_traders": copy_traders,
    }


def persist_metrics(data: dict, lead_portfolio_id: str, database: Path | str) -> None:
    storage = SQLiteStorage(database)
    try:
        overview_row = build_overview_row(data["overview"])
        storage.upsert_overview(overview_row)

        performance_rows = [
            build_performance_row(lead_portfolio_id, rng, metrics)
            for rng, metrics in data["performance"].items()
        ]
        storage.upsert_performance(performance_rows)

        storage.replace_holdings(
            lead_portfolio_id,
            build_holdings_rows(lead_portfolio_id, data["holdings"]),
        )
        storage.replace_trade_history(
            lead_portfolio_id,
            build_trade_history_rows(lead_portfolio_id, data["trade_history"]),
        )
        storage.replace_balances(
            lead_portfolio_id,
            build_balance_history_rows(lead_portfolio_id, data["balance_history"]),
        )
        storage.replace_copy_traders(
            lead_portfolio_id,
            build_copy_trader_rows(lead_portfolio_id, data["copy_traders"]),
        )
    finally:
        storage.close()


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    LOGGER.info("Collecting data for lead portfolio %s", args.lead_portfolio_id)

    data = collect_metrics(args.lead_portfolio_id, args.time_ranges)

    if args.dump_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        persist_metrics(data, args.lead_portfolio_id, args.database)
        LOGGER.info("Data stored in %s", args.database)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
