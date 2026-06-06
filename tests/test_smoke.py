"""Smoke tests for LeWM-MCP."""

from __future__ import annotations

import os

import pytest
from httpx import ASGITransport, AsyncClient

from lewm_mcp.config import get_config
from lewm_mcp.engine.runner import UpstreamRunner
from lewm_mcp.server import app, mcp

UPSTREAM = r"D:\Dev\repos\external\le-wm"


@pytest.fixture(autouse=True)
def dry_run_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LEWM_DRY_RUN", "1")
    if os.path.isdir(UPSTREAM):
        monkeypatch.setenv("LEWM_UPSTREAM_ROOT", UPSTREAM)


def test_upstream_runner_health():
    h = UpstreamRunner.default().health()
    assert h["arxiv"] == "2603.19312"
    assert "upstream_configured" in h


def test_auto_discover_upstream_when_cloned():
    if not os.path.isdir(UPSTREAM):
        pytest.skip("upstream not cloned")
    cfg = get_config()
    assert cfg.upstream_root is not None
    assert "le-wm" in cfg.upstream_root.replace("\\", "/")


def test_mcp_instance():
    assert mcp.name == "lewm-mcp"
    assert mcp.version == "0.2.1"


@pytest.mark.asyncio
async def test_mcp_tools_registered():
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    for expected in ("lewm_world", "lewm_status", "lewm_agentic_workflow"):
        assert expected in names, f"Missing tool: {expected}"


@pytest.mark.asyncio
async def test_lewm_world_health():
    result = await mcp.call_tool("lewm_world", {"operation": "health"})
    assert result is not None


@pytest.mark.asyncio
async def test_lewm_world_train_run_dry():
    if not os.path.isdir(UPSTREAM):
        pytest.skip("upstream not cloned")
    py = os.path.join(UPSTREAM, ".venv", "Scripts", "python.exe")
    if not os.path.isfile(py):
        pytest.skip("upstream venv not bootstrapped")
    result = await mcp.call_tool("lewm_world", {"operation": "train_run", "data_env": "pusht"})
    text = str(result)
    assert "train.py" in text or "dry_run" in text


@pytest.mark.asyncio
async def test_lewm_world_unknown_op():
    result = await mcp.call_tool("lewm_world", {"operation": "bogus"})
    assert result is not None


@pytest.mark.asyncio
async def test_api_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        resp = await c.get("/api/health")
        assert resp.status_code == 200
        assert resp.json().get("ok") is True


@pytest.mark.asyncio
async def test_api_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        resp = await c.get("/api/status")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("mcp_name") == "lewm-mcp"


@pytest.mark.asyncio
async def test_api_checkpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        resp = await c.get("/api/checkpoints")
        assert resp.status_code == 200
