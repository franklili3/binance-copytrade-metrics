from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import parse_qs, urlparse

import scrapy
from parsel import Selector
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from scrapy.exceptions import CloseSpider
from scrapy_playwright.page import PageMethod

from money2x_spider.items import (
    CopyTradeFollowerItem,
    CopyTradeOverviewItem,
    CopyTradePerformanceItem,
)

DEFAULT_LEAD_URL = (
    "https://www.binance.com/zh-CN/copy-trading/lead-details/4458914342020236800?timeRange=180D"
)

TIME_RANGE_TO_DAYS: Dict[str, int] = {
    "7D": 7,
    "30D": 30,
    "90D": 90,
    "180D": 180,
    "365D": 365,
}

APP_DATA_SELECTORS: Sequence[str] = (
    "script#__APP_DATA::text",
    "script#__APP_STATE::text",
    "script[id='__APP_DATA']::text",
    "script[type='application/json']::text",
)

JSON_FALLBACK_PATTERN = re.compile(r"__APP_DATA__\s*=\s*(\{.*?\})\s*;\s*</script>", re.S)

COPY_TRADER_TAB_XPATHS: Sequence[str] = (
    "//button[normalize-space()='Copy Traders']",
    "//div[@role='tab' and normalize-space()='Copy Traders']",
    "//div[contains(@class,'tab')][.//text()[normalize-space()='Copy Traders']]",
    "//span[@role='tab' and normalize-space()='Copy Traders']",
    "//*[self::button or self::div or self::span][contains(normalize-space(), 'Copy Traders') and @role='tab']",
)

NEXT_BUTTON_XPATHS: Sequence[str] = (
    "//button[normalize-space()='Next' and not(@disabled)]",
    "//button[contains(., '下一页') and not(@disabled)]",
    "//button[contains(., 'Load more') and not(@disabled)]",
    "//a[@rel='next' and not(contains(@aria-disabled,'true'))]",
    "//li[contains(@class,'next')]//button[not(@disabled)]",
    "//li[contains(@class,'next')]//a[not(contains(@aria-disabled,'true'))]",
)

USDT_PATTERN = re.compile(r"([+\-]?\d[\d,]*(?:\.\d+)?)\s*USDT", re.I)
PERCENT_PATTERN = re.compile(r"([+\-]?\d[\d,]*(?:\.\d+)?)\s*%")
DURATION_PATTERN = re.compile(r"(\d+)\s*D", re.I)
INTEGER_PATTERN = re.compile(r"(\d+)")
MAX_PAGES = 12


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

    def __init__(self, lead_url: Optional[str] = None, **kwargs: Any) -> None:
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

            html = await page.content()
            app_data = self._extract_app_data_from_html(html)
            if app_data:
                overview_item = self._build_overview_item(app_data)
                if overview_item:
                    self._validate_overview(overview_item)
                    yield overview_item
                for perf_item in self._build_performance_items(app_data):
                    self._validate_performance(perf_item)
                    yield perf_item
            else:
                self.logger.warning("Unable to locate Binance app data in rendered HTML")

            await self._open_copy_trader_tab(page)

            seen_ids: set[str] = set()
            last_html = ""
            for _ in range(MAX_PAGES):
                page_html = await page.content()
                if page_html == last_html:
                    break
                last_html = page_html
                for record in self._extract_copy_traders_from_html(page_html):
                    if record["user_id"] in seen_ids:
                        continue
                    seen_ids.add(record["user_id"])
                    item = self._build_follower_item(record)
                    if item is not None:
                        yield item

                if not await self._click_next(page):
                    break
                await page.wait_for_timeout(900)

            if not seen_ids:
                raise CloseSpider("No copy traders parsed from DOM")
        finally:
            try:
                await page.close()
            except PlaywrightError:
                pass

    async def _open_copy_trader_tab(self, page) -> None:
        for xpath in COPY_TRADER_TAB_XPATHS:
            locator = page.locator(f"xpath={xpath}")
            try:
                if await locator.count() == 0:
                    continue
                handle = locator.first
                if not await handle.is_visible():
                    continue
                aria_selected = await handle.get_attribute("aria-selected")
                if aria_selected == "true":
                    return
                try:
                    await handle.click()
                    await page.wait_for_timeout(600)
                    return
                except PlaywrightError as exc:
                    self.logger.debug("Failed to click copy trader tab via %s: %s", xpath, exc)
                    continue
            except PlaywrightError:
                continue

    async def _click_next(self, page) -> bool:
        for xpath in NEXT_BUTTON_XPATHS:
            locator = page.locator(f"xpath={xpath}")
            try:
                if await locator.count() == 0:
                    continue
                handle = locator.first
                if not await handle.is_visible():
                    continue
                disabled = await handle.get_attribute("disabled")
                if disabled is not None:
                    continue
                aria_disabled = await handle.get_attribute("aria-disabled")
                if aria_disabled and aria_disabled.lower() == "true":
                    continue
                try:
                    await handle.click()
                    return True
                except PlaywrightError as exc:
                    self.logger.debug("Failed to click next button via %s: %s", xpath, exc)
                    continue
            except PlaywrightError:
                continue
        return False

    def _extract_copy_traders_from_html(self, html: str) -> List[Dict[str, Any]]:
        selector = Selector(text=html)
        records: List[Dict[str, Any]] = []
        row_nodes = selector.xpath(
            "//table//tbody/tr"
            " | //table//tr[td]"
            " | //*[@role='rowgroup']/*[@role='row']"
            " | //*[@role='row' and not(ancestor::*[@aria-hidden='true'])]"
            " | //div[contains(@class,'table-row') or contains(@class,'bn-table-row')][.//div]"
        )
        for node in row_nodes:
            payload = self._parse_row(node)
            if payload is not None:
                records.append(payload)
        return records

    def _parse_row(self, node: Selector) -> Optional[Dict[str, Any]]:
        text_content = " ".join(node.xpath(".//text()").getall()).strip()
        if not text_content or len(text_content) < 6:
            return None
        if any(
            header in text_content
            for header in ("User ID", "Amount", "Total ROI", "Duration", "Total PNL")
        ) and not USDT_PATTERN.search(text_content):
            return None

        user_id = (
            node.xpath("normalize-space(.//td[1])").get()
            or node.xpath("normalize-space(.//*[@role='cell'][1])").get()
            or node.xpath("normalize-space(.//a[contains(@href,'lead-details')])").get()
        )
        if not user_id:
            return None

        amount_text = (
            node.xpath("string(.//td[2])").get()
            or node.xpath("string(.//*[@role='cell'][2])").get()
            or ""
        )
        pnl_text = (
            node.xpath("string(.//td[3])").get()
            or node.xpath("string(.//*[@role='cell'][3])").get()
            or ""
        )
        roi_text = (
            node.xpath("string(.//td[4])").get()
            or node.xpath("string(.//*[@role='cell'][4])").get()
            or ""
        )
        duration_text = (
            node.xpath("string(.//td[5])").get()
            or node.xpath("string(.//*[@role='cell'][5])").get()
            or ""
        )

        amount = self._parse_usdt(amount_text) or self._parse_usdt(text_content)
        total_pnl = self._parse_usdt(pnl_text) or self._parse_usdt(text_content)
        total_roi = self._parse_percent(roi_text) or self._parse_percent(text_content)
        duration = self._parse_duration(duration_text) or self._parse_duration(text_content)

        if None in (amount, total_pnl, total_roi, duration):
            return None
        if any(value == 0 for value in (amount, total_pnl, total_roi, duration)):
            return None

        return {
            "lead_trader_id": self.lead_trader_id,
            "user_id": str(user_id),
            "amount": amount,
            "total_pnl": total_pnl,
            "total_roi": total_roi,
            "duration": int(duration),
            "created_date": self.scraped_date,
        }

    def _parse_usdt(self, value: str) -> Optional[float]:
        if not value:
            return None
        match = USDT_PATTERN.search(value)
        if match:
            return float(match.group(1).replace(",", ""))
        cleaned = value.strip().replace(",", "")
        if cleaned and cleaned.replace(".", "", 1).replace("-", "", 1).isdigit():
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def _parse_percent(self, value: str) -> Optional[float]:
        if not value:
            return None
        match = PERCENT_PATTERN.search(value)
        if match:
            return float(match.group(1).replace(",", ""))
        return None

    def _parse_duration(self, value: str) -> Optional[int]:
        if not value:
            return None
        match = DURATION_PATTERN.search(value)
        if match:
            return int(match.group(1))
        match = INTEGER_PATTERN.search(value)
        if match:
            return int(match.group(1))
        return None

    def _extract_app_data_from_html(self, html: str) -> Optional[Dict[str, Any]]:
        selector = Selector(text=html)
        for script_selector in APP_DATA_SELECTORS:
            for script in selector.css(script_selector).getall():
                data = (script or "").strip()
                if not data:
                    continue
                try:
                    parsed = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if isinstance(parsed, dict):
                    return parsed
        match = JSON_FALLBACK_PATTERN.search(html)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
        return None

    def _build_overview_item(self, app_data: Dict[str, Any]) -> Optional[CopyTradeOverviewItem]:
        copiers = self._parse_int(
            self._find_first(
                app_data,
                ["totalCopyTraders", "copyTraderCount", "copyCount", "followers"],
            )
        )
        aum = self._parse_number(
            self._find_first(
                app_data, ["aum", "aumInUsdt", "aumValue", "aumUsd"]
            )
        )
        balance = self._parse_number(
            self._find_first(
                app_data,
                ["leadingBalance", "leadBalance", "spotBalance", "balance"],
            )
        )
        mock = self._parse_int(
            self._find_first(
                app_data, ["mockCopyTraders", "mockCopiers", "mockCopyCount"]
            )
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

    def _build_performance_items(
        self, app_data: Dict[str, Any]
    ) -> Iterable[CopyTradePerformanceItem]:
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
                self._pick(candidate, ["roi", "roiValue", "roiPercentage", "ROI"])
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
            ["copyTraderId", "copyUid", "copyId", "uid", "userId", "user_id"],
        )
        amount = self._parse_number(
            self._pick(record, ["copyAmount", "amount", "investment", "followAmount"])
        )
        total_pnl = self._parse_number(
            self._pick(record, ["totalPnl", "copyTotalPnl", "pnl", "copyPnl", "total_pnl"])
        )
        total_roi = self._parse_number(
            self._pick(record, ["totalRoi", "copyTotalRoi", "roi", "copyRoi", "total_roi"])
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
        item["created_date"] = record.get("created_date", self.scraped_date)
        return item

    def _validate_overview(self, item: CopyTradeOverviewItem) -> None:
        for field in ("copiers", "aum_usdt", "leading_balance_usdt"):
            value = item.get(field)
            if value in (None, 0):
                raise CloseSpider(f"Overview field {field} is empty")

    def _validate_performance(self, item: CopyTradePerformanceItem) -> None:
        for field in ("roi", "pnl_usdt"):
            value = item.get(field)
            if value in (None, 0):
                raise CloseSpider(f"Performance field {field} is empty")

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
