"""Utilities for interacting with Bright Data's proxy network."""

from __future__ import annotations

import os
import random
import string
from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional

import requests

BRIGHT_DATA_PROXY_HOST = "brd.superproxy.io"
BRIGHT_DATA_PROXY_PORT = 22225


def _random_session_id(length: int = 8) -> str:
    """Generate a short random session identifier."""

    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


class BrightDataCredentialsError(RuntimeError):
    """Raised when Bright Data credentials are missing."""


@dataclass
class BrightDataProxyConfig:
    """Configuration for building Bright Data proxy URLs."""

    zone: str
    api_key: str
    host: str = BRIGHT_DATA_PROXY_HOST
    port: int = BRIGHT_DATA_PROXY_PORT

    def build_proxy_url(self, session_id: Optional[str] = None) -> str:
        """Return the proxy URL with the encoded credentials."""

        session_token = session_id or _random_session_id()
        username = f"{self.zone}-session-{session_token}"
        return f"http://{username}:{self.api_key}@{self.host}:{self.port}"


class BrightDataProxySession:
    """Minimal wrapper around ``requests.Session`` configured for Bright Data."""

    def __init__(
        self,
        *,
        config: Optional[BrightDataProxyConfig] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        zone = os.getenv("BRIGHTDATA_ZONE")
        api_key = os.getenv("BRIGHTDATA_API_KEY")

        if config is None:
            if not zone or not api_key:
                raise BrightDataCredentialsError(
                    "Both BRIGHTDATA_ZONE and BRIGHTDATA_API_KEY environment variables must be set",
                )
            config = BrightDataProxyConfig(zone=zone, api_key=api_key)

        self._config = config
        self._session = session or requests.Session()

    @property
    def session(self) -> requests.Session:
        """Expose the underlying ``requests`` session."""

        return self._session

    def _prepare_kwargs(self, kwargs: MutableMapping[str, Any]) -> None:
        proxies = self._build_proxies(kwargs.pop("session_id", None))
        headers = kwargs.setdefault("headers", {})
        headers.setdefault(
            "User-Agent",
            (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
        )
        kwargs["proxies"] = proxies
        kwargs.setdefault("timeout", 30)

    def _build_proxies(self, session_id: Optional[str]) -> Mapping[str, str]:
        proxy_url = self._config.build_proxy_url(session_id=session_id)
        return {"http": proxy_url, "https": proxy_url}

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """Execute an HTTP request through the Bright Data proxy."""

        self._prepare_kwargs(kwargs)
        response = self._session.request(method=method, url=url, **kwargs)
        response.raise_for_status()
        return response

    def get_json(self, url: str, **kwargs: Any) -> Any:
        """Shortcut for ``GET`` requests that return JSON payloads."""

        response = self.request("GET", url, **kwargs)
        if "application/json" not in response.headers.get("Content-Type", ""):
            raise ValueError(
                "Expected JSON response but received Content-Type: "
                f"{response.headers.get('Content-Type')}"
            )
        return response.json()


__all__ = [
    "BrightDataProxyConfig",
    "BrightDataProxySession",
    "BrightDataCredentialsError",
]
