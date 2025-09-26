from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Iterable, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import scrapy
from scrapy_playwright.page import PageMethod

from money2x_spider.items import CopyTraderSnapshotItem

DEFAULT_LEAD_URL = (
    "https://www.binance.com/zh-CN/copy-trading/lead-details/4458914342020236800?timeRange=180D"
)

TIME_RANGE_TO_DAYS = {
    "7D": 7,
    "30D": 30,
    "90D": 90,
    "180D": 180,
    "365D": 365,
}

APP_DATA_SELECTORS = [
    "script#__APP_DATA::text",
    "script#__APP_STATE::text",
    "script[id='__APP_DATA']::text",
    "script[type='application/json']::text",
]

JSON_FALLBACK_PATTERN = re.compile(r"__APP_DATA__\s*=\s*(\{.*?\})\s*;\s*</script>", re.S)


class CopyTradeSpider(scrapy.Spider):
    name = "copy_trade"

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.binance.com/",
        }
    }

    def __init__(self, lead_url: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.lead_url = lead_url or DEFAULT_LEAD_URL
        self.lead_trader_id, self.time_range, self.performance_days = self._parse_lead_url(
            self.lead_url
        )
        self.scraped_at = datetime.now(timezone.utc)

    def start_requests(self):
        yield scrapy.Request(
            url=self.lead_url,
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod(
                        "add_init_script",
                        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
                    ),
                    PageMethod(
                        "add_init_script",
                        "window.chrome = { runtime: {} };",
                    ),
                    PageMethod(
                        "add_init_script",
                        "Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh']});",
                    ),
                    PageMethod(
                        "add_init_script",
                        "Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});",
                    ),
                    PageMethod(
                        "add_init_script",
                        "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});",
                    ),
                    PageMethod("wait_for_load_state", "networkidle", timeout=45000),
                    PageMethod("wait_for_timeout", 500),
                ],
            },
            dont_filter=True,
        )

    def _parse_lead_url(self, url: str) -> Tuple[int, str, int]:
        parsed = urlparse(url)
        segments = [segment for segment in parsed.path.split("/") if segment]
        lead_trader_id: Optional[int] = None
        for segment in reversed(segments):
            if segment.isdigit():
                lead_trader_id = int(segment)
                break
        if lead_trader_id is None:
            raise ValueError("Unable to determine lead trader id from URL")

        query = parse_qs(parsed.query)
        time_range = query.get("timeRange", ["180D"])[0]
        performance_days = TIME_RANGE_TO_DAYS.get(time_range.upper())
        if performance_days is None:
            if time_range.upper().endswith("D") and time_range[:-1].isdigit():
                performance_days = int(time_range[:-1])
            else:
                raise ValueError(f"Unsupported time range value: {time_range}")
        return lead_trader_id, time_range.upper(), performance_days

    def parse(self, response, **_kwargs):
        records = self._extract_records(response)

        if not records:
            raise scrapy.exceptions.CloseSpider("No copy traders discovered in page data")

        for record in records:
            item = self._build_item(record)
            if item is not None:
                yield item

    def _extract_records(self, response) -> list[dict]:
        html = response.text
        data = self._extract_app_data(response)
        if data is None:
            match = JSON_FALLBACK_PATTERN.search(html)
            if match:
                raw = match.group(1)
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    data = None

        if data is None:
            self.logger.error("Unable to locate Binance app data in rendered HTML")
            return []

        records: list[dict] = []
        for candidate in self._iter_candidates(data):
            if isinstance(candidate, dict):
                maybe_list = self._normalise_list_container(candidate)
                if maybe_list:
                    records.extend(maybe_list)
            elif isinstance(candidate, list):
                records.extend(candidate)

        unique_records: dict[str, dict] = {}
        for record in records:
            identifier = str(
                record.get("copyTraderId")
                or record.get("copyUid")
                or record.get("copyId")
                or record.get("uid")
                or record.get("userId")
            )
            if identifier and identifier not in unique_records and self._looks_like_record(record):
                unique_records[identifier] = record
        return list(unique_records.values())

    def _extract_app_data(self, response) -> Optional[dict]:
        for selector in APP_DATA_SELECTORS:
            for script in response.css(selector).getall():
                script = script.strip()
                if not script:
                    continue
                try:
                    data = json.loads(script)
                except json.JSONDecodeError:
                    continue
                if isinstance(data, dict):
                    return data
        return None

    def _iter_candidates(self, data: object) -> Iterable[object]:
        stack = [data]
        seen = set()
        while stack:
            current = stack.pop()
            obj_id = id(current)
            if obj_id in seen:
                continue
            seen.add(obj_id)
            if isinstance(current, dict):
                for value in current.values():
                    stack.append(value)
                yield current
            elif isinstance(current, list):
                for value in current:
                    stack.append(value)
                yield current

    def _normalise_list_container(self, value: dict) -> list[dict]:
        if "copyTraderList" in value and isinstance(value["copyTraderList"], list):
            return [item for item in value["copyTraderList"] if isinstance(item, dict)]
        if "list" in value and isinstance(value["list"], list):
            return [item for item in value["list"] if isinstance(item, dict)]
        if "rows" in value and isinstance(value["rows"], list):
            return [item for item in value["rows"] if isinstance(item, dict)]
        if "items" in value and isinstance(value["items"], list):
            return [item for item in value["items"] if isinstance(item, dict)]
        return []

    def _looks_like_record(self, record: dict) -> bool:
        if not isinstance(record, dict):
            return False
        indicators = 0
        for key in (
            "copyTraderId",
            "copyUid",
            "nickname",
            "roi",
            "pnl",
            "copyAmount",
            "copyCount",
            "followTime",
        ):
            if key in record:
                indicators += 1
        return indicators >= 3

    def _parse_number(self, value: Optional[object]) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.strip().replace(",", "")
            if cleaned.endswith("%"):
                cleaned = cleaned[:-1]
            if not cleaned:
                return None
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def _parse_int(self, value: Optional[object]) -> Optional[int]:
        number = self._parse_number(value)
        if number is None:
            return None
        return int(number)

    def _parse_timestamp(self, value: Optional[object]) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            timestamp = int(value)
            if timestamp > 10**12:
                timestamp /= 1000.0
            return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned.isdigit():
                return self._parse_timestamp(int(cleaned))
            try:
                datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
                return cleaned
            except ValueError:
                return None
        return None

    def _build_item(self, record: dict) -> Optional[CopyTraderSnapshotItem]:
        copy_trader_id = (
            record.get("copyTraderId")
            or record.get("copyUid")
            or record.get("copyId")
            or record.get("uid")
            or record.get("userId")
        )
        nickname = record.get("nickname") or record.get("nickName") or record.get("name")
        roi = self._parse_number(
            record.get("roi")
            or record.get("roiValue")
            or record.get("copyRoi")
            or record.get("roiPercentage")
        )
        pnl = self._parse_number(
            record.get("pnl") or record.get("pnlValue") or record.get("copyPnl")
        )
        investment = self._parse_number(
            record.get("copyAmount") or record.get("investment") or record.get("amount")
        )
        copy_count = self._parse_int(
            record.get("copyCount") or record.get("count") or record.get("copiers")
        )
        copied_at = self._parse_timestamp(
            record.get("followTime")
            or record.get("updateTime")
            or record.get("createTime")
            or record.get("timestamp")
        )

        if not all([copy_trader_id, nickname, roi, pnl, investment, copy_count, copied_at]):
            self.logger.debug("Skipping record with missing data: %s", record)
            return None

        item = CopyTraderSnapshotItem()
        item["lead_trader_id"] = self.lead_trader_id
        item["performance_days"] = self.performance_days
        item["time_range"] = self.time_range
        item["copy_trader_id"] = str(copy_trader_id)
        item["copy_trader_nickname"] = nickname
        item["roi"] = roi
        item["pnl_usdt"] = pnl
        item["investment_usdt"] = investment
        item["copy_count"] = copy_count
        item["copied_at"] = copied_at
        item["scraped_at"] = self.scraped_at.isoformat()
        return item
