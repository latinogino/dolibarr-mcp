import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from dolibarr_mcp.dolibarr_mcp_server import handle_call_tool
from dolibarr_mcp.dolibarr_client import DolibarrClient

@pytest.mark.asyncio
async def test_search_products_by_ref():
    # Mock DolibarrClient
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        
        # Mock search_products response
        mock_instance.search_products = AsyncMock(return_value=[
            {"id": 1, "ref": "PRJ-123", "label": "Project 123"}
        ])
        
        # Call the tool
        result = await handle_call_tool("search_products_by_ref", {"ref_prefix": "PRJ"})
        
        # Verify the call
        mock_instance.search_products.assert_called_once()
        call_args = mock_instance.search_products.call_args
        assert "sqlfilters" in call_args.kwargs
        assert call_args.kwargs["sqlfilters"] == "(t.ref:like:'PRJ%')"
        
        # Verify result
        assert "PRJ-123" in result[0].text

@pytest.mark.asyncio
async def test_resolve_product_ref_exact():
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        
        # Mock search_products response (exact match)
        mock_instance.search_products = AsyncMock(return_value=[
            {"id": 1, "ref": "PRJ-123", "label": "Project 123"}
        ])
        
        result = await handle_call_tool("resolve_product_ref", {"ref": "PRJ-123"})
        
        mock_instance.search_products.assert_called_once()
        assert "ok" in result[0].text
        assert "PRJ-123" in result[0].text

@pytest.mark.asyncio
async def test_resolve_product_ref_ambiguous():
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        
        # Mock search_products response (multiple matches, none exact)
        mock_instance.search_products = AsyncMock(return_value=[
            {"id": 1, "ref": "PRJ-123-A", "label": "Project 123 A"},
            {"id": 2, "ref": "PRJ-123-B", "label": "Project 123 B"}
        ])
        
        # Search for "PRJ-123" which matches both partially (hypothetically) but neither exactly
        result = await handle_call_tool("resolve_product_ref", {"ref": "PRJ-123"})
        
        assert "ambiguous" in result[0].text

@pytest.mark.asyncio
async def test_search_customers():
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        
        mock_instance.search_customers = AsyncMock(return_value=[
            {"id": 1, "nom": "Acme Corp"}
        ])
        
        result = await handle_call_tool("search_customers", {"query": "Acme"})
        
        mock_instance.search_customers.assert_called_once()
        call_args = mock_instance.search_customers.call_args
        assert "sqlfilters" in call_args.kwargs
        assert "Acme" in call_args.kwargs["sqlfilters"]
