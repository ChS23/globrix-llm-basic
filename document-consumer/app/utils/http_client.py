"""
HTTP client with proxy support for OpenAI.
"""
import os
import httpx


def get_http_client() -> httpx.Client | None:
    """
    Creates httpx client with SOCKS proxy if configured.
    Returns None if no proxy is set.
    """
    proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY") or os.getenv("ALL_PROXY")

    if not proxy_url:
        return None

    return httpx.Client(proxy=proxy_url)


def get_async_http_client() -> httpx.AsyncClient | None:
    """
    Creates async httpx client with SOCKS proxy if configured.
    Returns None if no proxy is set.
    """
    proxy_url = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY") or os.getenv("ALL_PROXY")

    if not proxy_url:
        return None

    return httpx.AsyncClient(proxy=proxy_url)
