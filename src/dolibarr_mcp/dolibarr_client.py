"""Professional Dolibarr API client with comprehensive CRUD operations."""

import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from .config import Config


class DolibarrAPIError(Exception):
    """Custom exception for Dolibarr API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class DolibarrClient:
    """Professional Dolibarr API client with comprehensive functionality."""
    
    def __init__(self, config: Config):
        """Initialize the Dolibarr client."""
        self.config = config
        self.base_url = config.dolibarr_url.rstrip('/')
        self.api_key = config.api_key
        self.session: Optional[ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
        # Configure timeout
        self.timeout = ClientTimeout(total=30, connect=10)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_session()
    
    async def start_session(self):
        """Start the HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    "DOLAPIKEY": self.api_key,
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
    
    async def close_session(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    @staticmethod
    def _extract_identifier(response: Any) -> Any:
        """Return the identifier from Dolibarr responses when available."""
        if isinstance(response, dict):
            if "id" in response:
                return response["id"]
            success = response.get("success")
            if isinstance(success, dict) and "id" in success:
                return success["id"]
        return response

    @staticmethod
    def _merge_payload(data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Merge an optional dictionary with keyword overrides."""
        payload: Dict[str, Any] = {}
        if data:
            payload.update(data)
        if kwargs:
            payload.update(kwargs)
        return payload

    
    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Public helper retained for compatibility with legacy integrations and tests."""
        return await self._make_request(method, endpoint, params=params, data=data)

    def _build_url(self, endpoint: str) -> str:
        """Build full API URL."""
        endpoint = endpoint.lstrip('/')
        base = self.base_url.rstrip('/')

        if endpoint == "status":
            base_without_index = base.replace('/index.php', '')
            return f"{base_without_index}/status"

        return f"{base}/{endpoint}"

    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Dolibarr API."""
        if not self.session:
            await self.start_session()
        
        url = self._build_url(endpoint)
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            kwargs = {
                "params": params or {},
            }
            
            if data and method.upper() in ["POST", "PUT"]:
                kwargs["json"] = data
            
            async with self.session.request(method, url, **kwargs) as response:
                response_text = await response.text()
                
                # Log response for debugging
                self.logger.debug(f"Response status: {response.status}")
                self.logger.debug(f"Response text: {response_text[:500]}...")
                
                # Try to parse JSON response
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    response_data = {"raw_response": response_text}
                
                # Handle error responses
                if response.status >= 400:
                    error_msg = f"HTTP {response.status}: {response.reason}"
                    if isinstance(response_data, dict):
                        if "error" in response_data:
                            error_details = response_data["error"]
                            if isinstance(error_details, dict):
                                error_msg = error_details.get("message", error_msg)
                                if "code" in error_details:
                                    error_msg = f"{error_msg} (Code: {error_details['code']})"
                            else:
                                error_msg = str(error_details)
                        elif "message" in response_data:
                            error_msg = response_data["message"]
                    
                    raise DolibarrAPIError(
                        message=error_msg,
                        status_code=response.status,
                        response_data=response_data
                    )
                
                return response_data
                
        except aiohttp.ClientError as e:
            # For status endpoint, try alternative URL if first attempt fails
            if endpoint == "status" and not url.endswith("/api/status"):
                try:
                    # Try with /api/index.php/setup/modules as alternative
                    alt_url = f"{self.base_url}/setup/modules"
                    self.logger.debug(f"Status failed, trying alternative: {alt_url}")
                    
                    async with self.session.get(alt_url) as response:
                        if response.status == 200:
                            # Return a status-like response
                            return {
                                "success": 1,
                                "dolibarr_version": "API Available",
                                "api_version": "1.0"
                            }
                except:
                    pass
            
            raise DolibarrAPIError(f"HTTP client error: {endpoint}")
        except Exception as e:
            if isinstance(e, DolibarrAPIError):
                raise
            raise DolibarrAPIError(f"Unexpected error: {str(e)}")
    
    # ============================================================================
    # SYSTEM ENDPOINTS
    # ============================================================================
    
    async def test_connection(self) -> Dict[str, Any]:
        """Compatibility helper that proxies to get_status."""
        return await self.get_status()

    async def get_status(self) -> Dict[str, Any]:
        """Get API status and version information."""
        try:
            # First try the standard status endpoint
            return await self.request("GET", "status")
        except DolibarrAPIError:
            # If status fails, try to get module list as a connectivity test
            try:
                result = await self.request("GET", "setup/modules")
                if result:
                    return {
                        "success": 1,
                        "dolibarr_version": "Connected",
                        "api_version": "1.0",
                        "modules_available": isinstance(result, (list, dict))
                    }
            except:
                pass
            
            # If all else fails, try a simple user list
            try:
                result = await self.request("GET", "users?limit=1")
                if result is not None:
                    return {
                        "success": 1,
                        "dolibarr_version": "API Working",
                        "api_version": "1.0"
                    }
            except:
                raise DolibarrAPIError("Cannot connect to Dolibarr API. Please check your configuration.")
    
    # ============================================================================
    # USER MANAGEMENT
    # ============================================================================
    
    async def get_users(self, limit: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Get list of users."""
        params = {"limit": limit}
        if page > 1:
            params["page"] = page
        
        result = await self.request("GET", "users", params=params)
        return result if isinstance(result, list) else []
    
    async def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get specific user by ID."""
        return await self.request("GET", f"users/{user_id}")
    
    async def create_user(
        self,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new user."""
        payload = self._merge_payload(data, **kwargs)
        result = await self.request("POST", "users", data=payload)
        return self._extract_identifier(result)

    async def update_user(
        self,
        user_id: int,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update an existing user."""
        payload = self._merge_payload(data, **kwargs)
        return await self.request("PUT", f"users/{user_id}", data=payload)

    async def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Delete a user."""
        return await self.request("DELETE", f"users/{user_id}")
    
    # ============================================================================
    # CUSTOMER/THIRD PARTY MANAGEMENT
    # ============================================================================
    
    async def get_customers(self, limit: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Get list of customers/third parties."""
        params = {"limit": limit}
        if page > 1:
            params["page"] = page
        
        result = await self.request("GET", "thirdparties", params=params)
        return result if isinstance(result, list) else []
    
    async def get_customer_by_id(self, customer_id: int) -> Dict[str, Any]:
        """Get specific customer by ID."""
        return await self.request("GET", f"thirdparties/{customer_id}")
    
    async def create_customer(
        self,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new customer/third party."""
        payload = self._merge_payload(data, **kwargs)

        type_value = payload.pop("type", None)
        if type_value is not None:
            payload.setdefault("client", 1 if type_value in (1, 3) else 0)
            payload.setdefault("fournisseur", 1 if type_value in (2, 3) else 0)
        else:
            payload.setdefault("client", 1)

        payload.setdefault("status", payload.get("status", 1))
        payload.setdefault("country_id", payload.get("country_id", 1))

        result = await self.request("POST", "thirdparties", data=payload)
        return self._extract_identifier(result)

    async def update_customer(
        self,
        customer_id: int,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update an existing customer."""
        payload = self._merge_payload(data, **kwargs)

        type_value = payload.pop("type", None)
        if type_value is not None:
            payload["client"] = 1 if type_value in (1, 3) else 0
            payload["fournisseur"] = 1 if type_value in (2, 3) else 0

        return await self.request("PUT", f"thirdparties/{customer_id}", data=payload)

    async def delete_customer(self, customer_id: int) -> Dict[str, Any]:
        """Delete a customer."""
        return await self.request("DELETE", f"thirdparties/{customer_id}")
    
    # ============================================================================
    # PRODUCT MANAGEMENT
    # ============================================================================
    
    async def get_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of products."""
        params = {"limit": limit}
        result = await self.request("GET", "products", params=params)
        return result if isinstance(result, list) else []
    
    async def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """Get specific product by ID."""
        return await self.request("GET", f"products/{product_id}")
    
    async def create_product(
        self,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new product or service."""
        payload = self._merge_payload(data, **kwargs)
        result = await self.request("POST", "products", data=payload)
        return self._extract_identifier(result)

    async def update_product(
        self,
        product_id: int,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update an existing product."""
        payload = self._merge_payload(data, **kwargs)
        return await self.request("PUT", f"products/{product_id}", data=payload)

    async def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Delete a product."""
        return await self.request("DELETE", f"products/{product_id}")
    
    # ============================================================================
    # INVOICE MANAGEMENT
    # ============================================================================
    
    async def get_invoices(self, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of invoices."""
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        result = await self.request("GET", "invoices", params=params)
        return result if isinstance(result, list) else []
    
    async def get_invoice_by_id(self, invoice_id: int) -> Dict[str, Any]:
        """Get specific invoice by ID."""
        return await self.request("GET", f"invoices/{invoice_id}")
    
    async def create_invoice(
        self,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new invoice."""
        payload = self._merge_payload(data, **kwargs)
        result = await self.request("POST", "invoices", data=payload)
        return self._extract_identifier(result)

    async def update_invoice(
        self,
        invoice_id: int,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update an existing invoice."""
        payload = self._merge_payload(data, **kwargs)
        return await self.request("PUT", f"invoices/{invoice_id}", data=payload)

    async def delete_invoice(self, invoice_id: int) -> Dict[str, Any]:
        """Delete an invoice."""
        return await self.request("DELETE", f"invoices/{invoice_id}")
    
    # ============================================================================
    # ORDER MANAGEMENT
    # ============================================================================
    
    async def get_orders(self, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of orders."""
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        result = await self.request("GET", "orders", params=params)
        return result if isinstance(result, list) else []
    
    async def get_order_by_id(self, order_id: int) -> Dict[str, Any]:
        """Get specific order by ID."""
        return await self.request("GET", f"orders/{order_id}")
    
    async def create_order(
        self,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new order."""
        payload = self._merge_payload(data, **kwargs)
        result = await self.request("POST", "orders", data=payload)
        return self._extract_identifier(result)

    async def update_order(
        self,
        order_id: int,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update an existing order."""
        payload = self._merge_payload(data, **kwargs)
        return await self.request("PUT", f"orders/{order_id}", data=payload)

    async def delete_order(self, order_id: int) -> Dict[str, Any]:
        """Delete an order."""
        return await self.request("DELETE", f"orders/{order_id}")
    
    # ============================================================================
    # CONTACT MANAGEMENT
    # ============================================================================
    
    async def get_contacts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of contacts."""
        params = {"limit": limit}
        result = await self.request("GET", "contacts", params=params)
        return result if isinstance(result, list) else []
    
    async def get_contact_by_id(self, contact_id: int) -> Dict[str, Any]:
        """Get specific contact by ID."""
        return await self.request("GET", f"contacts/{contact_id}")
    
    async def create_contact(
        self,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new contact."""
        payload = self._merge_payload(data, **kwargs)
        result = await self.request("POST", "contacts", data=payload)
        return self._extract_identifier(result)

    async def update_contact(
        self,
        contact_id: int,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update an existing contact."""
        payload = self._merge_payload(data, **kwargs)
        return await self.request("PUT", f"contacts/{contact_id}", data=payload)

    async def delete_contact(self, contact_id: int) -> Dict[str, Any]:
        """Delete a contact."""
        return await self.request("DELETE", f"contacts/{contact_id}")
    
    # ============================================================================
    # RAW API CALL
    # ============================================================================
    
    async def dolibarr_raw_api(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make raw API call to any Dolibarr endpoint."""
        return await self.request(method, endpoint, params=params, data=data)
