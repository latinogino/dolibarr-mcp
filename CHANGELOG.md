# Changelog

All notable changes to the Dolibarr MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-10

### Added

#### Core Infrastructure
- Professional MCP server implementation with comprehensive Dolibarr ERP integration
- Asynchronous HTTP client with proper session management and error handling
- Type-safe configuration management with Pydantic validation
- Comprehensive CLI interface with test and serve commands
- Professional project structure following Python best practices

#### API Client Features
- Full async/await architecture for high performance
- Custom `DolibarrAPIError` exception handling with detailed error information
- Automatic session management with context manager support
- Request/response logging for debugging and monitoring
- Flexible parameter handling for all API endpoints

#### MCP Server Capabilities
- Complete tool registration following MCP 1.0.0 specification
- JSON schema validation for all tool inputs and outputs
- Proper error propagation with meaningful error messages
- Structured response formatting for LLM consumption

#### Customer/Third Party Management
- `get_customers` - List customers and suppliers with pagination
- `get_customer_by_id` - Retrieve specific customer details
- `create_customer` - Create new customers with full address information
- `update_customer` - Update existing customer information
- `delete_customer` - Remove customers from the system

#### Product Management
- `get_products` - List products with inventory information
- `get_product_by_id` - Retrieve specific product details
- `create_product` - Create new products with pricing and stock
- `update_product` - Update existing product information
- `delete_product` - Remove products from catalog

#### Invoice Management
- `get_invoices` - List invoices with status filtering
- `get_invoice_by_id` - Retrieve specific invoice details
- `create_invoice` - Create new invoices with line items and calculations
- `update_invoice` - Update existing invoice information
- `delete_invoice` - Remove invoices from the system

#### Order Management
- `get_orders` - List orders with status filtering
- `get_order_by_id` - Retrieve specific order details
- `create_order` - Create new orders for customers
- `update_order` - Update existing order information
- `delete_order` - Remove orders from the system

#### Contact Management
- `get_contacts` - List contacts with company associations
- `get_contact_by_id` - Retrieve specific contact details
- `create_contact` - Create new contacts with full information
- `update_contact` - Update existing contact information
- `delete_contact` - Remove contacts from the system

#### User Management
- `get_users` - List system users with permissions
- `get_user_by_id` - Retrieve specific user details
- `create_user` - Create new system users with roles
- `update_user` - Update existing user information
- `delete_user` - Remove users from the system

#### System Tools
- `test_connection` - Test API connectivity and authentication
- `get_status` - Retrieve system status and version information
- `dolibarr_raw_api` - Direct access to any Dolibarr API endpoint

#### Documentation
- Comprehensive README with installation and usage instructions
- Professional API documentation based on live testing
- Environment configuration examples and setup guides
- Code examples for both MCP and programmatic usage

#### Development Tools
- Professional `pyproject.toml` with complete metadata
- Requirements management with pinned versions
- CLI testing commands for connection verification
- Type hints throughout the codebase for better IDE support

### Security
- API key authentication with proper header management
- Input validation using Pydantic models
- Safe error handling without credential exposure

### Performance
- Async/await throughout for non-blocking operations
- Connection pooling with aiohttp ClientSession
- Configurable timeouts for API requests
- Efficient JSON parsing and response handling

### Quality
- Comprehensive error handling with custom exception types
- Detailed logging for debugging and monitoring
- Type safety with full type hints
- Professional code structure and organization

## [Unreleased]

### Planned for 1.1.0
- Docker containerization with multi-stage builds
- Advanced filtering and search capabilities
- Performance optimization and caching
- Extended API coverage for additional Dolibarr modules

### Planned for 1.2.0
- Webhook support for real-time integrations
- Bulk operations for improved efficiency
- Enhanced error recovery and retry mechanisms
- Metrics and monitoring capabilities

### Planned for 2.0.0
- Web UI for server management
- Multi-instance support
- Plugin system for extensibility
- Advanced business intelligence features

---

## Guidelines

### Types of Changes
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

### Version Numbers
- **Major** version when making incompatible API changes
- **Minor** version when adding functionality in a backwards compatible manner
- **Patch** version when making backwards compatible bug fixes
