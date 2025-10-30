from __future__ import annotations

from pathlib import Path

from binance_copytrade_metrics.storage import SQLiteStorage


def test_storage_upsert_and_replace(tmp_path: Path) -> None:
    db_path = tmp_path / "metrics.db"
    storage = SQLiteStorage(db_path)

    try:
        storage.upsert_overview(
            {
                "leadPortfolioId": "lead",
                "favoriteCount": 1,
                "currentCopyCount": 2,
                "maxCopyCount": 3,
                "totalCopyCount": 4,
                "walletBalanceAmount": 10.5,
                "walletBalanceAsset": "USDT",
                "currentInvestAmount": 5.0,
                "currentAvailableAmount": 5.5,
                "aumAmount": 100.0,
                "aumAsset": "USDT",
                "badgeName": "Badge",
                "badgeCopierCount": 6,
                "tagName": "Tag",
                "tag_days": "90",
                "tag_ranking": "1",
                "tag_sort": "1",
                "copyMockCount": 7,
                "dataUpdatedAt": "1000",
                "datetime": "2024-01-01T00:00:00+00:00",
            }
        )

        storage.upsert_performance(
            [
                {
                    "leadPortfolioId": "lead",
                    "timeRange": "180D",
                    "roi": 1.2,
                    "pnl": 3.4,
                    "mdd": 0.5,
                    "copierPnl": 0.6,
                    "winRate": 90.0,
                    "winDays": 100,
                    "sharpRatio": 1.1,
                    "dataUpdatedAt": "1010",
                    "datetime": "2024-01-01T00:00:00+00:00",
                }
            ]
        )

        storage.replace_holdings(
            "lead",
            [
                {
                    "leadPortfolioId": "lead",
                    "Assets": "BTC",
                    "Time_Updated": "1001",
                    "Remain_Amount": 0.1,
                    "Buy_Amount": 0.2,
                    "Avg_Buy_Price": 20000.0,
                    "Last_Price": 21000.0,
                    "Unrealized_PNL": 100.0,
                    "Realized_PNL": 50.0,
                }
            ],
        )

        storage.replace_trade_history(
            "lead",
            [
                {
                    "leadPortfolioId": "lead",
                    "Time": "1002",
                    "Pair": "BTCUSDT",
                    "Side": "BUY",
                    "Executed": 0.1,
                    "Role": "TAKER",
                    "Total": 2100.0,
                }
            ],
        )

        storage.replace_balances(
            "lead",
            [
                {
                    "leadPortfolioId": "lead",
                    "Coin": "USDT",
                    "Time": "1003",
                    "Amount": 100.0,
                    "From": "trade",
                    "To": "wallet",
                }
            ],
        )

        storage.replace_copy_traders(
            "lead",
            [
                {
                    "leadPortfolioId": "lead",
                    "User_ID": "user-1",
                    "Amount": 1000.0,
                    "Total_PNL": 50.0,
                    "Total_ROI": 5.0,
                    "Duration": "30D",
                }
            ],
        )

        cur = storage.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM binance_copy_trade_overview")
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT COUNT(*) FROM binance_copy_trade_performance")
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT COUNT(*) FROM binance_copy_trade_holdings")
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT COUNT(*) FROM binance_copy_trade_history")
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT COUNT(*) FROM binance_copy_trade_balances_history")
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT COUNT(*) FROM binance_copy_traders")
        assert cur.fetchone()[0] == 1
    finally:
        storage.close()
