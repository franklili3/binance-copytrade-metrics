"""Transform Binance API payloads into relational rows."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

Number = Optional[float]


def _parse_float(value: Any) -> Number:
    try:
        if value in (None, "", "null"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_int(value: Any) -> Optional[int]:
    try:
        if value in (None, "", "null"):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def build_overview_row(data: Mapping[str, Any]) -> MutableMapping[str, Any]:
    tag = None
    tags = data.get("tagItemVos") or []
    if tags:
        tag = tags[0]

    row: MutableMapping[str, Any] = {
        "leadPortfolioId": data.get("leadPortfolioId"),
        "favoriteCount": _parse_int(data.get("favoriteCount")),
        "currentCopyCount": _parse_int(data.get("currentCopyCount")),
        "maxCopyCount": _parse_int(data.get("maxCopyCount")),
        "totalCopyCount": _parse_int(data.get("totalCopyCount")),
        "walletBalanceAmount": _parse_float(data.get("walletBalanceAmount")),
        "walletBalanceAsset": data.get("walletBalanceAsset"),
        "currentInvestAmount": _parse_float(data.get("currentInvestAmount")),
        "currentAvailableAmount": _parse_float(data.get("currentAvailableAmount")),
        "aumAmount": _parse_float(data.get("aumAmount")),
        "aumAsset": data.get("aumAsset"),
        "badgeName": data.get("badgeName"),
        "badgeCopierCount": _parse_int(data.get("badgeCopierCount")),
        "tagName": (tag or {}).get("name"),
        "tag_days": (tag or {}).get("days"),
        "tag_ranking": (tag or {}).get("ranking"),
        "tag_sort": (tag or {}).get("sort"),
        "copyMockCount": _parse_int(data.get("copyMockCount")),
        "dataUpdatedAt": data.get("lastTradeTime") or data.get("badgeModifyTime"),
        "datetime": _utc_now_iso(),
    }
    return row


def build_performance_row(
    lead_portfolio_id: str,
    time_range: str,
    data: Mapping[str, Any],
) -> MutableMapping[str, Any]:
    return {
        "leadPortfolioId": lead_portfolio_id,
        "timeRange": time_range,
        "roi": _parse_float(data.get("roi")),
        "pnl": _parse_float(data.get("pnl")),
        "mdd": _parse_float(data.get("mdd")),
        "copierPnl": _parse_float(data.get("copierPnl")),
        "winRate": _parse_float(data.get("winRate")),
        "winDays": _parse_int(data.get("winDays")),
        "sharpRatio": _parse_float(data.get("sharpRatio")),
        "dataUpdatedAt": data.get("dataUpdatedAt"),
        "datetime": _utc_now_iso(),
    }


def build_holdings_rows(
    lead_portfolio_id: str,
    holdings: Iterable[Mapping[str, Any]],
) -> List[MutableMapping[str, Any]]:
    rows: List[MutableMapping[str, Any]] = []
    for item in holdings:
        rows.append(
            {
                "leadPortfolioId": lead_portfolio_id,
                "Assets": item.get("asset") or item.get("symbol"),
                "Time_Updated": item.get("updateTime") or item.get("timeUpdated"),
                "Remain_Amount": _parse_float(item.get("remainAmount")),
                "Buy_Amount": _parse_float(item.get("buyAmount")),
                "Avg_Buy_Price": _parse_float(item.get("avgBuyPrice")),
                "Last_Price": _parse_float(item.get("lastPrice")),
                "Unrealized_PNL": _parse_float(item.get("unrealizedPnl")),
                "Realized_PNL": _parse_float(item.get("realizedPnl")),
            }
        )
    return rows


def build_trade_history_rows(
    lead_portfolio_id: str,
    trades: Iterable[Mapping[str, Any]],
) -> List[MutableMapping[str, Any]]:
    rows: List[MutableMapping[str, Any]] = []
    for trade in trades:
        rows.append(
            {
                "leadPortfolioId": lead_portfolio_id,
                "Time": trade.get("time") or trade.get("transactTime"),
                "Pair": trade.get("pair") or trade.get("symbol"),
                "Side": trade.get("side"),
                "Executed": _parse_float(trade.get("executedQty")),
                "Role": trade.get("role"),
                "Total": _parse_float(trade.get("total")),
            }
        )
    return rows


def build_balance_history_rows(
    lead_portfolio_id: str,
    balances: Iterable[Mapping[str, Any]],
) -> List[MutableMapping[str, Any]]:
    rows: List[MutableMapping[str, Any]] = []
    for entry in balances:
        rows.append(
            {
                "leadPortfolioId": lead_portfolio_id,
                "Coin": entry.get("coin") or entry.get("asset"),
                "Time": entry.get("time"),
                "Amount": _parse_float(entry.get("amount")),
                "From": entry.get("source") or entry.get("from"),
                "To": entry.get("target") or entry.get("to"),
            }
        )
    return rows


def build_copy_trader_rows(
    lead_portfolio_id: str,
    traders: Iterable[Mapping[str, Any]],
) -> List[MutableMapping[str, Any]]:
    rows: List[MutableMapping[str, Any]] = []
    for trader in traders:
        rows.append(
            {
                "leadPortfolioId": lead_portfolio_id,
                "User_ID": trader.get("userId") or trader.get("user_id"),
                "Amount": _parse_float(trader.get("amount")),
                "Total_PNL": _parse_float(trader.get("totalPnl")),
                "Total_ROI": _parse_float(trader.get("totalRoi")),
                "Duration": trader.get("duration"),
            }
        )
    return rows


__all__ = [
    "build_overview_row",
    "build_performance_row",
    "build_holdings_rows",
    "build_trade_history_rows",
    "build_balance_history_rows",
    "build_copy_trader_rows",
]
