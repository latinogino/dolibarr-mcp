import pytest
from unittest.mock import AsyncMock, patch
from dolibarr_mcp.config import Config
from dolibarr_mcp.dolibarr_client import DolibarrClient

@pytest.mark.asyncio
class TestInvoiceAtomic:
    
    @pytest.fixture
    def client(self):
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key"
        )
        return DolibarrClient(config)

    @patch('aiohttp.ClientSession.request')
    async def test_add_invoice_line(self, mock_request, client):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = '123' # Returns line ID usually
        mock_request.return_value.__aenter__.return_value = mock_response

        async with client:
            await client.add_invoice_line(
                invoice_id=1,
                desc="Test Line",
                qty=1,
                subprice=100,
                product_id=99
            )

        # Verify call
        args, kwargs = mock_request.call_args
        assert args[0] == "POST"
        assert args[1] == "https://test.dolibarr.com/api/index.php/invoices/1/lines"
        assert kwargs['json'] == {
            "desc": "Test Line",
            "qty": 1,
            "subprice": 100,
            "fk_product": 99
        }

    @patch('aiohttp.ClientSession.request')
    async def test_update_invoice_line(self, mock_request, client):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = '{"success": 1}'
        mock_request.return_value.__aenter__.return_value = mock_response

        async with client:
            await client.update_invoice_line(
                invoice_id=1,
                line_id=10,
                qty=5
            )

        args, kwargs = mock_request.call_args
        assert args[0] == "PUT"
        assert args[1] == "https://test.dolibarr.com/api/index.php/invoices/1/lines/10"
        assert kwargs['json'] == {"qty": 5}

    @patch('aiohttp.ClientSession.request')
    async def test_delete_invoice_line(self, mock_request, client):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = '{"success": 1}'
        mock_request.return_value.__aenter__.return_value = mock_response

        async with client:
            await client.delete_invoice_line(invoice_id=1, line_id=10)

        args, kwargs = mock_request.call_args
        assert args[0] == "DELETE"
        assert args[1] == "https://test.dolibarr.com/api/index.php/invoices/1/lines/10"

    @patch('aiohttp.ClientSession.request')
    async def test_validate_invoice(self, mock_request, client):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = '{"success": 1}'
        mock_request.return_value.__aenter__.return_value = mock_response

        async with client:
            await client.validate_invoice(invoice_id=1, warehouse_id=5)

        args, kwargs = mock_request.call_args
        assert args[0] == "POST"
        assert args[1] == "https://test.dolibarr.com/api/index.php/invoices/1/validate"
        assert kwargs['json'] == {"idwarehouse": 5, "not_trigger": 0}
