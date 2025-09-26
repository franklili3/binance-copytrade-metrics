from __future__ import annotations

import json
import numbers
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from scrapy.exceptions import DropItem
from supabase import Client, create_client

from money2x_spider.items import (
    CopyTradeFollowerItem,
    CopyTradeOverviewItem,
    CopyTradePerformanceItem,
)


class ValidationPipeline:
    """Validate and persist crawl results locally for manual inspection."""

    OUTPUT_PATH = Path("output/copy_traders.json")

    def open_spider(self, spider):
        self.items: list[Dict[str, Any]] = []
        self.OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    def process_item(self, item, spider):
        record = dict(item)
        for field, value in record.items():
            if value in (None, "", [], {}, ()):  # reject empty data early
                raise DropItem(f"Field '{field}' is empty")
            if isinstance(value, numbers.Number) and value == 0:
                raise DropItem(f"Field '{field}' is zero")
        self.items.append(record)
        return item

    def close_spider(self, spider):
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {"generated_at": timestamp, "items": self.items}
        self.OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


class SupabasePipeline:
    """Persist validated items into the configured Supabase tables."""

    def __init__(self) -> None:
        self.client: Client | None = None
        self.overview_table: str = "binance_spot_copy_trade_overview"
        self.performance_table: str = "binance_spot_copy_trade"
        self.follower_table: str = "binance_spot_copy_traders"

    def open_spider(self, spider):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            spider.logger.warning(
                "Supabase credentials not provided; SupabasePipeline is disabled"
            )
            self.client = None
            return

        self.client = create_client(url, key)
        self.overview_table = os.environ.get(
            "SUPABASE_TABLE_OVERVIEW", self.overview_table
        )
        self.performance_table = os.environ.get(
            "SUPABASE_TABLE_PERFORMANCE", self.performance_table
        )
        self.follower_table = os.environ.get(
            "SUPABASE_TABLE_FOLLOWERS", self.follower_table
        )

    def process_item(self, item, spider):
        if self.client is None:
            return item

        if isinstance(item, CopyTradeOverviewItem):
            payload = self._prepare_overview_payload(dict(item))
            self._upsert(self.overview_table, payload)
        elif isinstance(item, CopyTradePerformanceItem):
            payload = self._prepare_performance_payload(dict(item))
            self._upsert(self.performance_table, payload)
        elif isinstance(item, CopyTradeFollowerItem):
            payload = self._prepare_follower_payload(dict(item))
            self._upsert(self.follower_table, payload)
        else:
            spider.logger.debug("SupabasePipeline received unsupported item: %r", item)
        return item

    def _prepare_overview_payload(self, record: Dict[str, Any]) -> Dict[str, Any]:
        allowed = {
            "lead_trader_id",
            "scraped_date",
            "scraped_at",
            "copiers",
            "aum_usdt",
            "leading_balance_usdt",
            "mock_copiers",
        }
        data = {key: record[key] for key in allowed if key in record}
        rename_map = {
            "aum_usdt": "AUM_usdt",
            "leading_balance_usdt": "Leading_Balance_usdt",
        }
        return self._rename_keys(data, rename_map)

    def _prepare_performance_payload(self, record: Dict[str, Any]) -> Dict[str, Any]:
        allowed = {
            "lead_trader_id",
            "scraped_date",
            "scraped_at",
            "performance_days",
            "roi",
            "pnl_usdt",
            "copier_pnl_usdt",
            "sharpe_ratio",
            "mdd",
            "win_rate",
            "win_days",
        }
        data = {key: record[key] for key in allowed if key in record}
        rename_map = {
            "roi": "ROI",
            "pnl_usdt": "PnL_usdt",
            "copier_pnl_usdt": "Copier_PnL_usdt",
            "sharpe_ratio": "Sharpe_Ratio",
        }
        return self._rename_keys(data, rename_map)

    def _prepare_follower_payload(self, record: Dict[str, Any]) -> Dict[str, Any]:
        allowed = {"duration", "user_id", "amount", "total_pnl", "total_roi", "created_date"}
        data = {key: record[key] for key in allowed if key in record}
        return data

    def _rename_keys(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        for source, target in mapping.items():
            if source in data:
                data[target] = data.pop(source)
        return data

    def _upsert(self, table: str, payload: Dict[str, Any]):
        if not payload:
            raise DropItem(f"Supabase payload for table {table} is empty")
        assert self.client is not None
        self.client.table(table).upsert(payload).execute()
