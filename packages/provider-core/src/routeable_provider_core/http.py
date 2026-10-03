"""Thin httpx wrapper with the limits every outbound call must respect."""

import ssl
from typing import Any

import httpx
import truststore

DEFAULT_TIMEOUT_S = 5.0
DEFAULT_MAX_BYTES = 2 * 1024 * 1024


def system_ssl_context() -> ssl.SSLContext:
    """Trust the OS certificate store so corporate TLS interception works."""
    return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)


class ProviderHttpError(RuntimeError):
    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class HttpClient:
    """Shared client: timeouts, a descriptive user agent and a hard body-size cap."""

    def __init__(
        self,
        user_agent: str = "RouteAble/0.1",
        timeout_s: float = DEFAULT_TIMEOUT_S,
        max_bytes: int = DEFAULT_MAX_BYTES,
    ) -> None:
        self._max_bytes = max_bytes
        self._client = httpx.AsyncClient(
            timeout=timeout_s,
            follow_redirects=True,
            verify=system_ssl_context(),
            headers={"User-Agent": user_agent, "Accept-Encoding": "gzip"},
        )

    async def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        response = await self._request("GET", url, params=params)
        return response.json()

    async def post_form_json(self, url: str, data: dict[str, str]) -> Any:
        response = await self._request("POST", url, data=data)
        return response.json()

    async def get_text(self, url: str) -> str:
        async with self._client.stream("GET", url) as response:
            self._raise_for_status(response, url)
            chunks: list[bytes] = []
            size = 0
            async for chunk in response.aiter_bytes():
                remaining = self._max_bytes - size
                if len(chunk) >= remaining:
                    chunks.append(chunk[:remaining])
                    break
                chunks.append(chunk)
                size += len(chunk)
            return b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        try:
            response = await self._client.request(method, url, **kwargs)
        except httpx.HTTPError as error:
            raise ProviderHttpError(f"Request to {url} failed: {error}") from error
        self._raise_for_status(response, url)
        return response

    @staticmethod
    def _raise_for_status(response: httpx.Response, url: str) -> None:
        if response.is_error:
            raise ProviderHttpError(
                f"Request to {url} failed with {response.status_code}", response.status_code
            )
