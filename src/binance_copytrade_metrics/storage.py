"""SQLite storage for Binance copy trading data."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Mapping, Sequence


def _quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


class SQLiteStorage:
    """Persist scraper output into SQLite tables."""

    def __init__(self, path: str | Path) -> None:
        self._path = str(path)
        self._conn = sqlite3.connect(self._path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._ensure_schema()

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn

    def close(self) -> None:
        self._conn.close()

    def _ensure_schema(self) -> None:
        cur = self._conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS binance_copy_trade_overview (
                leadPortfolioId TEXT PRIMARY KEY,
                favoriteCount INTEGER,
                currentCopyCount INTEGER,
                maxCopyCount INTEGER,
                totalCopyCount INTEGER,
                walletBalanceAmount REAL,
                walletBalanceAsset TEXT,
                currentInvestAmount REAL,
                currentAvailableAmount REAL,
                aumAmount REAL,
                aumAsset TEXT,
                badgeName TEXT,
                badgeCopierCount INTEGER,
                tagName TEXT,
                tag_days TEXT,
                tag_ranking TEXT,
                tag_sort TEXT,
                copyMockCount INTEGER,
                dataUpdatedAt TEXT,
                datetime TEXT
            );

            CREATE TABLE IF NOT EXISTS binance_copy_trade_performance (
                leadPortfolioId TEXT,
                timeRange TEXT,
                roi REAL,
                pnl REAL,
                mdd REAL,
                copierPnl REAL,
                winRate REAL,
                winDays INTEGER,
                sharpRatio REAL,
                dataUpdatedAt TEXT,
                datetime TEXT,
                PRIMARY KEY (leadPortfolioId, timeRange)
            );

            CREATE TABLE IF NOT EXISTS binance_copy_trade_holdings (
                leadPortfolioId TEXT,
                Assets TEXT,
                Time_Updated TEXT,
                Remain_Amount REAL,
                Buy_Amount REAL,
                Avg_Buy_Price REAL,
                Last_Price REAL,
                Unrealized_PNL REAL,
                Realized_PNL REAL,
                PRIMARY KEY (leadPortfolioId, Assets)
            );

            CREATE TABLE IF NOT EXISTS binance_copy_trade_history (
                leadPortfolioId TEXT,
                Time TEXT,
                Pair TEXT,
                Side TEXT,
                Executed REAL,
                Role TEXT,
                Total REAL,
                PRIMARY KEY (leadPortfolioId, Time, Pair, Side, Role)
            );

            CREATE TABLE IF NOT EXISTS binance_copy_trade_balances_history (
                leadPortfolioId TEXT,
                Coin TEXT,
                Time TEXT,
                Amount REAL,
                "From" TEXT,
                "To" TEXT,
                PRIMARY KEY (leadPortfolioId, Coin, Time, "From", "To")
            );

            CREATE TABLE IF NOT EXISTS binance_copy_traders (
                leadPortfolioId TEXT,
                User_ID TEXT,
                Amount REAL,
                Total_PNL REAL,
                Total_ROI REAL,
                Duration TEXT,
                PRIMARY KEY (leadPortfolioId, User_ID)
            );
            """
        )
        self._conn.commit()

    def upsert_overview(self, row: Mapping[str, object]) -> None:
        self._upsert("binance_copy_trade_overview", row)

    def upsert_performance(self, rows: Iterable[Mapping[str, object]]) -> None:
        for row in rows:
            self._upsert("binance_copy_trade_performance", row)

    def replace_holdings(
        self,
        lead_portfolio_id: str,
        rows: Sequence[Mapping[str, object]],
    ) -> None:
        self._replace_for_lead('binance_copy_trade_holdings', lead_portfolio_id, rows)

    def replace_trade_history(
        self,
        lead_portfolio_id: str,
        rows: Sequence[Mapping[str, object]],
    ) -> None:
        self._replace_for_lead('binance_copy_trade_history', lead_portfolio_id, rows)

    def replace_balances(
        self,
        lead_portfolio_id: str,
        rows: Sequence[Mapping[str, object]],
    ) -> None:
        self._replace_for_lead('binance_copy_trade_balances_history', lead_portfolio_id, rows)

    def replace_copy_traders(
        self,
        lead_portfolio_id: str,
        rows: Sequence[Mapping[str, object]],
    ) -> None:
        self._replace_for_lead('binance_copy_traders', lead_portfolio_id, rows)

    def _replace_for_lead(
        self,
        table: str,
        lead_portfolio_id: str,
        rows: Sequence[Mapping[str, object]],
    ) -> None:
        cur = self._conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE leadPortfolioId=?", (lead_portfolio_id,))
        if rows:
            columns = list(rows[0].keys())
            placeholders = ','.join(['?'] * len(columns))
            column_list = ','.join(_quote_identifier(col) for col in columns)
            sql = f"INSERT OR REPLACE INTO {table} ({column_list}) VALUES ({placeholders})"
            values = [tuple(row.get(col) for col in columns) for row in rows]
            cur.executemany(sql, values)
        self._conn.commit()

    def _upsert(self, table: str, row: Mapping[str, object]) -> None:
        columns = list(row.keys())
        placeholders = ",".join(["?"] * len(columns))
        column_list = ','.join(_quote_identifier(col) for col in columns)
        sql = f"INSERT OR REPLACE INTO {table} ({column_list}) VALUES ({placeholders})"
        values = [row.get(col) for col in columns]
        self._conn.execute(sql, values)
        self._conn.commit()


__all__ = ["SQLiteStorage"]
