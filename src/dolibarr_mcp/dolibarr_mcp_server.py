"""Professional Dolibarr MCP Server with comprehensive CRUD operations."""

import asyncio
import json
import sys
import os
import logging
from contextlib import asynccontextmanager

# Import MCP components
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import our Dolibarr components
from .config import Config
from .dolibarr_client import DolibarrClient, DolibarrAPIError


# Configure logging to stderr so it doesn't interfere with MCP protocol
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise in MCP communication
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

# Create server instance
server = Server("dolibarr-mcp")


def _escape_sqlfilter(value: str) -> str:
    """Escape single quotes for SQL filters."""
    return value.replace("'", "''")


@server.list_tools()
async def handle_list_tools():
    """List all available tools."""
    return [
        # System & Info
        Tool(
            name="test_connection",
            description="Test Dolibarr API connection",
            inputSchema={"type": "object", "properties": {}, "additionalProperties": False}
        ),
        Tool(
            name="get_status",
            description="Get Dolibarr system status and version information",
            inputSchema={"type": "object", "properties": {}, "additionalProperties": False}
        ),

        # Search Tools
        Tool(
            name="search_products_by_ref",
            description="Search products by reference prefix (e.g. 'PRJ-123')",
            inputSchema={
                "type": "object",
                "properties": {
                    "ref_prefix": {"type": "string", "description": "Prefix of the product reference"},
                    "limit": {"type": "integer", "description": "Maximum number of results", "default": 20}
                },
                "required": ["ref_prefix"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="search_customers",
            description="Search customers by name or alias",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term for name or alias"},
                    "limit": {"type": "integer", "description": "Maximum number of results", "default": 20}
                },
                "required": ["query"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="search_products_by_label",
            description="Search products by label/description",
            inputSchema={
                "type": "object",
                "properties": {
                    "label_search": {"type": "string", "description": "Search term in product label"},
                    "limit": {"type": "integer", "description": "Maximum number of results", "default": 20}
                },
                "required": ["label_search"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="resolve_product_ref",
            description="Find exactly one product by reference. Returns status 'ok', 'not_found', or 'ambiguous'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ref": {"type": "string", "description": "Exact product reference"}
                },
                "required": ["ref"],
                "additionalProperties": False
            }
        ),
        
        # User Management CRUD
        Tool(
            name="get_users",
            description="Get list of users from Dolibarr",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of users to return (default: 100)", "default": 100},
                    "page": {"type": "integer", "description": "Page number for pagination (default: 1)", "default": 1}
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_user_by_id",
            description="Get specific user details by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "User ID to retrieve"}
                },
                "required": ["user_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="create_user",
            description="Create a new user",
            inputSchema={
                "type": "object",
                "properties": {
                    "login": {"type": "string", "description": "User login"},
                    "lastname": {"type": "string", "description": "Last name"},
                    "firstname": {"type": "string", "description": "First name"},
                    "email": {"type": "string", "description": "Email address"},
                    "password": {"type": "string", "description": "Password"},
                    "admin": {"type": "integer", "description": "Admin level (0=No, 1=Yes)", "default": 0}
                },
                "required": ["login", "lastname"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="update_user",
            description="Update an existing user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "User ID to update"},
                    "login": {"type": "string", "description": "User login"},
                    "lastname": {"type": "string", "description": "Last name"},
                    "firstname": {"type": "string", "description": "First name"},
                    "email": {"type": "string", "description": "Email address"},
                    "admin": {"type": "integer", "description": "Admin level (0=No, 1=Yes)"}
                },
                "required": ["user_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="delete_user",
            description="Delete a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "User ID to delete"}
                },
                "required": ["user_id"],
                "additionalProperties": False
            }
        ),
        
        # Customer/Third Party Management CRUD
        Tool(
            name="get_customers",
            description="Get list of customers/third parties from Dolibarr",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of customers to return (default: 100)", "default": 100},
                    "page": {"type": "integer", "description": "Page number for pagination (default: 1)", "default": 1}
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_customer_by_id",
            description="Get specific customer details by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer", "description": "Customer ID to retrieve"}
                },
                "required": ["customer_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="create_customer",
            description="Create a new customer/third party",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer name"},
                    "email": {"type": "string", "description": "Email address"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "address": {"type": "string", "description": "Customer address"},
                    "town": {"type": "string", "description": "City/Town"},
                    "zip": {"type": "string", "description": "Postal code"},
                    "country_id": {"type": "integer", "description": "Country ID (default: 1)", "default": 1},
                    "type": {"type": "integer", "description": "Customer type (1=Customer, 2=Supplier, 3=Both)", "default": 1},
                    "status": {"type": "integer", "description": "Status (1=Active, 0=Inactive)", "default": 1}
                },
                "required": ["name"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="update_customer",
            description="Update an existing customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer", "description": "Customer ID to update"},
                    "name": {"type": "string", "description": "Customer name"},
                    "email": {"type": "string", "description": "Email address"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "address": {"type": "string", "description": "Customer address"},
                    "town": {"type": "string", "description": "City/Town"},
                    "zip": {"type": "string", "description": "Postal code"},
                    "status": {"type": "integer", "description": "Status (1=Active, 0=Inactive)"}
                },
                "required": ["customer_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="delete_customer",
            description="Delete a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer", "description": "Customer ID to delete"}
                },
                "required": ["customer_id"],
                "additionalProperties": False
            }
        ),
        
        # Product Management CRUD
        Tool(
            name="get_products",
            description="Get list of products from Dolibarr",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of products to return (default: 100)", "default": 100}
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_product_by_id",
            description="Get specific product details by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "Product ID to retrieve"}
                },
                "required": ["product_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="create_product",
            description="Create a new product",
            inputSchema={
                "type": "object",
                "properties": {
                    "label": {"type": "string", "description": "Product name/label"},
                    "price": {"type": "number", "description": "Product price"},
                    "description": {"type": "string", "description": "Product description"},
                    "stock": {"type": "integer", "description": "Initial stock quantity"}
                },
                "required": ["label", "price"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="update_product",
            description="Update an existing product",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "Product ID to update"},
                    "label": {"type": "string", "description": "Product name/label"},
                    "price": {"type": "number", "description": "Product price"},
                    "description": {"type": "string", "description": "Product description"}
                },
                "required": ["product_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="delete_product",
            description="Delete a product",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "Product ID to delete"}
                },
                "required": ["product_id"],
                "additionalProperties": False
            }
        ),
        
        # Invoice Management CRUD
        Tool(
            name="get_invoices",
            description="Get list of invoices from Dolibarr",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of invoices to return (default: 100)", "default": 100},
                    "status": {"type": "string", "description": "Invoice status filter (draft, unpaid, paid, etc.)"}
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_invoice_by_id",
            description="Get specific invoice details by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "integer", "description": "Invoice ID to retrieve"}
                },
                "required": ["invoice_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="create_invoice",
            description="Create a new invoice",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer", "description": "Customer ID (socid)"},
                    "date": {"type": "string", "description": "Invoice date (YYYY-MM-DD)"},
                    "due_date": {"type": "string", "description": "Due date (YYYY-MM-DD)"},
                    "lines": {
                        "type": "array",
                        "description": "Invoice lines",
                        "items": {
                            "type": "object",
                            "properties": {
                                "desc": {"type": "string", "description": "Line description"},
                                "qty": {"type": "number", "description": "Quantity"},
                                "subprice": {"type": "number", "description": "Unit price"},
                                "total_ht": {"type": "number", "description": "Total excluding tax"},
                                "total_ttc": {"type": "number", "description": "Total including tax"},
                                "vat": {"type": "number", "description": "VAT rate"},
                                "product_id": {"type": "integer", "description": "Product ID to link (optional)"},
                                "product_type": {"type": "integer", "description": "Type of line (0=Product, 1=Service)"}
                            },
                            "required": ["desc", "qty", "subprice"]
                        }
                    }
                },
                "required": ["customer_id", "lines"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="update_invoice",
            description="Update an existing invoice",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "integer", "description": "Invoice ID to update"},
                    "date": {"type": "string", "description": "Invoice date (YYYY-MM-DD)"},
                    "due_date": {"type": "string", "description": "Due date (YYYY-MM-DD)"}
                },
                "required": ["invoice_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="delete_invoice",
            description="Delete an invoice",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "integer", "description": "Invoice ID to delete"}
                },
                "required": ["invoice_id"],
                "additionalProperties": False
            }
        ),
        
        # Order Management CRUD  
        Tool(
            name="get_orders",
            description="Get list of orders from Dolibarr",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of orders to return (default: 100)", "default": 100},
                    "status": {"type": "string", "description": "Order status filter"}
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_order_by_id",
            description="Get specific order details by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer", "description": "Order ID to retrieve"}
                },
                "required": ["order_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="create_order",
            description="Create a new order",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer", "description": "Customer ID (socid)"},
                    "date": {"type": "string", "description": "Order date (YYYY-MM-DD)"}
                },
                "required": ["customer_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="update_order",
            description="Update an existing order",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer", "description": "Order ID to update"},
                    "date": {"type": "string", "description": "Order date (YYYY-MM-DD)"}
                },
                "required": ["order_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="delete_order",
            description="Delete an order",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer", "description": "Order ID to delete"}
                },
                "required": ["order_id"],
                "additionalProperties": False
            }
        ),
        
        # Contact Management CRUD
        Tool(
            name="get_contacts",
            description="Get list of contacts from Dolibarr",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of contacts to return (default: 100)", "default": 100}
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_contact_by_id",
            description="Get specific contact details by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "contact_id": {"type": "integer", "description": "Contact ID to retrieve"}
                },
                "required": ["contact_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="create_contact",
            description="Create a new contact",
            inputSchema={
                "type": "object",
                "properties": {
                    "firstname": {"type": "string", "description": "First name"},
                    "lastname": {"type": "string", "description": "Last name"},
                    "email": {"type": "string", "description": "Email address"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "socid": {"type": "integer", "description": "Associated company ID"}
                },
                "required": ["firstname", "lastname"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="update_contact",
            description="Update an existing contact",
            inputSchema={
                "type": "object",
                "properties": {
                    "contact_id": {"type": "integer", "description": "Contact ID to update"},
                    "firstname": {"type": "string", "description": "First name"},
                    "lastname": {"type": "string", "description": "Last name"},
                    "email": {"type": "string", "description": "Email address"},
                    "phone": {"type": "string", "description": "Phone number"}
                },
                "required": ["contact_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="delete_contact",
            description="Delete a contact",
            inputSchema={
                "type": "object",
                "properties": {
                    "contact_id": {"type": "integer", "description": "Contact ID to delete"}
                },
                "required": ["contact_id"],
                "additionalProperties": False
            }
        ),

        # Project Management CRUD
        Tool(
            name="get_projects",
            description="Get list of projects from Dolibarr",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of projects to return (default: 100)", "default": 100},
                    "page": {"type": "integer", "description": "Page number for pagination (default: 1)", "default": 1},
                    "status": {"type": "integer", "description": "Project status filter (e.g. 0=draft, 1=open, 2=closed)", "default": 1}
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="get_project_by_id",
            description="Get specific project details by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "Project ID to retrieve"}
                },
                "required": ["project_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="search_projects",
            description="Search projects by reference or title",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term for project ref or title"},
                    "limit": {"type": "integer", "description": "Maximum number of results", "default": 20}
                },
                "required": ["query"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="create_project",
            description="Create a new project",
            inputSchema={
                "type": "object",
                "properties": {
                    "ref": {"type": "string", "description": "Project reference (optional, if Dolibarr auto-generates)"},
                    "title": {"type": "string", "description": "Project title"},
                    "description": {"type": "string", "description": "Project description"},
                    "socid": {"type": "integer", "description": "Linked customer ID (thirdparty)"},
                    "status": {"type": "integer", "description": "Project status (e.g. 1=open)", "default": 1}
                },
                "required": ["title"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="update_project",
            description="Update an existing project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "Project ID to update"},
                    "title": {"type": "string", "description": "Project title"},
                    "description": {"type": "string", "description": "Project description"},
                    "status": {"type": "integer", "description": "Project status"}
                },
                "required": ["project_id"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="delete_project",
            description="Delete a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "Project ID to delete"}
                },
                "required": ["project_id"],
                "additionalProperties": False
            }
        ),
        
        # Raw API Access
        Tool(
            name="dolibarr_raw_api",
            description="Make raw API call to any Dolibarr endpoint",
            inputSchema={
                "type": "object",
                "properties": {
                    "method": {"type": "string", "description": "HTTP method", "enum": ["GET", "POST", "PUT", "DELETE"]},
                    "endpoint": {"type": "string", "description": "API endpoint (e.g., /thirdparties, /invoices)"},
                    "params": {"type": "object", "description": "Query parameters"},
                    "data": {"type": "object", "description": "Request payload for POST/PUT requests"}
                },
                "required": ["method", "endpoint"],
                "additionalProperties": False
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Handle all tool calls using the DolibarrClient."""
    
    try:
        # Initialize the config and client
        config = Config()
        
        async with DolibarrClient(config) as client:
            
            # System & Info
            if name == "test_connection":
                result = await client.get_status()
                if 'success' not in result:
                    result = {"status": "success", "message": "API connection working", "data": result}
            
            elif name == "get_status":
                result = await client.get_status()
            
            # Search Tools
            elif name == "search_products_by_ref":
                ref_prefix = _escape_sqlfilter(arguments['ref_prefix'])
                limit = arguments.get('limit', 20)
                sqlfilters = f"(t.ref:like:'{ref_prefix}%')"
                result = await client.search_products(sqlfilters=sqlfilters, limit=limit)

            elif name == "search_customers":
                query = _escape_sqlfilter(arguments['query'])
                limit = arguments.get('limit', 20)
                sqlfilters = f"((t.nom:like:'%{query}%') OR (t.name_alias:like:'%{query}%'))"
                result = await client.search_customers(sqlfilters=sqlfilters, limit=limit)

            elif name == "search_products_by_label":
                label_search = _escape_sqlfilter(arguments['label_search'])
                limit = arguments.get('limit', 20)
                sqlfilters = f"(t.label:like:'%{label_search}%')"
                result = await client.search_products(sqlfilters=sqlfilters, limit=limit)

            elif name == "resolve_product_ref":
                ref = arguments['ref']
                ref_esc = _escape_sqlfilter(ref)
                sqlfilters = f"(t.ref:like:'{ref_esc}')"
                products = await client.search_products(sqlfilters=sqlfilters, limit=2)
                
                if not products:
                    result = {"status": "not_found", "message": f"Product with ref '{ref}' not found"}
                elif len(products) == 1:
                    result = {"status": "ok", "product": products[0]}
                else:
                    # Check if one is exact match
                    exact_matches = [p for p in products if p.get('ref') == ref]
                    if len(exact_matches) == 1:
                        result = {"status": "ok", "product": exact_matches[0]}
                    else:
                        result = {"status": "ambiguous", "message": f"Multiple products found for ref '{ref}'", "products": products}

            # User Management
            elif name == "get_users":
                result = await client.get_users(
                    limit=arguments.get('limit', 100),
                    page=arguments.get('page', 1)
                )
            
            elif name == "get_user_by_id":
                result = await client.get_user_by_id(arguments['user_id'])
            
            elif name == "create_user":
                result = await client.create_user(**arguments)
            
            elif name == "update_user":
                user_id = arguments.pop('user_id')
                result = await client.update_user(user_id, **arguments)
            
            elif name == "delete_user":
                result = await client.delete_user(arguments['user_id'])
            
            # Customer Management
            elif name == "get_customers":
                result = await client.get_customers(
                    limit=arguments.get('limit', 100),
                    page=arguments.get('page', 1)
                )
            
            elif name == "get_customer_by_id":
                result = await client.get_customer_by_id(arguments['customer_id'])
            
            elif name == "create_customer":
                result = await client.create_customer(**arguments)
            
            elif name == "update_customer":
                customer_id = arguments.pop('customer_id')
                result = await client.update_customer(customer_id, **arguments)
            
            elif name == "delete_customer":
                result = await client.delete_customer(arguments['customer_id'])
            
            # Product Management
            elif name == "get_products":
                result = await client.get_products(limit=arguments.get('limit', 100))
            
            elif name == "get_product_by_id":
                result = await client.get_product_by_id(arguments['product_id'])
            
            elif name == "create_product":
                result = await client.create_product(**arguments)
            
            elif name == "update_product":
                product_id = arguments.pop('product_id')
                result = await client.update_product(product_id, **arguments)
            
            elif name == "delete_product":
                result = await client.delete_product(arguments['product_id'])
            
            # Invoice Management
            elif name == "get_invoices":
                result = await client.get_invoices(
                    limit=arguments.get('limit', 100),
                    status=arguments.get('status')
                )
            
            elif name == "get_invoice_by_id":
                result = await client.get_invoice_by_id(arguments['invoice_id'])
            
            elif name == "create_invoice":
                result = await client.create_invoice(**arguments)
            
            elif name == "update_invoice":
                invoice_id = arguments.pop('invoice_id')
                result = await client.update_invoice(invoice_id, **arguments)
            
            elif name == "delete_invoice":
                result = await client.delete_invoice(arguments['invoice_id'])
            
            # Order Management
            elif name == "get_orders":
                result = await client.get_orders(
                    limit=arguments.get('limit', 100),
                    status=arguments.get('status')
                )
            
            elif name == "get_order_by_id":
                result = await client.get_order_by_id(arguments['order_id'])
            
            elif name == "create_order":
                result = await client.create_order(**arguments)
            
            elif name == "update_order":
                order_id = arguments.pop('order_id')
                result = await client.update_order(order_id, **arguments)
            
            elif name == "delete_order":
                result = await client.delete_order(arguments['order_id'])
            
            # Contact Management
            elif name == "get_contacts":
                result = await client.get_contacts(limit=arguments.get('limit', 100))
            
            elif name == "get_contact_by_id":
                result = await client.get_contact_by_id(arguments['contact_id'])
            
            elif name == "create_contact":
                result = await client.create_contact(**arguments)
            
            elif name == "update_contact":
                contact_id = arguments.pop('contact_id')
                result = await client.update_contact(contact_id, **arguments)
            
            elif name == "delete_contact":
                result = await client.delete_contact(arguments['contact_id'])
            
            # Project Management
            elif name == "get_projects":
                result = await client.get_projects(
                    limit=arguments.get("limit", 100),
                    page=arguments.get("page", 1),
                    status=arguments.get("status")
                )

            elif name == "get_project_by_id":
                result = await client.get_project_by_id(arguments["project_id"])

            elif name == "search_projects":
                query = _escape_sqlfilter(arguments["query"])
                limit = arguments.get("limit", 20)
                sqlfilters = f"((t.ref:like:'%{query}%') OR (t.title:like:'%{query}%'))"
                result = await client.search_projects(sqlfilters=sqlfilters, limit=limit)

            elif name == "create_project":
                result = await client.create_project(**arguments)

            elif name == "update_project":
                project_id = arguments.pop("project_id")
                result = await client.update_project(project_id, **arguments)

            elif name == "delete_project":
                result = await client.delete_project(arguments["project_id"])

            # Raw API Access
            elif name == "dolibarr_raw_api":
                result = await client.dolibarr_raw_api(**arguments)
            
            else:
                result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except DolibarrAPIError as e:
        error_result = {"error": f"Dolibarr API Error: {str(e)}", "type": "api_error"}
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    except Exception as e:
        error_result = {"error": f"Tool execution failed: {str(e)}", "type": "internal_error"}
        print(f"🔥 Tool execution error: {e}", file=sys.stderr)  # Debug logging
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


@asynccontextmanager
async def test_api_connection():
    """Test API connection and yield client if successful."""
    config = None
    try:
        config = Config()
        
        # Check if environment variables are set
        if not config.dolibarr_url or config.dolibarr_url == "https://your-dolibarr-instance.com/api/index.php":
            print("⚠️  Warning: DOLIBARR_URL not configured in .env file", file=sys.stderr)
            print("⚠️  Using placeholder URL - API calls will fail", file=sys.stderr)
            print("📝 Please configure your .env file with valid Dolibarr credentials", file=sys.stderr)
            yield True  # Allow server to start anyway
            return
            
        if not config.api_key or config.api_key == "your_dolibarr_api_key_here":
            print("⚠️  Warning: DOLIBARR_API_KEY not configured in .env file", file=sys.stderr)
            print("⚠️  API authentication will fail", file=sys.stderr)
            print("📝 Please configure your .env file with valid Dolibarr credentials", file=sys.stderr)
            yield True  # Allow server to start anyway
            return
        
        async with DolibarrClient(config) as client:
            print("🧪 Testing Dolibarr API connection...", file=sys.stderr)
            result = await client.get_status()
            if 'success' in result or 'dolibarr_version' in str(result):
                print("✅ Dolibarr API connection successful", file=sys.stderr)
                print("🎯 Full CRUD operations available for all Dolibarr modules", file=sys.stderr)
                yield True
            else:
                print(f"⚠️  API test returned unexpected result: {result}", file=sys.stderr)
                print("⚠️  Server will start but API calls may fail", file=sys.stderr)
                yield True  # Allow server to start anyway
    except Exception as e:
        print(f"⚠️  API test error: {e}", file=sys.stderr)
        if config is None:
            print("💡 Check your .env file configuration", file=sys.stderr)
        print("⚠️  Server will start but API calls may fail", file=sys.stderr)
        yield True  # Allow server to start anyway


async def main():
    """Run the Dolibarr MCP server."""
    
    # Test API connection but don't fail if it's not working
    async with test_api_connection() as api_ok:
        if not api_ok:
            print("⚠️  Starting server without valid API connection", file=sys.stderr)
            print("📝 Configure your .env file to enable API functionality", file=sys.stderr)
        else:
            print("✅ API connection validated", file=sys.stderr)
    
    # Run server regardless of API status
    print("🚀 Starting Professional Dolibarr MCP server...", file=sys.stderr)
    print("✅ Server ready with comprehensive ERP management capabilities", file=sys.stderr)
    print("📝 Tools will attempt to connect when called", file=sys.stderr)
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="dolibarr-mcp",
                    server_version="1.0.1",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        print(f"💥 Server error: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server startup error: {e}", file=sys.stderr)
        sys.exit(1)
