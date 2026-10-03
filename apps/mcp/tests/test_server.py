from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from mcp.client import Client

import routeable_mcp.__main__ as entry
from routeable_mcp.server import create_server


@pytest.mark.asyncio
async def test_server_exposes_and_calls_tools() -> None:
    search_places = AsyncMock(return_value=SimpleNamespace(model_dump=lambda mode: {"places": []}))
    server = create_server(SimpleNamespace(search_places=search_places))

    async with Client(server) as client:
        tools = await client.list_tools()
        assert {tool.name for tool in tools.tools} == {
            "search_places",
            "get_place_accessibility",
            "get_accessibility_evidence",
            "report_accessibility_issue",
        }

        result = await client.call_tool("search_places", {"query": "museum"})

    assert result.structured_content == {"places": []}
    assert search_places.await_args.args[0] == "museum"


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ["stdio", "http"])
async def test_server_startup_closes_container(
    monkeypatch: pytest.MonkeyPatch, transport: str
) -> None:
    monkeypatch.setenv("MCP_TRANSPORT", transport)
    monkeypatch.setenv("FASTMCP_HOST", "0.0.0.0")
    monkeypatch.setenv("FASTMCP_PORT", "3002")
    container = SimpleNamespace(service=None, aclose=AsyncMock())
    server = SimpleNamespace(run_stdio_async=AsyncMock(), run_streamable_http_async=AsyncMock())

    with (
        patch.object(entry, "build_container", new=AsyncMock(return_value=container)),
        patch.object(entry, "create_server", return_value=server),
    ):
        await entry.serve()

    if transport == "http":
        server.run_streamable_http_async.assert_awaited_once_with(host="0.0.0.0", port=3002)
        server.run_stdio_async.assert_not_awaited()
    else:
        server.run_stdio_async.assert_awaited_once_with()
        server.run_streamable_http_async.assert_not_awaited()
    container.aclose.assert_awaited_once_with()
