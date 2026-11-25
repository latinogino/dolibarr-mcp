import json
import pytest
from unittest.mock import AsyncMock, patch
from dolibarr_mcp.config import Config
from dolibarr_mcp.dolibarr_client import DolibarrAPIError, DolibarrClient

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
        args, kwargs = next(c for c in mock_request.call_args_list if c.args[0] == "POST")
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
        """Dolibarr's PUT resets omitted fields: the current line must be merged in."""
        current_lines = json.dumps([
            {"id": "9", "qty": "1", "subprice": "1.0", "desc": "Other", "tva_tx": "20.000"},
            {
                "id": "10", "rowid": "10", "fk_product": "16", "product_type": "1",
                "qty": "0.5", "subprice": "80.00000000", "tva_tx": "0.000",
                "desc": "Support service", "remise_percent": "0", "date_start": "",
                "product_ref": "SERV-SUPPORT",
            },
        ])
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.side_effect = [current_lines, '{"success": 1}']
        mock_request.return_value.__aenter__.return_value = mock_response

        async with client:
            await client.update_invoice_line(invoice_id=1, line_id=10, vat=20)

        args, kwargs = mock_request.call_args
        assert args[0] == "PUT"
        assert args[1] == "https://test.dolibarr.com/api/index.php/invoices/1/lines/10"
        assert kwargs['json'] == {
            "desc": "Support service",
            "subprice": "80.00000000",
            "qty": "0.5",
            "tva_tx": 20,
            "fk_product": "16",
            "product_type": "1",
            "remise_percent": "0",
        }

    @patch('aiohttp.ClientSession.request')
    async def test_update_invoice_line_unknown_line(self, mock_request, client):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = '[]'
        mock_request.return_value.__aenter__.return_value = mock_response

        async with client:
            with pytest.raises(DolibarrAPIError):
                await client.update_invoice_line(invoice_id=1, line_id=10, qty=5)
        assert all(c.args[0] == "GET" for c in mock_request.call_args_list)

    @patch('aiohttp.ClientSession.request')
    async def test_add_invoice_line_5xx_after_insert(self, mock_request, client):
        """A 5xx after Dolibarr inserted the line returns the new id, not an error."""
        ok, ko = AsyncMock(), AsyncMock()
        ok.status, ko.status = 200, 500
        ok.text.side_effect = ['[{"id": "1"}]', '[{"id": "1"}, {"id": "2"}]']
        ko.text.return_value = '{"error": {"code": 500, "message": "boom"}}'
        mock_request.return_value.__aenter__.side_effect = [ok, ko, ok]

        async with client:
            result = await client.add_invoice_line(invoice_id=1, desc="L", qty=1, subprice=10)
        assert result == 2

    @patch('aiohttp.ClientSession.request')
    async def test_add_invoice_line_5xx_without_insert(self, mock_request, client):
        """A real failure still raises, with Dolibarr's own message."""
        ok, ko = AsyncMock(), AsyncMock()
        ok.status, ko.status = 200, 500
        ok.text.return_value = '[{"id": "1"}]'
        ko.text.return_value = '{"error": {"code": 500, "message": "boom"}}'
        mock_request.return_value.__aenter__.side_effect = [ok, ko, ok]

        async with client:
            with pytest.raises(DolibarrAPIError) as excinfo:
                await client.add_invoice_line(invoice_id=1, desc="L", qty=1, subprice=10)
        assert excinfo.value.message == "boom"

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

    @patch('aiohttp.ClientSession.request')
    async def test_line_vat_is_sent_as_tva_tx(self, mock_request, client):
        """Dolibarr ignores 'vat' and books 0% VAT: it must be sent as tva_tx."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = '123'
        mock_request.return_value.__aenter__.return_value = mock_response

        async with client:
            await client.add_invoice_line(invoice_id=1, desc="L", qty=1, subprice=10, vat=20)
            assert mock_request.call_args.kwargs['json'] == {
                "desc": "L", "qty": 1, "subprice": 10, "tva_tx": 20
            }

            await client.create_invoice(
                customer_id=7, lines=[{"desc": "L", "qty": 1, "subprice": 10, "vat": 20}]
            )
            sent_line = mock_request.call_args.kwargs['json']["lines"][0]
            assert sent_line["tva_tx"] == 20 and "vat" not in sent_line
