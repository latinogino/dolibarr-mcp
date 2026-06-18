"""
Ticket Management Tests for Dolibarr MCP Server.

These tests verify the ticket tools: listing, lookup by reference, search,
creation, adding messages, and updates. Focus is on the ticket-specific
behaviour (ref/track_id resolution and payload validation).
Run with: pytest tests/test_ticket_operations.py -v
"""

import pytest
from unittest.mock import patch, AsyncMock

# Add src to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dolibarr_mcp import DolibarrClient, Config
from dolibarr_mcp.dolibarr_client import DolibarrValidationError


class TestTicketOperations:
    """Test ticket tools on the Dolibarr client."""

    @pytest.fixture
    def config(self):
        return Config(
            dolibarr_url="https://test.dolibarr.com",
            dolibarr_api_key="test_api_key",
            log_level="INFO",
        )

    @pytest.fixture
    def client(self, config):
        return DolibarrClient(config)

    @pytest.mark.asyncio
    async def test_get_tickets_defaults_to_open(self, client):
        """Without a status filter only open tickets are requested."""
        with patch.object(client, 'request', new=AsyncMock(return_value=[])) as mock_request:
            await client.get_tickets()

            method, endpoint = mock_request.call_args[0]
            params = mock_request.call_args[1]["params"]
            assert method == "GET"
            assert endpoint == "tickets"
            assert params["sqlfilters"] == "(t.fk_statut:!=:8) and (t.fk_statut:!=:9)"

    @pytest.mark.asyncio
    async def test_get_tickets_with_status_filter(self, client):
        """An explicit status filters on fk_statut."""
        with patch.object(client, 'request', new=AsyncMock(return_value=[])) as mock_request:
            await client.get_tickets(status=5)

            params = mock_request.call_args[1]["params"]
            assert params["sqlfilters"] == "(t.fk_statut:=:5)"

    @pytest.mark.asyncio
    async def test_get_ticket_by_ref(self, client):
        """Lookup by reference hits the dedicated ref endpoint."""
        with patch.object(
            client, 'request',
            new=AsyncMock(return_value={"id": "1140", "ref": "TI1046", "track_id": "abc123"}),
        ) as mock_request:
            ticket = await client.get_ticket_by_ref("TI1046")

            method, endpoint = mock_request.call_args[0]
            assert method == "GET"
            assert endpoint == "tickets/ref/TI1046"
            assert ticket["track_id"] == "abc123"

    @pytest.mark.asyncio
    async def test_search_tickets(self, client):
        with patch.object(
            client, 'request',
            new=AsyncMock(return_value=[{"id": "1140", "ref": "TI1046"}]),
        ) as mock_request:
            results = await client.search_tickets(
                sqlfilters="((t.ref:like:'%TI1046%'))", limit=10
            )

            assert len(results) == 1
            method, endpoint = mock_request.call_args[0]
            params = mock_request.call_args[1]["params"]
            assert method == "GET"
            assert endpoint == "tickets"
            assert params["limit"] == 10

    @pytest.mark.asyncio
    async def test_create_ticket(self, client):
        with patch.object(client, 'request', new=AsyncMock(return_value={"id": 1141})) as mock_request:
            ticket_id = await client.create_ticket(
                subject="Printer broken",
                message="The office printer does not respond.",
                socid=79,
            )

            assert ticket_id == 1141
            method, endpoint = mock_request.call_args[0]
            payload = mock_request.call_args[1]["data"]
            assert method == "POST"
            assert endpoint == "tickets"
            assert payload["subject"] == "Printer broken"
            assert payload["socid"] == 79

    @pytest.mark.asyncio
    async def test_create_ticket_fk_soc_alias(self, client):
        """fk_soc is promoted to socid."""
        with patch.object(client, 'request', new=AsyncMock(return_value={"id": 1142})) as mock_request:
            await client.create_ticket(subject="X", message="Y", fk_soc=79)

            payload = mock_request.call_args[1]["data"]
            assert payload["socid"] == 79
            assert "fk_soc" not in payload

    @pytest.mark.asyncio
    async def test_create_ticket_requires_subject_and_message(self, client):
        with patch.object(client, 'request', new=AsyncMock()) as mock_request:
            with pytest.raises(DolibarrValidationError) as exc:
                await client.create_ticket(subject="Only subject")

            assert "message" in exc.value.response_data["missing_fields"]
            mock_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_ticket_message_with_track_id(self, client):
        """A given track_id is used directly without a lookup."""
        with patch.object(client, 'request', new=AsyncMock(return_value={"success": True})) as mock_request:
            with patch.object(client, 'get_ticket_by_ref', new=AsyncMock()) as mock_lookup:
                await client.add_ticket_message(track_id="abc123", message="Any update?")

                mock_lookup.assert_not_called()
                method, endpoint = mock_request.call_args[0]
                payload = mock_request.call_args[1]["data"]
                assert method == "POST"
                assert endpoint == "tickets/messages"
                assert payload["track_id"] == "abc123"
                assert "ref" not in payload

    @pytest.mark.asyncio
    async def test_add_ticket_message_resolves_ref(self, client):
        """A ref is resolved to its track_id before posting."""
        with patch.object(client, 'request', new=AsyncMock(return_value={"success": True})) as mock_request:
            with patch.object(
                client, 'get_ticket_by_ref',
                new=AsyncMock(return_value={"id": "1140", "track_id": "resolved999"}),
            ) as mock_lookup:
                await client.add_ticket_message(ref="TI1046", message="Resolved message")

                mock_lookup.assert_awaited_once_with("TI1046")
                payload = mock_request.call_args[1]["data"]
                assert payload["track_id"] == "resolved999"
                assert "ref" not in payload

    @pytest.mark.asyncio
    async def test_add_ticket_message_requires_ref_or_track_id(self, client):
        with patch.object(client, 'request', new=AsyncMock()) as mock_request:
            with pytest.raises(DolibarrValidationError) as exc:
                await client.add_ticket_message(message="No target")

            assert "track_id or ref" in exc.value.response_data["missing_fields"]
            mock_request.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_ticket_by_id(self, client):
        with patch.object(client, 'request', new=AsyncMock(return_value={"id": 1140})) as mock_request:
            await client.update_ticket(ticket_id=1140, fk_statut=8)

            method, endpoint = mock_request.call_args[0]
            payload = mock_request.call_args[1]["data"]
            assert method == "PUT"
            assert endpoint == "tickets/1140"
            assert payload["fk_statut"] == 8

    @pytest.mark.asyncio
    async def test_update_ticket_resolves_ref(self, client):
        """When only a ref is given the internal id is resolved first."""
        with patch.object(client, 'request', new=AsyncMock(return_value={"id": 1140})) as mock_request:
            with patch.object(
                client, 'get_ticket_by_ref',
                new=AsyncMock(return_value={"id": "1140", "ref": "TI1046"}),
            ) as mock_lookup:
                await client.update_ticket(ref="TI1046", fk_statut=4)

                mock_lookup.assert_awaited_once_with("TI1046")
                method, endpoint = mock_request.call_args[0]
                assert method == "PUT"
                assert endpoint == "tickets/1140"

    @pytest.mark.asyncio
    async def test_update_ticket_requires_id_or_ref(self, client):
        with patch.object(client, 'request', new=AsyncMock()) as mock_request:
            with pytest.raises(DolibarrValidationError) as exc:
                await client.update_ticket(fk_statut=8)

            assert "ticket_id or ref" in exc.value.response_data["missing_fields"]
            mock_request.assert_not_called()
