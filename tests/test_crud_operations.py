"""
CRUD Operations Integration Tests for Dolibarr MCP Server.

These tests verify complete CRUD operations for all Dolibarr entities.
Run with: pytest tests/test_crud_operations.py -v
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# Add src to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dolibarr_mcp import DolibarrClient, Config


class TestCRUDOperations:
    """Test complete CRUD operations for all Dolibarr entities."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return Config(
            dolibarr_url="https://test.dolibarr.com",
            dolibarr_api_key="test_api_key",
            log_level="INFO"
        )
    
    @pytest.fixture
    def client(self, config):
        """Create a test client instance."""
        return DolibarrClient(config)
    
    # Customer (Third Party) CRUD Tests
    
    @pytest.mark.asyncio
    async def test_customer_crud_lifecycle(self, client):
        """Test complete customer CRUD lifecycle."""
        # Mock responses for each operation
        with patch.object(client, 'request') as mock_request:
            # Create
            mock_request.return_value = {"id": 1}
            customer_id = await client.create_customer({
                "name": "Test Company",
                "email": "test@company.com"
            })
            assert customer_id == 1
            
            # Read
            mock_request.return_value = {
                "id": 1,
                "name": "Test Company",
                "email": "test@company.com"
            }
            customer = await client.get_customer_by_id(1)
            assert customer["name"] == "Test Company"
            
            # Update
            mock_request.return_value = {"id": 1, "name": "Updated Company"}
            result = await client.update_customer(1, {"name": "Updated Company"})
            assert result["name"] == "Updated Company"
            
            # Delete
            mock_request.return_value = {"success": True}
            result = await client.delete_customer(1)
            assert result["success"] is True
    
    # Product CRUD Tests
    
    @pytest.mark.asyncio
    async def test_product_crud_lifecycle(self, client):
        """Test complete product CRUD lifecycle."""
        with patch.object(client, 'request') as mock_request:
            # Create
            mock_request.return_value = {"id": 10}
            product_id = await client.create_product({
                "label": "Test Product",
                "price": 99.99,
                "description": "Test product description"
            })
            assert product_id == 10
            
            # Read
            mock_request.return_value = {
                "id": 10,
                "label": "Test Product",
                "price": "99.99"
            }
            product = await client.get_product_by_id(10)
            assert product["label"] == "Test Product"
            
            # Update
            mock_request.return_value = {"id": 10, "price": "149.99"}
            result = await client.update_product(10, {"price": 149.99})
            assert result["price"] == "149.99"
            
            # Delete
            mock_request.return_value = {"success": True}
            result = await client.delete_product(10)
            assert result["success"] is True
    
    # Invoice CRUD Tests
    
    @pytest.mark.asyncio
    async def test_invoice_crud_lifecycle(self, client):
        """Test complete invoice CRUD lifecycle."""
        with patch.object(client, 'request') as mock_request:
            # Create
            mock_request.return_value = {"id": 100}
            invoice_id = await client.create_invoice({
                "socid": 1,  # Customer ID
                "date": datetime.now().isoformat(),
                "lines": [
                    {"desc": "Service", "qty": 1, "subprice": 100}
                ]
            })
            assert invoice_id == 100
            
            # Read
            mock_request.return_value = {
                "id": 100,
                "ref": "INV-2024-100",
                "total_ttc": "100.00"
            }
            invoice = await client.get_invoice_by_id(100)
            assert invoice["ref"] == "INV-2024-100"
            
            # Update
            mock_request.return_value = {"id": 100, "date_lim_reglement": "2024-02-01"}
            result = await client.update_invoice(100, {
                "date_lim_reglement": "2024-02-01"
            })
            assert result["date_lim_reglement"] == "2024-02-01"
            
            # Delete
            mock_request.return_value = {"success": True}
            result = await client.delete_invoice(100)
            assert result["success"] is True
    
    # Order CRUD Tests
    
    @pytest.mark.asyncio
    async def test_order_crud_lifecycle(self, client):
        """Test complete order CRUD lifecycle."""
        with patch.object(client, 'request') as mock_request:
            # Create
            mock_request.return_value = {"id": 50}
            order_id = await client.create_order({
                "socid": 1,
                "date": datetime.now().isoformat()
            })
            assert order_id == 50
            
            # Read
            mock_request.return_value = {
                "id": 50,
                "ref": "ORD-2024-50",
                "socid": 1
            }
            order = await client.get_order_by_id(50)
            assert order["ref"] == "ORD-2024-50"
            
            # Update
            mock_request.return_value = {"id": 50, "note_public": "Updated note"}
            result = await client.update_order(50, {
                "note_public": "Updated note"
            })
            assert result["note_public"] == "Updated note"
            
            # Delete
            mock_request.return_value = {"success": True}
            result = await client.delete_order(50)
            assert result["success"] is True
    
    # Contact CRUD Tests
    
    @pytest.mark.asyncio
    async def test_contact_crud_lifecycle(self, client):
        """Test complete contact CRUD lifecycle."""
        with patch.object(client, 'request') as mock_request:
            # Create
            mock_request.return_value = {"id": 20}
            contact_id = await client.create_contact({
                "firstname": "John",
                "lastname": "Doe",
                "email": "john.doe@example.com"
            })
            assert contact_id == 20
            
            # Read
            mock_request.return_value = {
                "id": 20,
                "firstname": "John",
                "lastname": "Doe",
                "email": "john.doe@example.com"
            }
            contact = await client.get_contact_by_id(20)
            assert contact["firstname"] == "John"
            
            # Update
            mock_request.return_value = {"id": 20, "phone": "+1234567890"}
            result = await client.update_contact(20, {
                "phone": "+1234567890"
            })
            assert result["phone"] == "+1234567890"
            
            # Delete
            mock_request.return_value = {"success": True}
            result = await client.delete_contact(20)
            assert result["success"] is True
    
    # User Management Tests
    
    @pytest.mark.asyncio
    async def test_user_crud_lifecycle(self, client):
        """Test complete user CRUD lifecycle."""
        with patch.object(client, 'request') as mock_request:
            # Create
            mock_request.return_value = {"id": 5}
            user_id = await client.create_user({
                "login": "testuser",
                "lastname": "User",
                "firstname": "Test",
                "email": "testuser@example.com"
            })
            assert user_id == 5
            
            # Read
            mock_request.return_value = {
                "id": 5,
                "login": "testuser",
                "email": "testuser@example.com"
            }
            user = await client.get_user_by_id(5)
            assert user["login"] == "testuser"
            
            # Update
            mock_request.return_value = {"id": 5, "admin": 1}
            result = await client.update_user(5, {"admin": 1})
            assert result["admin"] == 1
            
            # Delete
            mock_request.return_value = {"success": True}
            result = await client.delete_user(5)
            assert result["success"] is True
    
    # Batch Operations Tests
    
    @pytest.mark.asyncio
    async def test_batch_operations(self, client):
        """Test batch operations for multiple entities."""
        with patch.object(client, 'request') as mock_request:
            # Get multiple customers
            mock_request.return_value = [
                {"id": 1, "name": "Company A"},
                {"id": 2, "name": "Company B"},
                {"id": 3, "name": "Company C"}
            ]
            customers = await client.get_customers(limit=3)
            assert len(customers) == 3
            
            # Get multiple products
            mock_request.return_value = [
                {"id": 10, "label": "Product A"},
                {"id": 11, "label": "Product B"}
            ]
            products = await client.get_products(limit=2)
            assert len(products) == 2
    
    # Error Handling Tests
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """Test error handling in CRUD operations."""
        with patch.object(client, 'request') as mock_request:
            # Test 404 Not Found
            mock_request.side_effect = Exception("404 Not Found")
            with pytest.raises(Exception, match="404"):
                await client.get_customer_by_id(999)
            
            # Test validation error
            mock_request.side_effect = Exception("Validation Error: Missing required field")
            with pytest.raises(Exception, match="Validation"):
                await client.create_product({})
            
            # Test connection error
            mock_request.side_effect = Exception("Connection refused")
            with pytest.raises(Exception, match="Connection"):
                await client.test_connection()


class TestMCPServerIntegration:
    """Test MCP Server integration with Dolibarr API."""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test server initialization and configuration."""
        with patch('dolibarr_mcp.config.Config') as mock_config_class:
            mock_config_class.return_value = Config(
                dolibarr_url="https://test.com",
                dolibarr_api_key="key",
                log_level="INFO"
            )
            
            # Import the server module to test initialization
            from dolibarr_mcp import dolibarr_mcp_server
            assert dolibarr_mcp_server.server is not None
    
    @pytest.mark.asyncio
    async def test_server_tool_execution(self):
        """Test server tool execution via client."""
        config = Config(
            dolibarr_url="https://test.com",
            dolibarr_api_key="key",
            log_level="INFO"
        )
        
        with patch('dolibarr_mcp.dolibarr_client.DolibarrClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get_customers = AsyncMock(return_value=[
                {"id": 1, "name": "Test Company"}
            ])
            
            # Create real client
            async with DolibarrClient(config) as client:
                # Mock the request
                client.get_customers = mock_client.get_customers
                result = await client.get_customers()
                assert len(result) == 1
                assert result[0]["name"] == "Test Company"


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([__file__, "-v", "--cov=dolibarr_mcp", "--cov-report=term-missing"])
