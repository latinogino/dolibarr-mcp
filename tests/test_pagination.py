"""Tool pages start at 1; Dolibarr list endpoints number pages from 0."""

from unittest.mock import AsyncMock, patch

import pytest

from dolibarr_mcp.config import Config
from dolibarr_mcp.dolibarr_client import DolibarrClient


@pytest.fixture
def client():
    return DolibarrClient(Config(dolibarr_url="https://test.dolibarr.com", dolibarr_api_key="k"))


@pytest.mark.asyncio
@pytest.mark.parametrize("method, endpoint", [
    ("get_users", "users"),
    ("get_customers", "thirdparties"),
    ("get_projects", "projects"),
])
@pytest.mark.parametrize("page, expected", [(1, None), (2, 1), (3, 2)])
async def test_page_is_translated_to_zero_based(client, method, endpoint, page, expected):
    with patch.object(client, "request", new=AsyncMock(return_value=[])) as mock_request:
        await getattr(client, method)(limit=10, page=page)

    assert mock_request.call_args.args == ("GET", endpoint)
    params = mock_request.call_args.kwargs["params"]
    assert params.get("page") == expected
