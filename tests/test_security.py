"""Tests for the hardening features: tool policy, HTTP auth and CORS."""

import json

import pytest
from starlette.testclient import TestClient

from dolibarr_mcp.config import Config
from dolibarr_mcp import dolibarr_mcp_server as srv


def _cfg(**kw):
    base = dict(dolibarr_url="https://erp.example.com", dolibarr_api_key="k")
    base.update(kw)
    return Config(**base)


def test_write_tool_detection():
    for name in ["create_invoice", "update_customer", "delete_user", "add_invoice_line",
                 "set_invoice_project", "validate_invoice", "create_invoice_draft", "dolibarr_raw_api"]:
        assert srv.is_write_tool(name), name
    for name in ["get_invoices", "search_customers", "resolve_product_ref", "test_connection"]:
        assert not srv.is_write_tool(name), name


def test_raw_api_disabled_by_default():
    names = {t.name for t in srv._all_tools() if srv.is_tool_allowed(t.name, _cfg())}
    assert "dolibarr_raw_api" not in names
    assert "create_invoice" in names


def test_read_only_hides_all_write_tools():
    cfg = _cfg(mcp_read_only=True, mcp_enable_raw_api=True)
    names = {t.name for t in srv._all_tools() if srv.is_tool_allowed(t.name, cfg)}
    assert names and all(not srv.is_write_tool(n) for n in names)
    assert "get_invoices" in names


@pytest.mark.asyncio
async def test_call_tool_rejects_disabled_tool(monkeypatch):
    monkeypatch.setenv("DOLIBARR_URL", "https://erp.example.com")
    monkeypatch.setenv("DOLIBARR_API_KEY", "k")
    monkeypatch.setenv("MCP_READ_ONLY", "true")
    result = await srv.handle_call_tool("delete_customer", {"customer_id": 1})
    assert result.isError is True
    payload = json.loads(result.content[0].text)
    assert payload["status"] == 403


def test_defaults_are_safe():
    cfg = _cfg()
    assert cfg.mcp_http_host == "127.0.0.1"
    assert cfg.cors_origins == []
    assert not cfg.mcp_enable_raw_api


class _DummySessionManager:
    def run(self):
        class _Ctx:
            async def __aenter__(self_inner):
                return None

            async def __aexit__(self_inner, *exc):
                return False
        return _Ctx()

    async def handle_request(self, scope, receive, send):
        from starlette.responses import PlainTextResponse
        await PlainTextResponse("ok")(scope, receive, send)


def test_http_requires_bearer_token():
    app = srv._build_http_app(_DummySessionManager(), _cfg(mcp_http_token="s3cret"))
    with TestClient(app) as client:
        assert client.post("/mcp").status_code == 401
        assert client.post("/mcp", headers={"Authorization": "Bearer wrong"}).status_code == 401
        ok = client.post("/mcp", headers={"Authorization": "Bearer s3cret"})
        assert ok.status_code == 200 and ok.text == "ok"


def test_cors_disabled_by_default():
    app = srv._build_http_app(_DummySessionManager(), _cfg(mcp_http_token="t"))
    with TestClient(app) as client:
        r = client.post("/mcp", headers={"Authorization": "Bearer t", "Origin": "https://evil.example"})
        assert "access-control-allow-origin" not in r.headers


def test_cors_allowlist():
    cfg = _cfg(mcp_http_token="t", mcp_cors_origins="https://webui.local")
    app = srv._build_http_app(_DummySessionManager(), cfg)
    with TestClient(app) as client:
        pre = client.options("/mcp", headers={"Origin": "https://webui.local",
                                              "Access-Control-Request-Method": "POST",
                                              "Access-Control-Request-Headers": "authorization"})
        assert pre.status_code == 200
        assert pre.headers["access-control-allow-origin"] == "https://webui.local"
        bad = client.options("/mcp", headers={"Origin": "https://evil.example",
                                              "Access-Control-Request-Method": "POST"})
        assert bad.headers.get("access-control-allow-origin") != "https://evil.example"


@pytest.mark.asyncio
async def test_refuses_public_bind_without_token():
    with pytest.raises(RuntimeError):
        await srv._run_http_server(_cfg(mcp_http_host="0.0.0.0", mcp_http_token=""))
