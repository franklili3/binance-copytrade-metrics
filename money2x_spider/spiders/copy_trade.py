from __future__ import annotations

import asyncio
import json
import re
from contextlib import suppress
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import scrapy
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from scrapy.exceptions import CloseSpider
from scrapy.selector import Selector
from scrapy_playwright.page import PageMethod

from money2x_spider.items import (
    CopyTradeFollowerItem,
    CopyTradeOverviewItem,
    CopyTradePerformanceItem,
)

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
COPY_TRADER_ENDPOINT_RE = re.compile(r"/bapi/.*/lead-copy-traders/", re.I)
COPY_TRADER_BUTTON_SELECTORS = [
    "button:has-text('复制交易员')",
    "button:has-text('Copy traders')",
    "div[data-bn-type='button']:has-text('复制交易员')",
    "div[data-bn-type='button']:has-text('Copy traders')",
]
NEXT_BUTTON_SELECTORS = [
    "button:has-text('下一页')",
    "button[aria-label='Next']",
    "button:has-text('Next')",
    "a[aria-label='Next']",
]
RESPONSE_TIMEOUT_MS = 60000
MAX_PAGES = 100


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
        (
            self.lead_trader_id,
            self.time_range,
            self.performance_days,
        ) = self._parse_lead_url(self.lead_url)
        self.scraped_at = datetime.now(timezone.utc)
        self.scraped_date = self.scraped_at.date().isoformat()

    def start_requests(self):
        yield scrapy.Request(
            url=self.lead_url,
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_context_kwargs": {
                    "locale": "zh-CN",
                    "user_agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                    ),
                },
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
                    PageMethod("wait_for_load_state", "domcontentloaded", timeout=45000),
                    PageMethod("wait_for_timeout", 300),
                ],
            },
            dont_filter=True,
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        try:
            try:
                await page.wait_for_load_state("networkidle", timeout=45000)
            except PlaywrightTimeoutError:
                self.logger.warning("Timed out waiting for network idle; continuing")

            app_data = await self._extract_app_data(page)
            if app_data:
                overview_item = self._build_overview_item(app_data)
                if overview_item:
                    yield overview_item
                for perf_item in self._build_performance_items(app_data):
                    yield perf_item
            else:
                self.logger.warning("Unable to locate Binance app data in rendered HTML")

            async for follower in self._collect_copy_traders(page):
                yield follower
        finally:
            with suppress(Exception):
                await page.close()

    async def _collect_copy_traders(self, page):
        seen_pages: set[int] = set()
        total_pages: Optional[int] = None
        first_click = True
        pages_processed = 0
        button = await self._query_first(page, COPY_TRADER_BUTTON_SELECTORS)
        if button is None:
            raise CloseSpider("Copy trader button not found")

        while pages_processed < MAX_PAGES:
            wait_task = asyncio.create_task(
                page.wait_for_response(
                    lambda resp: bool(
                        resp is not None
                        and resp.url
                        and COPY_TRADER_ENDPOINT_RE.search(resp.url)
                    ),
                    timeout=RESPONSE_TIMEOUT_MS,
                )
            )

            if first_click:
                await button.click()
                first_click = False
            else:
                clicked = await self._click_next(page)
                if not clicked:
                    wait_task.cancel()
                    with suppress(asyncio.CancelledError):
                        await wait_task
                    break

            response = await self._await_response(wait_task)
            if response is None:
                break

            payload = await self._decode_payload(response)
            if payload is None:
                continue

            records, page_no, page_total = self._extract_copy_trader_records(payload)
            if page_no is not None:
                if page_no in seen_pages:
                    if total_pages and len(seen_pages) >= total_pages:
                        break
                    continue
                seen_pages.add(page_no)

            if page_total is not None:
                total_pages = page_total

            yielded = False
            for record in records:
                item = self._build_follower_item(record)
                if item is not None:
                    yielded = True
                    yield item

            pages_processed += 1

            if total_pages is not None and page_no is not None and page_no >= total_pages:
                break

            if not yielded and total_pages is None:
                self.logger.debug(
                    "Copy trader payload for page %s contained no usable records", page_no
                )

            await page.wait_for_timeout(300)

    async def _await_response(self, wait_task: asyncio.Task):
        try:
            return await wait_task
        except PlaywrightTimeoutError:
            self.logger.error("Timed out waiting for copy trader response")
        except asyncio.CancelledError:
            return None
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.error("Unexpected error waiting for response: %s", exc)
        return None

    async def _decode_payload(self, response):
        try:
            return await response.json()
        except Exception:
            try:
                text = await response.text()
            except Exception:
                return None
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                self.logger.error("Failed to decode copy trader payload from %s", response.url)
                return None

    async def _click_next(self, page) -> bool:
        for selector in NEXT_BUTTON_SELECTORS:
            handles = await page.query_selector_all(selector)
            for handle in handles:
                try:
                    if not await handle.is_enabled():
                        continue
                    await handle.click()
                    await page.wait_for_timeout(200)
                    return True
                except PlaywrightTimeoutError:
                    continue
                except Exception as exc:  # pragma: no cover - defensive
                    self.logger.debug("Failed to click next button %s: %s", selector, exc)
        return False

    async def _query_first(self, page, selectors):
        for selector in selectors:
            handle = await page.query_selector(selector)
            if handle is not None:
                return handle
        return None

    def _extract_copy_trader_records(
        self, payload: Dict[str, Any]
    ) -> Tuple[list[Dict[str, Any]], Optional[int], Optional[int]]:
        records: list[Dict[str, Any]] = []
        page_no = self._extract_page_number(payload)
        total_pages = self._extract_total_pages(payload)

        for candidate in self._iter_objects(payload):
            if isinstance(candidate, dict):
                for key in ("copyTraderList", "list", "rows", "items", "data"):
                    value = candidate.get(key)
                    if isinstance(value, list) and all(isinstance(v, dict) for v in value):
                        records = value
                        if page_no is None:
                            page_no = self._parse_int(
                                candidate.get("page")
                                or candidate.get("pageNo")
                                or candidate.get("pageIndex")
                                or candidate.get("currentPage")
                            )
                        if total_pages is None:
                            total_pages = self._parse_int(
                                candidate.get("totalPage")
                                or candidate.get("pageCount")
                                or candidate.get("pages")
                                or candidate.get("totalPages")
                            )
                        return records, page_no, total_pages

        return records, page_no, total_pages

    def _build_overview_item(self, app_data: Dict[str, Any]) -> Optional[CopyTradeOverviewItem]:
        copiers = self._parse_int(
            self._find_first(app_data, ["totalCopyTraders", "copyTraderCount", "copyCount", "followers"])
        )
        aum = self._parse_number(
            self._find_first(app_data, ["aum", "aumInUsdt", "aumValue", "aumUsd"])
        )
        balance = self._parse_number(
            self._find_first(
                app_data,
                ["leadingBalance", "leadBalance", "spotBalance", "balance"],
            )
        )
        mock = self._parse_int(
            self._find_first(app_data, ["mockCopyTraders", "mockCopiers", "mockCopyCount"])
        )

        if copiers is None or aum is None or balance is None:
            return None

        item = CopyTradeOverviewItem()
        item["lead_trader_id"] = self.lead_trader_id
        item["scraped_date"] = self.scraped_date
        item["scraped_at"] = self.scraped_at.isoformat()
        item["copiers"] = copiers
        item["aum_usdt"] = aum
        item["leading_balance_usdt"] = balance
        if mock is not None:
            item["mock_copiers"] = mock
        return item

    def _build_performance_items(self, app_data: Dict[str, Any]) -> Iterable[CopyTradePerformanceItem]:
        results: Dict[int, Dict[str, Any]] = {}
        for candidate in self._iter_objects(app_data):
            if not isinstance(candidate, dict):
                continue
            days = self._normalise_days(
                candidate.get("performanceDays") or candidate.get("timeRange")
            )
            if days is None:
                continue
            roi = self._parse_number(
                self._pick(candidate, ["roi", "roiValue", "roiPercentage"])
            )
            pnl = self._parse_number(
                self._pick(candidate, ["pnl", "pnlValue", "copyPnl", "profit"])
            )
            copier_pnl = self._parse_number(
                self._pick(candidate, ["copierPnl", "copyerPnl", "followerPnl"])
            )
            sharpe = self._parse_number(
                self._pick(candidate, ["sharpeRatio", "sharpe"])
            )
            mdd = self._pick(candidate, ["mdd", "maxDrawdown"])
            win_rate = self._pick(candidate, ["winRate", "winningRate"])
            win_days = self._parse_int(
                self._pick(candidate, ["winDays", "winningDays"])
            )

            if roi is None or pnl is None:
                continue

            existing = results.get(days, {})
            merged = {
                "roi": roi,
                "pnl_usdt": pnl,
                "copier_pnl_usdt": copier_pnl,
                "sharpe_ratio": sharpe,
                "mdd": mdd,
                "win_rate": win_rate,
                "win_days": win_days,
            }
            if not existing:
                results[days] = merged
            else:
                for key, value in merged.items():
                    if existing.get(key) is None and value is not None:
                        existing[key] = value

        for days, payload in results.items():
            item = CopyTradePerformanceItem()
            item["lead_trader_id"] = self.lead_trader_id
            item["scraped_date"] = self.scraped_date
            item["scraped_at"] = self.scraped_at.isoformat()
            item["performance_days"] = days
            item["roi"] = payload.get("roi")
            item["pnl_usdt"] = payload.get("pnl_usdt")
            if payload.get("copier_pnl_usdt") is not None:
                item["copier_pnl_usdt"] = payload.get("copier_pnl_usdt")
            if payload.get("sharpe_ratio") is not None:
                item["sharpe_ratio"] = payload.get("sharpe_ratio")
            if payload.get("mdd") is not None:
                item["mdd"] = payload.get("mdd")
            if payload.get("win_rate") is not None:
                item["win_rate"] = payload.get("win_rate")
            if payload.get("win_days") is not None:
                item["win_days"] = payload.get("win_days")
            yield item

    def _build_follower_item(self, record: Dict[str, Any]) -> Optional[CopyTradeFollowerItem]:
        user_id = self._pick(
            record,
            ["copyTraderId", "copyUid", "copyId", "uid", "userId"],
        )
        amount = self._parse_number(
            self._pick(record, ["copyAmount", "amount", "investment", "followAmount"])
        )
        total_pnl = self._parse_number(
            self._pick(record, ["totalPnl", "copyTotalPnl", "pnl", "copyPnl"])
        )
        total_roi = self._parse_number(
            self._pick(record, ["totalRoi", "copyTotalRoi", "roi", "copyRoi"])
        )
        duration = self._parse_int(
            self._pick(record, ["duration", "followDuration", "copyDuration"])
        )

        if not user_id or amount is None or total_pnl is None or total_roi is None:
            return None
        if duration is None or duration <= 0:
            return None
        if any(value == 0 for value in (amount, total_pnl, total_roi)):
            return None

        item = CopyTradeFollowerItem()
        item["lead_trader_id"] = self.lead_trader_id
        item["user_id"] = str(user_id)
        item["amount"] = amount
        item["total_pnl"] = total_pnl
        item["total_roi"] = total_roi
        item["duration"] = duration
        item["created_date"] = self.scraped_date
        return item

    async def _extract_app_data(self, page) -> Optional[Dict[str, Any]]:
        html = await page.content()
        selector = Selector(text=html)
        for script_selector in APP_DATA_SELECTORS:
            for script in selector.css(script_selector).getall():
                script = (script or "").strip()
                if not script:
                    continue
                try:
                    data = json.loads(script)
                except json.JSONDecodeError:
                    continue
                if isinstance(data, dict):
                    return data
        match = JSON_FALLBACK_PATTERN.search(html)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    def _iter_objects(self, data: Any) -> Iterable[Any]:
        stack = [data]
        seen: set[int] = set()
        while stack:
            current = stack.pop()
            obj_id = id(current)
            if obj_id in seen:
                continue
            seen.add(obj_id)
            if isinstance(current, dict):
                stack.extend(current.values())
                yield current
            elif isinstance(current, list):
                stack.extend(current)
                yield current

    def _find_first(self, data: Any, keys: Iterable[str]) -> Any:
        for candidate in self._iter_objects(data):
            if isinstance(candidate, dict):
                for key in keys:
                    value = candidate.get(key)
                    if value not in (None, ""):
                        return value
        return None

    def _pick(self, record: Dict[str, Any], keys: Iterable[str]) -> Any:
        for key in keys:
            if key in record and record[key] not in (None, ""):
                return record[key]
        return None

    def _parse_number(self, value: Optional[Any]) -> Optional[float]:
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

    def _parse_int(self, value: Optional[Any]) -> Optional[int]:
        number = self._parse_number(value)
        if number is None:
            return None
        try:
            return int(number)
        except (TypeError, ValueError):
            return None

    def _extract_page_number(self, payload: Dict[str, Any]) -> Optional[int]:
        return self._parse_int(
            self._find_first(payload, ["page", "pageNo", "pageIndex", "currentPage"])
        )

    def _extract_total_pages(self, payload: Dict[str, Any]) -> Optional[int]:
        return self._parse_int(
            self._find_first(payload, ["totalPage", "pageCount", "totalPages", "pages"])
        )

    def _normalise_days(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            cleaned = value.strip().upper()
            if cleaned in TIME_RANGE_TO_DAYS:
                return TIME_RANGE_TO_DAYS[cleaned]
            if cleaned.endswith("D") and cleaned[:-1].isdigit():
                return int(cleaned[:-1])
            if cleaned.isdigit():
                return int(cleaned)
        return None

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
