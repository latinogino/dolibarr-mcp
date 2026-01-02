"""
Project Management Integration Tests for Dolibarr MCP Server.

These tests verify complete CRUD operations for Dolibarr projects.
Run with: pytest tests/test_project_operations.py -v
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


class TestProjectOperations:
    """Test complete CRUD operations for Dolibarr projects."""
    
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
    
    @pytest.mark.asyncio
    async def test_project_crud_lifecycle(self, client):
        """Test complete project CRUD lifecycle."""
        with patch.object(client, 'request') as mock_request:
            # Create
            mock_request.return_value = {"id": 200}
            project_id = await client.create_project({
                "ref": "PRJ-NEW-WEBSITE",
                "title": "New Website",
                "description": "Website redesign project",
                "socid": 1,
                "status": 1
            })
            assert project_id == 200
            
            # Read
            mock_request.return_value = {
                "id": 200,
                "ref": "PJ2401-001",
                "title": "New Website",
                "description": "Website redesign project"
            }
            project = await client.get_project_by_id(200)
            assert project["title"] == "New Website"
            assert project["ref"] == "PJ2401-001"
            
            # Update
            mock_request.return_value = {"id": 200, "title": "Updated Website Project"}
            result = await client.update_project(200, {"title": "Updated Website Project"})
            assert result["title"] == "Updated Website Project"
            
            # Delete
            mock_request.return_value = {"success": True}
            result = await client.delete_project(200)
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_search_projects(self, client):
        """Test searching projects."""
        with patch.object(client, 'request') as mock_request:
            mock_request.return_value = [
                {"id": 200, "ref": "PJ2401-001", "title": "Website Redesign"},
                {"id": 201, "ref": "PJ2401-002", "title": "Mobile App"}
            ]
            
            # Search by query
            results = await client.search_projects(sqlfilters="(t.title:like:'%Website%')", limit=10)
            
            assert len(results) == 2
            assert results[0]["title"] == "Website Redesign"
            
            # Verify call arguments
            call_args = mock_request.call_args
            assert call_args is not None
            method, endpoint = call_args[0]
            kwargs = call_args[1]
            
            assert method == "GET"
            assert endpoint == "projects"
            assert kwargs["params"]["sqlfilters"] == "(t.title:like:'%Website%')"

    @pytest.mark.asyncio
    async def test_get_projects_with_filters(self, client):
        """Test getting projects with status filter."""
        with patch.object(client, 'request') as mock_request:
            mock_request.return_value = []
            
            await client.get_projects(limit=50, page=2, status=1)
            
            call_args = mock_request.call_args
            kwargs = call_args[1]
            params = kwargs["params"]
            
            assert params["limit"] == 50
            assert params["page"] == 2
            assert params["status"] == 1
