# Dolibarr API Coverage

This server wraps the Dolibarr REST API v21.0.1 that is exposed by an instance at
`https://db.ginos.cloud/api/index.php`. The MCP tools use the following REST
resources, mirroring the scope that the sibling `prestashop-mcp` project
implements for PrestaShop.

## Authentication and Conventions

- **Header** – send the `DOLAPIKEY` header with the personal access token that is
  configured for your Dolibarr user.
- **Content Type** – every request uses `application/json` payloads and
  responses.
- **Pagination** – list endpoints accept the `limit`, `sortfield`, `sortorder`
  and `sqlfilters` query parameters.
- **Identifiers** – Dolibarr returns both `id` (numeric) and `ref` (business
  reference) for most entities. The MCP tools expose both values to the client.

## Supported Resources

| Resource        | Endpoint(s)                 | Tool group                              |
| --------------- | --------------------------- | --------------------------------------- |
| Status          | `GET /status`               | `get_status`, `test_connection`         |
| Search          | `/products`, `/thirdparties`| `search_products_by_ref`, `search_customers`, `resolve_product_ref` |
| Users           | `/users`                    | CRUD helpers under the *Users* group    |
| Third parties   | `/thirdparties`             | Customer CRUD operations                |
| Products        | `/products`                 | Product CRUD operations                 |
| Invoices        | `/invoices`                 | Invoice CRUD operations                 |
| Orders          | `/orders`                   | Order CRUD operations                   |
| Projects        | `/projects`                 | Project CRUD operations & Search        |
| Contacts        | `/contacts`                 | Contact CRUD operations                 |
| Raw passthrough | Any relative path           | `dolibarr_raw_api` tool for quick tests |

Every endpoint supports create, read, update and delete operations unless noted
otherwise. The Dolibarr instance that informed this reference currently contains
live data for users, third parties and contacts; other modules respond with
empty lists until records are created.

## Response Examples

### Status

```json
{
  "success": {
    "code": 200,
    "dolibarr_version": "21.0.1",
    "access_locked": "0"
  }
}
```

### Third Party

```json
{
  "id": "1",
  "ref": "1",
  "name": "Test Customer MCP",
  "status": "1",
  "address": "123 Test Street",
  "zip": "12345",
  "town": "Test City",
  "email": "test@mcp-dolibarr.com",
  "phone": "+1-555-0123",
  "date_creation": 1752005684,
  "user_creation_id": "4",
  "array_options": {}
}
```

### Common Error Shape

```json
{
  "error": {
    "code": 404,
    "message": "Not found"
  }
}
```

Dolibarr communicates detailed failure information in the `error` object. The
client wrapper turns these payloads into Python exceptions with the same
metadata so MCP hosts can display friendly error messages.
