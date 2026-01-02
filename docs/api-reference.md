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

### Structured Error Shapes

The MCP server and wrapper normalize Dolibarr errors into predictable JSON so
callers can surface actionable messages and debugging breadcrumbs.

#### Validation errors (`400`)

```json
{
  "error": "Bad Request",
  "status": 400,
  "message": "Validation failed",
  "missing_fields": ["ref", "socid"],
  "invalid_fields": [
    { "field": "price", "message": "must be a positive number" }
  ],
  "endpoint": "/api/index.php/products",
  "timestamp": "2026-01-02T12:34:56Z"
}
```

#### Unexpected errors (`500`)

```json
{
  "error": "Internal Server Error",
  "status": 500,
  "message": "An unexpected error occurred while creating project",
  "correlation_id": "abc123-uuid",
  "endpoint": "/api/index.php/projects",
  "timestamp": "2026-01-02T12:35:06Z"
}
```

#### Successful create

```json
{
  "status": 201,
  "id": 42,
  "ref": "FREELANCE_HOUR_TEST",
  "message": "Product created"
}
```

Include the `correlation_id` from a 500 response when opening support tickets
so logs can be located quickly.

### Create Endpoint Requirements & Examples

The wrapper validates payloads before sending them to Dolibarr. Required fields:

| Endpoint | Required fields | Notes |
| --- | --- | --- |
| `POST /products` | `ref`, `label`, `type`, `price` | `type` accepts `product`/`0` or `service`/`1`. |
| `POST /projects` | `ref`, `name`, `socid` | `title` is accepted as an alias for `name`. |
| `POST /invoices` | `socid` | Provide `lines` for invoice content. |
| `POST /time` (timesheets) | `ref`, `task_id`, `duration`, `fk_project` | Provide `ref` or enable auto-generation. |

#### Example: product create without `ref` (expected 400)

```bash
curl -X POST "https://dolibarr.example/api/index.php/products" \
  -H "DOLAPIKEY: <REDACTED>" \
  -H "Content-Type: application/json" \
  -d '{"label":"Freelance hourly rate test — Gino test","type":"service","price":110.00,"tva_tx":19.0}'
```

#### Example: corrected product payload

```bash
curl -X POST "https://dolibarr.example/api/index.php/products" \
  -H "DOLAPIKEY: <REDACTED>" \
  -H "Content-Type: application/json" \
  -d '{"ref":"FREELANCE_HOUR_TEST","label":"Freelance hourly rate test — Gino test","type":"service","price":110.00,"tva_tx":19.0}'
```

#### Example: project create (minimal payload)

```bash
curl -X POST "https://dolibarr.example/api/index.php/projects" \
  -H "DOLAPIKEY: <REDACTED>" \
  -H "Content-Type: application/json" \
  -d '{"ref":"PERCISION_TEST_PROJECT","name":"Percision test — Project test","socid":8}'
```

If server-side reference auto-generation is enabled, omitting `ref` results in a
predictable `AUTO_<timestamp>` reference. Otherwise, the wrapper will raise a
client-side validation error before sending the request.
