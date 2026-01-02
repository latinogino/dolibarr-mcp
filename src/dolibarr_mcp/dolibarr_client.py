"""Professional Dolibarr API client with comprehensive CRUD operations."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

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


class DolibarrValidationError(DolibarrAPIError):
    """Raised for client-side validation failures before hitting the API."""


class DolibarrClient:
    """Professional Dolibarr API client with comprehensive functionality."""
    
    def __init__(self, config: Config):
        """Initialize the Dolibarr client."""
        self.config = config
        self.base_url = config.dolibarr_url.rstrip('/')
        self.api_key = config.api_key
        self.session: Optional[ClientSession] = None
        self.logger = logging.getLogger(__name__)
        self.debug_mode = getattr(config, "debug_mode", False)
        self.allow_ref_autogen = getattr(config, "allow_ref_autogen", False)
        self.ref_autogen_prefix = getattr(config, "ref_autogen_prefix", "AUTO")
        self.max_retries = getattr(config, "max_retries", 2)
        self.retry_backoff_seconds = getattr(config, "retry_backoff_seconds", 0.5)
        
        # Configure timeout
        self.timeout = ClientTimeout(total=30, connect=10)
        self.logger.setLevel(config.log_level)
    
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

    def _mask_api_key(self) -> str:
        """Return a masked representation of the API key for logging."""
        if not self.api_key:
            return "<not-set>"
        if len(self.api_key) <= 6:
            return "*" * len(self.api_key)
        return f"{self.api_key[:2]}***{self.api_key[-2:]}"

    @staticmethod
    def _now_iso() -> str:
        """Return current UTC timestamp in ISO format with Z suffix."""
        return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    @staticmethod
    def _generate_correlation_id() -> str:
        """Create a unique correlation identifier."""
        return str(uuid4())

    def _build_validation_error(
        self,
        endpoint: str,
        missing_fields: Optional[List[str]] = None,
        invalid_fields: Optional[List[Dict[str, str]]] = None,
        message: str = "Validation failed",
        status: int = 400,
    ) -> Dict[str, Any]:
        """Build a structured validation error response."""
        return {
            "error": "Bad Request",
            "status": status,
            "message": message,
            "missing_fields": missing_fields or [],
            "invalid_fields": invalid_fields or [],
            "endpoint": f"/{endpoint.lstrip('/')}",
            "timestamp": self._now_iso(),
        }

    def _build_internal_error(self, endpoint: str, message: str, correlation_id: str) -> Dict[str, Any]:
        """Build a structured internal server error response."""
        return {
            "error": "Internal Server Error",
            "status": 500,
            "message": message,
            "correlation_id": correlation_id,
            "endpoint": f"/{endpoint.lstrip('/')}",
            "timestamp": self._now_iso(),
        }

    def _apply_aliases(self, payload: Dict[str, Any], aliases: Dict[str, List[str]]) -> None:
        """Promote alias fields to canonical names."""
        for target, options in aliases.items():
            if target not in payload:
                for alias in options:
                    if alias in payload and payload[alias] not in (None, ""):
                        payload[target] = payload.pop(alias)
                        break

    def _validate_payload(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        required_fields: List[str],
        aliases: Optional[Dict[str, List[str]]] = None,
        numeric_positive: Optional[List[str]] = None,
        enum_fields: Optional[Dict[str, List[Any]]] = None,
    ) -> Dict[str, Any]:
        """Validate payload before sending to Dolibarr and optionally auto-generate refs."""
        aliases = aliases or {}
        numeric_positive = numeric_positive or []
        enum_fields = enum_fields or {}

        self._apply_aliases(payload, aliases)

        missing_fields = [
            field
            for field in required_fields
            if field not in payload or payload[field] in (None, "")
        ]

        invalid_fields: List[Dict[str, str]] = []

        for field in numeric_positive:
            if field in payload and isinstance(payload[field], (int, float)) and payload[field] < 0:
                invalid_fields.append({"field": field, "message": "must be a positive number"})

        for field, values in enum_fields.items():
            if field in payload and payload[field] not in values:
                invalid_fields.append({"field": field, "message": f"must be one of {values}"})

        if "ref" in missing_fields and self.allow_ref_autogen:
            payload["ref"] = f"{self.ref_autogen_prefix}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            missing_fields = [f for f in missing_fields if f != "ref"]

        if missing_fields or invalid_fields:
            error_data = self._build_validation_error(
                endpoint=endpoint,
                missing_fields=missing_fields,
                invalid_fields=invalid_fields,
            )
            raise DolibarrValidationError(
                message=error_data["message"],
                status_code=error_data["status"],
                response_data=error_data,
            )

        return payload

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
        
        last_exception: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                if self.debug_mode:
                    self.logger.debug(
                        "Making %s request to %s with params=%s payload_keys=%s api_key=%s",
                        method,
                        url,
                        params or {},
                        list((data or {}).keys()),
                        self._mask_api_key(),
                    )
                
                kwargs = {
                    "params": params or {},
                }
                
                if data and method.upper() in ["POST", "PUT"]:
                    kwargs["json"] = data
                
                async with self.session.request(method, url, **kwargs) as response:
                    response_text = await response.text()
                    
                    # Log response for debugging without leaking secrets
                    if self.debug_mode:
                        self.logger.debug("Response status: %s", response.status)
                        self.logger.debug("Response body (truncated): %s", response_text[:500])
                    
                    # Try to parse JSON response
                    try:
                        response_data = json.loads(response_text) if response_text else {}
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    
                    # Handle error responses
                    if response.status >= 400:
                        if response.status == 400:
                            missing = []
                            invalid: List[Dict[str, str]] = []
                            if isinstance(response_data, dict):
                                if "missing_fields" in response_data:
                                    missing = response_data.get("missing_fields") or []
                                if "invalid_fields" in response_data:
                                    invalid = response_data.get("invalid_fields") or []
                                # Heuristic: derive missing ref from message
                                if not missing and isinstance(response_data.get("error"), str):
                                    if "ref" in response_data.get("error").lower():
                                        missing.append("ref")
                                if not missing and "message" in response_data and "ref" in str(response_data["message"]).lower():
                                    missing.append("ref")
                            error_data = self._build_validation_error(
                                endpoint=endpoint,
                                missing_fields=missing,
                                invalid_fields=invalid,
                                message="Validation failed",
                            )
                            raise DolibarrValidationError(
                                message=error_data["message"],
                                status_code=400,
                                response_data=error_data,
                            )

                        if response.status >= 500:
                            correlation_id = self._generate_correlation_id()
                            internal_error = self._build_internal_error(
                                endpoint=endpoint,
                                message=response_data.get("message", f"An unexpected error occurred while processing {endpoint}"),
                                correlation_id=correlation_id,
                            )
                            self.logger.error(
                                "Server error %s for %s (correlation_id=%s): %s",
                                response.status,
                                endpoint,
                                correlation_id,
                                response_text[:500],
                            )
                            raise DolibarrAPIError(
                                message=internal_error["message"],
                                status_code=response.status,
                                response_data=internal_error,
                            )

                        error_msg = f"HTTP {response.status}: {response.reason}"
                        if isinstance(response_data, dict):
                            if "message" in response_data:
                                error_msg = response_data["message"]
                            elif "error" in response_data and isinstance(response_data["error"], str):
                                error_msg = response_data["error"]
                        raise DolibarrAPIError(
                            message=error_msg,
                            status_code=response.status,
                            response_data=response_data,
                        )
                    
                    return response_data
                    
            except aiohttp.ClientError as e:
                last_exception = e
                if endpoint == "status" and not url.endswith("/api/status"):
                    try:
                        alt_url = f"{self.base_url}/setup/modules"
                        self.logger.debug(f"Status failed, trying alternative: {alt_url}")
                        
                        async with self.session.get(alt_url) as response:
                            if response.status == 200:
                                return {
                                    "success": 1,
                                    "dolibarr_version": "API Available",
                                    "api_version": "1.0"
                                }
                    except Exception as alt_exc:  # pylint: disable=broad-except
                        last_exception = alt_exc

                if attempt < self.max_retries and isinstance(e, aiohttp.ClientResponseError) and e.status in {502, 503, 504}:
                    backoff = self.retry_backoff_seconds * (2 ** attempt)
                    await asyncio.sleep(backoff)
                    continue
                break
            except DolibarrAPIError:
                raise
            except Exception as e:  # pylint: disable=broad-except
                last_exception = e
                break

        if isinstance(last_exception, DolibarrAPIError):
            raise last_exception

        if isinstance(last_exception, Exception):
            correlation_id = self._generate_correlation_id()
            internal_error = self._build_internal_error(
                endpoint=endpoint,
                message=str(last_exception),
                correlation_id=correlation_id,
            )
            self.logger.error(
                "Unexpected error during %s %s (correlation_id=%s): %s",
                method,
                endpoint,
                correlation_id,
                last_exception,
            )
            raise DolibarrAPIError(
                message=internal_error["message"],
                status_code=500,
                response_data=internal_error,
            ) from last_exception

        raise DolibarrAPIError(f"HTTP client error: {endpoint}")
    
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
    
    async def search_customers(self, sqlfilters: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search customers using SQL filters."""
        params = {"limit": limit, "sqlfilters": sqlfilters}
        result = await self.request("GET", "thirdparties", params=params)
        return result if isinstance(result, list) else []

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
    
    async def search_products(self, sqlfilters: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search products using SQL filters."""
        params = {"limit": limit, "sqlfilters": sqlfilters}
        result = await self.request("GET", "products", params=params)
        return result if isinstance(result, list) else []

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
        payload = self._validate_payload(
            endpoint="products",
            payload=payload,
            required_fields=["ref", "label", "type", "price"],
            aliases={"label": ["name"]},
            numeric_positive=["price"],
            enum_fields={"type": ["product", "service", 0, 1]},
        )
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

        # Fix: Map customer_id to socid
        if "customer_id" in payload and "socid" not in payload:
            payload["socid"] = payload.pop("customer_id")

        # Fix: Map product_id to fk_product in lines
        if "lines" in payload and isinstance(payload["lines"], list):
            for line in payload["lines"]:
                if "product_id" in line:
                    line["fk_product"] = line.pop("product_id")
                # Ensure product_type is passed if present (0=Product, 1=Service)
                if "product_type" in line:
                    line["product_type"] = line["product_type"]

        payload = self._validate_payload(
            endpoint="invoices",
            payload=payload,
            required_fields=["socid"],
        )

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

    async def add_invoice_line(
        self,
        invoice_id: int,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Add a line to an invoice."""
        payload = self._merge_payload(data, **kwargs)
        
        # Map product_id to fk_product if present
        if "product_id" in payload:
            payload["fk_product"] = payload.pop("product_id")
            
        return await self.request("POST", f"invoices/{invoice_id}/lines", data=payload)

    async def update_invoice_line(
        self,
        invoice_id: int,
        line_id: int,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update a line in an invoice."""
        payload = self._merge_payload(data, **kwargs)
        return await self.request("PUT", f"invoices/{invoice_id}/lines/{line_id}", data=payload)

    async def delete_invoice_line(self, invoice_id: int, line_id: int) -> Dict[str, Any]:
        """Delete a line from an invoice."""
        return await self.request("DELETE", f"invoices/{invoice_id}/lines/{line_id}")

    async def validate_invoice(self, invoice_id: int, warehouse_id: int = 0, not_trigger: int = 0) -> Dict[str, Any]:
        """Validate an invoice."""
        payload = {
            "idwarehouse": warehouse_id,
            "not_trigger": not_trigger
        }
        return await self.request("POST", f"invoices/{invoice_id}/validate", data=payload)
    
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
    # PROJECT MANAGEMENT
    # ============================================================================
    
    async def get_projects(self, limit: int = 100, page: int = 1, status: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of projects."""
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if status is not None:
            params["status"] = status
        result = await self.request("GET", "projects", params=params)
        return result if isinstance(result, list) else []

    async def get_project_by_id(self, project_id: int) -> Dict[str, Any]:
        """Get specific project by ID."""
        return await self.request("GET", f"projects/{project_id}")

    async def search_projects(self, sqlfilters: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search projects using SQL filters."""
        params = {"limit": limit, "sqlfilters": sqlfilters}
        result = await self.request("GET", "projects", params=params)
        return result if isinstance(result, list) else []

    async def create_project(self, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Create a new project."""
        payload = self._merge_payload(data, **kwargs)
        payload = self._validate_payload(
            endpoint="projects",
            payload=payload,
            required_fields=["ref", "name", "socid"],
            aliases={"name": ["title"]},
        )
        result = await self.request("POST", "projects", data=payload)
        return self._extract_identifier(result)

    async def update_project(self, project_id: int, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Update an existing project."""
        payload = self._merge_payload(data, **kwargs)
        return await self.request("PUT", f"projects/{project_id}", data=payload)

    async def delete_project(self, project_id: int) -> Dict[str, Any]:
        """Delete a project."""
        return await self.request("DELETE", f"projects/{project_id}")

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
