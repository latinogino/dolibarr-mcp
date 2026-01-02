"""Tests for Dolibarr client functionality."""

import pytest
from unittest.mock import AsyncMock, patch

from dolibarr_mcp.config import Config
from dolibarr_mcp.dolibarr_client import DolibarrClient, DolibarrAPIError, DolibarrValidationError


class TestDolibarrClient:
    """Test cases for the DolibarrClient."""
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Test valid configuration
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key"
        )
        assert config.dolibarr_url == "https://test.dolibarr.com/api/index.php"
        assert config.api_key == "test_key"
        
        # Test validation
        config.validate_config()  # Should not raise
        
        # Test invalid URL
        with pytest.raises(ValueError, match="must start with http"):
            invalid_config = Config(
                dolibarr_url="invalid-url",
                api_key="test_key"
            )
            invalid_config.validate_config()
    
    @pytest.mark.asyncio
    async def test_client_session_management(self):
        """Test client session management."""
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key"
        )
        
        client = DolibarrClient(config)
        
        # Test session starts as None
        assert client.session is None
        
        # Test session creation
        await client.start_session()
        assert client.session is not None
        
        # Test session cleanup
        await client.close_session()
        assert client.session is None
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key"
        )
        
        async with DolibarrClient(config) as client:
            assert client.session is not None
        
        # Session should be closed after context exit
        assert client.session is None
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.request')
    async def test_successful_api_request(self, mock_request):
        """Test successful API request."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = '{"success": {"code": 200, "dolibarr_version": "21.0.1"}}'
        mock_request.return_value.__aenter__.return_value = mock_response
        
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key"
        )
        
        async with DolibarrClient(config) as client:
            result = await client.get_status()
            
            assert "success" in result
            assert result["success"]["code"] == 200
            assert result["success"]["dolibarr_version"] == "21.0.1"
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.request')
    async def test_api_error_handling(self, mock_request):
        """Test API error handling."""
        # Mock error response
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.reason = "Not Found"
        mock_response.text.return_value = '{"error": "Object not found"}'
        mock_request.return_value.__aenter__.return_value = mock_response
        
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key"
        )
        
        async with DolibarrClient(config) as client:
            with pytest.raises(DolibarrAPIError) as exc_info:
                await client.get_customer_by_id(999)
            
            assert exc_info.value.status_code == 404
            assert "Object not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validation_error_on_missing_ref(self):
        """Ensure client-side validation catches missing product ref."""
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key",
            allow_ref_autogen=False,
        )

        client = DolibarrClient(config)
        client.request = AsyncMock(return_value={"id": 1})  # Should not be called

        with pytest.raises(DolibarrValidationError) as exc_info:
            await client.create_product({"label": "No Ref", "type": "service", "price": 12.5})

        assert exc_info.value.response_data["missing_fields"] == ["ref"]
        client.request.assert_not_called()

    @pytest.mark.asyncio
    async def test_autogen_ref_when_enabled(self):
        """Auto-generate refs when allowed by configuration."""
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key",
            allow_ref_autogen=True,
            ref_autogen_prefix="AUTOREF",
        )

        client = DolibarrClient(config)
        client.request = AsyncMock(return_value={"id": 42, "ref": "AUTOREF_123"})

        await client.create_product({"label": "Generated Ref Product", "type": "service", "price": 10})

        assert client.request.await_count == 1
        sent_payload = client.request.call_args.kwargs["data"]
        assert "ref" in sent_payload
        assert sent_payload["ref"].startswith("AUTOREF_")

    @pytest.mark.asyncio
    async def test_product_validation_requires_price_field(self):
        """Ensure products require at least one pricing field."""
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key",
        )

        client = DolibarrClient(config)
        client.request = AsyncMock(return_value={"id": 99})  # Should not be called

        with pytest.raises(DolibarrValidationError) as exc_info:
            await client.create_product({"ref": "SKU-1", "label": "Widget", "type": "product"})

        assert exc_info.value.response_data["missing_fields"] == ["price or price_ttc"]
        client.request.assert_not_called()

    @pytest.mark.asyncio
    async def test_product_validation_allows_price_ttc(self):
        """Validate products using price_ttc instead of price."""
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key",
        )

        client = DolibarrClient(config)
        client.request = AsyncMock(return_value={"id": 101})

        await client.create_product({"ref": "SKU-2", "label": "Widget TTC", "type": "product", "price_ttc": 12.5})

        sent_payload = client.request.call_args.kwargs["data"]
        assert sent_payload["price_ttc"] == 12.5
        assert "price" not in sent_payload

    @pytest.mark.asyncio
    async def test_project_validation_missing_socid(self):
        """Ensure projects require ref and socid (name/title also required)."""
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key",
        )

        client = DolibarrClient(config)
        client.request = AsyncMock(return_value={"id": 33})  # Should not be called

        with pytest.raises(DolibarrValidationError) as exc_info:
            await client.create_project({"ref": "PRJ-1", "title": "Missing Soc"})

        assert "socid" in exc_info.value.response_data["missing_fields"]
        client.request.assert_not_called()

    @pytest.mark.asyncio
    async def test_project_autogen_ref_when_enabled(self):
        """Auto-generate project references when allowed and missing."""
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key",
            allow_ref_autogen=True,
            ref_autogen_prefix="PROJ",
        )

        client = DolibarrClient(config)
        client.request = AsyncMock(return_value={"id": 77})

        await client.create_project({"title": "Generated Ref Project", "socid": 5})

        sent_payload = client.request.call_args.kwargs["data"]
        assert "ref" in sent_payload
        assert sent_payload["ref"].startswith("PROJ_")

    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.request')
    async def test_internal_error_correlation_id(self, mock_request):
        """Include correlation IDs for unexpected server errors."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.reason = "Internal Server Error"
        mock_response.text.return_value = '{"message": "Database unavailable"}'
        mock_request.return_value.__aenter__.return_value = mock_response

        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key"
        )

        async with DolibarrClient(config) as client:
            with pytest.raises(DolibarrAPIError) as exc_info:
                await client.get_project_by_id(1)

            assert exc_info.value.status_code == 500
            assert "correlation_id" in exc_info.value.response_data
    
    def test_url_building(self):
        """Test URL building functionality."""
        config = Config(
            dolibarr_url="https://test.dolibarr.com/api/index.php",
            api_key="test_key"
        )
        
        client = DolibarrClient(config)
        
        # Test with leading slash
        url = client._build_url("/users")
        assert url == "https://test.dolibarr.com/api/index.php/users"
        
        # Test without leading slash
        url = client._build_url("users")
        assert url == "https://test.dolibarr.com/api/index.php/users"
        
        # Test with trailing slash in base URL
        client.base_url = "https://test.dolibarr.com/api/index.php/"
        url = client._build_url("users")
        assert url == "https://test.dolibarr.com/api/index.php/users"


class TestDolibarrAPIError:
    """Test cases for DolibarrAPIError."""
    
    def test_error_creation(self):
        """Test error object creation."""
        error = DolibarrAPIError(
            message="Test error",
            status_code=400,
            response_data={"error": "Bad request"}
        )
        
        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.response_data == {"error": "Bad request"}
    
    def test_error_without_optional_params(self):
        """Test error creation without optional parameters."""
        error = DolibarrAPIError("Simple error")
        
        assert str(error) == "Simple error"
        assert error.status_code is None
        assert error.response_data is None


# Example of how to add integration tests
@pytest.mark.integration
class TestDolibarrIntegration:
    """Integration tests (require real Dolibarr instance)."""
    
    @pytest.mark.asyncio
    async def test_real_connection(self):
        """Test connection to real Dolibarr instance."""
        # Skip if no real credentials available
        try:
            config = Config.from_env()
            config.validate_config()
        except ValueError:
            pytest.skip("No valid Dolibarr configuration available")
        
        async with DolibarrClient(config) as client:
            try:
                result = await client.get_status()
                assert "success" in result or "dolibarr_version" in str(result)
            except DolibarrAPIError as e:
                pytest.fail(f"API connection failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
