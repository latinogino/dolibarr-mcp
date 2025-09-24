"""Ultra-simple Dolibarr API client - Windows compatible, zero compiled extensions."""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union

# Only use standard library + requests (pure Python)
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Minimal config handling without pydantic
class SimpleConfig:
    """Simple configuration without pydantic - no compiled extensions."""
    
    def __init__(self):
        # Load .env manually
        self.load_env()
        
        self.dolibarr_url = os.getenv("DOLIBARR_URL", "")
        self.api_key = os.getenv("DOLIBARR_API_KEY", "")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Validate and fix URL
        if not self.dolibarr_url or "your-dolibarr-instance" in self.dolibarr_url:
            print("⚠️  DOLIBARR_URL not configured in .env file", file=sys.stderr)
            self.dolibarr_url = "https://your-dolibarr-instance.com/api/index.php"
        
        if not self.api_key or "your_dolibarr_api_key" in self.api_key:
            print("⚠️  DOLIBARR_API_KEY not configured in .env file", file=sys.stderr)
            self.api_key = "placeholder_api_key"
        
        # Ensure URL format
        if self.dolibarr_url and not self.dolibarr_url.endswith('/api/index.php'):
            if '/api' not in self.dolibarr_url:
                self.dolibarr_url = self.dolibarr_url.rstrip('/') + '/api/index.php'
            elif not self.dolibarr_url.endswith('/index.php'):
                self.dolibarr_url = self.dolibarr_url.rstrip('/') + '/index.php'
    
    def load_env(self):
        """Load .env file manually - no python-dotenv needed."""
        env_file = '.env'
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()


class SimpleDolibarrAPIError(Exception):
    """Simple API error exception."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class SimpleDolibarrClient:
    """Ultra-simple Dolibarr client using only requests - no aiohttp, no compiled extensions."""
    
    def __init__(self, config: SimpleConfig):
        self.config = config
        self.base_url = config.dolibarr_url.rstrip('/')
        self.api_key = config.api_key
        
        # Create requests session with retries
        self.session = requests.Session()
        
        # Add retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            "DOLAPIKEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Dolibarr-MCP-Client/1.0"
        })
        
        self.logger = logging.getLogger(__name__)
    
    def _build_url(self, endpoint: str) -> str:
        """Build full API URL."""
        endpoint = endpoint.lstrip('/')
        
        # Special handling for status endpoint
        if endpoint == "status":
            base = self.base_url.replace('/index.php', '')
            return f"{base}/status"
        
        return f"{self.base_url}/{endpoint}"
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Dolibarr API."""
        url = self._build_url(endpoint)
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            kwargs = {
                "params": params or {},
                "timeout": 30
            }
            
            if data and method.upper() in ["POST", "PUT"]:
                kwargs["json"] = data
            
            response = self.session.request(method, url, **kwargs)
            
            # Log response for debugging
            self.logger.debug(f"Response status: {response.status_code}")
            
            # Handle error responses
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and "error" in error_data:
                        error_msg = str(error_data["error"])
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.reason}"
                except:
                    error_msg = f"HTTP {response.status_code}: {response.reason}"
                
                raise SimpleDolibarrAPIError(error_msg, response.status_code)
            
            # Try to parse JSON response
            try:
                return response.json()
            except:
                # If not JSON, return as text
                return {"raw_response": response.text}
        
        except requests.RequestException as e:
            # For status endpoint, try alternative
            if endpoint == "status":
                try:
                    alt_url = f"{self.base_url.replace('/api/index.php', '')}/setup/modules"
                    alt_response = self.session.get(alt_url, timeout=10)
                    if alt_response.status_code == 200:
                        return {
                            "success": 1,
                            "dolibarr_version": "API Available",
                            "api_version": "1.0"
                        }
                except:
                    pass
            
            raise SimpleDolibarrAPIError(f"HTTP request failed: {str(e)}")
        except Exception as e:
            raise SimpleDolibarrAPIError(f"Unexpected error: {str(e)}")
    
    # ============================================================================
    # SYSTEM ENDPOINTS
    # ============================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get API status and version information."""
        try:
            return self._make_request("GET", "status")
        except SimpleDolibarrAPIError:
            # Try alternatives
            try:
                result = self._make_request("GET", "users?limit=1")
                if result is not None:
                    return {
                        "success": 1,
                        "dolibarr_version": "API Working",
                        "api_version": "1.0"
                    }
            except:
                pass
            
            raise SimpleDolibarrAPIError("Cannot connect to Dolibarr API. Please check your configuration.")
    
    # ============================================================================
    # USER MANAGEMENT
    # ============================================================================
    
    def get_users(self, limit: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Get list of users."""
        params = {"limit": limit}
        if page > 1:
            params["page"] = page
        
        result = self._make_request("GET", "users", params=params)
        return result if isinstance(result, list) else []
    
    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """Get specific user by ID."""
        return self._make_request("GET", f"users/{user_id}")
    
    def create_user(self, **kwargs) -> Dict[str, Any]:
        """Create a new user."""
        return self._make_request("POST", "users", data=kwargs)
    
    def update_user(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing user."""
        return self._make_request("PUT", f"users/{user_id}", data=kwargs)
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Delete a user."""
        return self._make_request("DELETE", f"users/{user_id}")
    
    # ============================================================================
    # CUSTOMER MANAGEMENT
    # ============================================================================
    
    def get_customers(self, limit: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Get list of customers/third parties."""
        params = {"limit": limit}
        if page > 1:
            params["page"] = page
        
        result = self._make_request("GET", "thirdparties", params=params)
        return result if isinstance(result, list) else []
    
    def get_customer_by_id(self, customer_id: int) -> Dict[str, Any]:
        """Get specific customer by ID."""
        return self._make_request("GET", f"thirdparties/{customer_id}")
    
    def create_customer(self, name: str, **kwargs) -> Dict[str, Any]:
        """Create a new customer."""
        data = {
            "name": name,
            "status": kwargs.get("status", 1),
            "client": 1 if kwargs.get("type", 1) in [1, 3] else 0,
            "fournisseur": 1 if kwargs.get("type", 1) in [2, 3] else 0,
            "country_id": kwargs.get("country_id", 1),
        }
        
        # Add optional fields
        for field in ["email", "phone", "address", "town", "zip"]:
            if field in kwargs:
                data[field] = kwargs[field]
        
        return self._make_request("POST", "thirdparties", data=data)
    
    def update_customer(self, customer_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing customer."""
        return self._make_request("PUT", f"thirdparties/{customer_id}", data=kwargs)
    
    def delete_customer(self, customer_id: int) -> Dict[str, Any]:
        """Delete a customer."""
        return self._make_request("DELETE", f"thirdparties/{customer_id}")
    
    # ============================================================================
    # PRODUCT MANAGEMENT
    # ============================================================================
    
    def get_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of products."""
        params = {"limit": limit}
        result = self._make_request("GET", "products", params=params)
        return result if isinstance(result, list) else []
    
    def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """Get specific product by ID."""
        return self._make_request("GET", f"products/{product_id}")
    
    def create_product(self, label: str, price: float, **kwargs) -> Dict[str, Any]:
        """Create a new product."""
        import time
        
        # Generate ref if not provided
        ref = kwargs.get("ref", f"PROD-{int(time.time())}")
        
        data = {
            "ref": ref,
            "label": label,
            "price": price,
            "price_ttc": price,
        }
        
        # Add optional fields
        for field in ["description", "stock"]:
            if field in kwargs:
                data[field] = kwargs[field]
        
        return self._make_request("POST", "products", data=data)
    
    def update_product(self, product_id: int, **kwargs) -> Dict[str, Any]:
        """Update an existing product."""
        return self._make_request("PUT", f"products/{product_id}", data=kwargs)
    
    def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Delete a product."""
        return self._make_request("DELETE", f"products/{product_id}")
    
    # ============================================================================
    # RAW API CALL
    # ============================================================================
    
    def raw_api(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make raw API call to any Dolibarr endpoint."""
        return self._make_request(method, endpoint, params=params, data=data)
    
    def close(self):
        """Close the session."""
        if self.session:
            self.session.close()
