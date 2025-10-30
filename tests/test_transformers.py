from __future__ import annotations

from binance_copytrade_metrics.transformers import (
    build_balance_history_rows,
    build_copy_trader_rows,
    build_holdings_rows,
    build_overview_row,
    build_performance_row,
    build_trade_history_rows,
)

OVERVIEW_SAMPLE = {
    "leadPortfolioId": "4458914342020236800",
    "favoriteCount": "123",
    "currentCopyCount": "10",
    "maxCopyCount": "200",
    "totalCopyCount": "500",
    "walletBalanceAmount": "12345.678",
    "walletBalanceAsset": "USDT",
    "currentInvestAmount": "234.5",
    "currentAvailableAmount": "12.34",
    "aumAmount": "45678.9",
    "aumAsset": "USDT",
    "badgeName": "Top Trader",
    "badgeCopierCount": "88",
    "tagItemVos": [
        {"name": "Top Performer", "days": "90", "ranking": "4", "sort": 3}
    ],
    "copyMockCount": "42",
    "lastTradeTime": "1710000000000",
}


PERFORMANCE_SAMPLE = {
    "roi": "35.54430844",
    "pnl": "64194.45986716",
    "mdd": "7.40776500",
    "copierPnl": "8651.31894666",
    "winRate": "97.92000000",
    "winDays": 188,
    "sharpRatio": "2.04514862",
    "dataUpdatedAt": "1710001000000",
}


def test_build_overview_row() -> None:
    row = build_overview_row(OVERVIEW_SAMPLE)
    assert row["leadPortfolioId"] == OVERVIEW_SAMPLE["leadPortfolioId"]
    assert row["favoriteCount"] == 123
    assert row["walletBalanceAmount"] == 12345.678
    assert row["tagName"] == "Top Performer"
    assert row["tag_days"] == "90"
    assert row["copyMockCount"] == 42
    assert row["dataUpdatedAt"] == "1710000000000"
    assert "datetime" in row


def test_build_performance_row() -> None:
    row = build_performance_row("lead", "180D", PERFORMANCE_SAMPLE)
    assert row["leadPortfolioId"] == "lead"
    assert row["timeRange"] == "180D"
    assert row["roi"] == 35.54430844
    assert row["winDays"] == 188
    assert row["dataUpdatedAt"] == "1710001000000"


HOLDINGS_SAMPLE = [
    {
        "asset": "BTC",
        "updateTime": "1709990000000",
        "remainAmount": "0.5",
        "buyAmount": "1.2",
        "avgBuyPrice": "40000",
        "lastPrice": "42000",
        "unrealizedPnl": "1000",
        "realizedPnl": "200",
    }
]


def test_build_holdings_rows() -> None:
    rows = build_holdings_rows("lead", HOLDINGS_SAMPLE)
    assert rows == [
        {
            "leadPortfolioId": "lead",
            "Assets": "BTC",
            "Time_Updated": "1709990000000",
            "Remain_Amount": 0.5,
            "Buy_Amount": 1.2,
            "Avg_Buy_Price": 40000.0,
            "Last_Price": 42000.0,
            "Unrealized_PNL": 1000.0,
            "Realized_PNL": 200.0,
        }
    ]


TRADE_SAMPLE = [
    {
        "time": "1709990001000",
        "pair": "BTCUSDT",
        "side": "BUY",
        "executedQty": "0.1",
        "role": "TAKER",
        "total": "4200",
    }
]


def test_build_trade_history_rows() -> None:
    rows = build_trade_history_rows("lead", TRADE_SAMPLE)
    assert rows[0]["Pair"] == "BTCUSDT"
    assert rows[0]["Executed"] == 0.1


BALANCE_SAMPLE = [
    {
        "coin": "USDT",
        "time": "1709990002000",
        "amount": "100",
        "source": "trade",
        "target": "copy",
    }
]


def test_build_balance_history_rows() -> None:
    rows = build_balance_history_rows("lead", BALANCE_SAMPLE)
    assert rows[0]["Coin"] == "USDT"
    assert rows[0]["Amount"] == 100.0
    assert rows[0]["From"] == "trade"


COPY_TRADER_SAMPLE = [
    {
        "userId": "user-1",
        "amount": "500",
        "totalPnl": "20",
        "totalRoi": "5.2",
        "duration": "30D",
    }
]


def test_build_copy_trader_rows() -> None:
    rows = build_copy_trader_rows("lead", COPY_TRADER_SAMPLE)
    assert rows[0]["User_ID"] == "user-1"
    assert rows[0]["Total_ROI"] == 5.2
