from __future__ import annotations

import json
import numbers
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from scrapy.exceptions import DropItem


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
