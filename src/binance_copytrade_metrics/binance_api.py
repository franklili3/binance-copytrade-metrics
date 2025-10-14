"""HTTP client for Binance copy trading endpoints."""

from __future__ import annotations

from typing import Any, Iterator, List, Mapping, Optional
from urllib.parse import urljoin

from .brightdata_client import BrightDataProxySession


class BinanceAPIError(RuntimeError):
    """Raised when Binance returns an unexpected payload."""


class BinanceCopyTradeClient:
    """High level helper for Binance copy trading endpoints."""

    BASE_URL = "https://www.binance.com"

    LEADER_INFO_PATH = "/bapi/copy-trade/lead/v1/public/lead/leaderPortfolioInfo"
    OVERVIEW_PATH = "/bapi/copy-trade/lead/v1/public/lead/overview"
    PERFORMANCE_PATH = "/bapi/copy-trade/lead/v1/public/lead/spotLeadPortfolioPerformance"
    HOLDINGS_PATH = "/bapi/copy-trade/lead/v1/public/lead/holdings"
    TRADE_HISTORY_PATH = "/bapi/copy-trade/lead/v1/public/lead/tradeHistory"
    BALANCE_HISTORY_PATH = "/bapi/copy-trade/lead/v1/public/lead/balanceHistory"
    COPY_TRADERS_PATH = "/bapi/copy-trade/lead/v1/public/lead/copyTraders"

    def __init__(self, proxy_session: BrightDataProxySession) -> None:
        self._session = proxy_session

    def _get(self, path: str, params: Optional[Mapping[str, Any]] = None) -> Any:
        url = urljoin(self.BASE_URL, path)
        payload = self._session.get_json(url, params=params)
        if isinstance(payload, Mapping) and payload.get("code") not in (None, "000000"):
            raise BinanceAPIError(str(payload))
        if isinstance(payload, Mapping) and "data" in payload:
            return payload["data"]
        return payload

    def get_leader_portfolio_info(self, lead_portfolio_id: str) -> Mapping[str, Any]:
        return self._get(self.LEADER_INFO_PATH, params={"portfolioId": lead_portfolio_id})

    def get_overview(self, lead_portfolio_id: str) -> Mapping[str, Any]:
        return self._get(self.OVERVIEW_PATH, params={"leadPortfolioId": lead_portfolio_id})

    def get_performance(self, lead_portfolio_id: str, time_range: str) -> Mapping[str, Any]:
        params = {"portfolioId": lead_portfolio_id, "timeRange": time_range}
        return self._get(self.PERFORMANCE_PATH, params=params)

    def get_holdings(self, lead_portfolio_id: str) -> List[Mapping[str, Any]]:
        params = {"leadPortfolioId": lead_portfolio_id}
        return list(self._paginate(self.HOLDINGS_PATH, params=params))

    def get_trade_history(self, lead_portfolio_id: str) -> List[Mapping[str, Any]]:
        params = {"leadPortfolioId": lead_portfolio_id}
        return list(self._paginate(self.TRADE_HISTORY_PATH, params=params))

    def get_balance_history(self, lead_portfolio_id: str) -> List[Mapping[str, Any]]:
        params = {"leadPortfolioId": lead_portfolio_id}
        return list(self._paginate(self.BALANCE_HISTORY_PATH, params=params))

    def get_copy_traders(self, lead_portfolio_id: str) -> List[Mapping[str, Any]]:
        params = {"leadPortfolioId": lead_portfolio_id}
        return list(self._paginate(self.COPY_TRADERS_PATH, params=params))

    def _paginate(
        self,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        page_param: str = "page",
        size_param: str = "pageSize",
        page_size: int = 50,
    ) -> Iterator[Mapping[str, Any]]:
        page = 1
        params = dict(params or {})
        while True:
            params[page_param] = page
            params[size_param] = page_size
            payload = self._get(path, params=params)
            records = _extract_records(payload)
            if not records:
                break
            yield from records
            if len(records) < page_size:
                break
            page += 1


def _extract_records(payload: Any) -> List[Mapping[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, Mapping)]
    if isinstance(payload, Mapping):
        for key in ("rows", "list", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, Mapping)]
        if payload:
            return [payload]
    return []


__all__ = [
    "BinanceCopyTradeClient",
    "BinanceAPIError",
]
