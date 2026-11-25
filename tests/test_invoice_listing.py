"""Tests for the get_invoices tool: customer filter, sorting, paging, compact output."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from dolibarr_mcp.config import Config
from dolibarr_mcp.dolibarr_client import DolibarrAPIError, DolibarrClient
from dolibarr_mcp.dolibarr_mcp_server import _summarize_invoice, handle_call_tool

LOCAL_MIDNIGHT = int(datetime(2024, 3, 15).timestamp())

RAW_INVOICE = {
    "id": "101",
    "ref": "FA2024-0001",
    "ref_client": "",
    "socid": "12",
    "type": "0",
    "date": LOCAL_MIDNIGHT,
    "date_lim_reglement": LOCAL_MIDNIGHT,
    "total_ht": "100.00000000",
    "total_tva": "20.00000000",
    "total_ttc": "120.00000000",
    "status": "1",
    "paye": "0",
    "remaintopay": 120.0,
    "fk_project": None,
    "lines": [{"desc": "big payload"}],
    "array_options": {"options_x": None},
}


def _mock_client(MockClient, invoices):
    instance = MockClient.return_value
    instance.__aenter__.return_value = instance
    instance.get_invoices = AsyncMock(return_value=invoices)
    return instance


def test_summarize_invoice_keeps_useful_fields_only():
    summary = _summarize_invoice(RAW_INVOICE)
    assert summary == {
        "id": 101,
        "ref": "FA2024-0001",
        "ref_client": None,
        "socid": 12,
        "type": "standard",
        "date": "2024-03-15",
        "due_date": "2024-03-15",
        "total_ht": "100.00000000",
        "total_tva": "20.00000000",
        "total_ttc": "120.00000000",
        "status": "unpaid",
        "paid": False,
        "remain_to_pay": 120.0,
        "project_id": None,
    }


@pytest.mark.asyncio
async def test_get_invoices_defaults_to_newest_first_compact():
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        client = _mock_client(MockClient, [RAW_INVOICE])

        result = await handle_call_tool("get_invoices", {"customer_id": 12})

        client.get_invoices.assert_awaited_once_with(
            limit=20,
            status=None,
            customer_id=12,
            page=0,
            sortfield="t.datef",
            sortorder="DESC",
        )
        payload = json.loads(result[0].text)
        assert payload[0]["ref"] == "FA2024-0001"
        assert "lines" not in payload[0]


@pytest.mark.asyncio
async def test_get_invoices_caps_limit_and_passes_paging():
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        client = _mock_client(MockClient, [])

        await handle_call_tool(
            "get_invoices",
            {"limit": 5000, "page": 3, "status": "paid", "sort_by": "ref", "sort_order": "asc"},
        )

        kwargs = client.get_invoices.call_args.kwargs
        assert kwargs["limit"] == 200
        assert kwargs["page"] == 3
        assert kwargs["status"] == "paid"
        assert kwargs["sortfield"] == "t.ref"
        assert kwargs["sortorder"] == "ASC"


@pytest.mark.asyncio
async def test_get_invoices_full_returns_raw_objects():
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        _mock_client(MockClient, [RAW_INVOICE])

        result = await handle_call_tool("get_invoices", {"full": True})

        assert json.loads(result[0].text)[0]["lines"] == [{"desc": "big payload"}]


@pytest.mark.asyncio
async def test_get_invoices_rejects_unknown_sort_field():
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        client = _mock_client(MockClient, [])

        result = await handle_call_tool("get_invoices", {"sort_by": "t.datef; DROP"})

        client.get_invoices.assert_not_awaited()
        assert result.isError
        assert "sort_by" in result.content[0].text


def _config():
    return Config(dolibarr_url="https://test.example.com/api/index.php", api_key="test_key")


@pytest.mark.asyncio
async def test_client_get_invoices_builds_dolibarr_params():
    client = DolibarrClient(_config())
    with patch.object(client, "request", AsyncMock(return_value=[])) as request:
        await client.get_invoices(
            limit=10, status="paid", customer_id=12, page=2, sortfield="t.datef", sortorder="DESC"
        )
        request.assert_awaited_once_with(
            "GET",
            "invoices",
            params={
                "limit": 10,
                "status": "paid",
                "thirdparty_ids": "12",
                "page": 2,
                "sortfield": "t.datef",
                "sortorder": "DESC",
            },
        )


@pytest.mark.asyncio
async def test_client_get_invoices_empty_result_on_404():
    client = DolibarrClient(_config())
    error = DolibarrAPIError("Not Found", status_code=404)
    with patch.object(client, "request", AsyncMock(side_effect=error)):
        assert await client.get_invoices(customer_id=999) == []
