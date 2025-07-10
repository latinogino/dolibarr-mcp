# Dolibarr API Endpoints Reference
## Live Testing Results from db.ginos.cloud

This document contains actual API responses and detailed endpoint specifications discovered through live testing of Dolibarr v21.0.1.

## Base Configuration
- **Base URL:** `https://db.ginos.cloud/api/index.php`
- **Authentication:** `DOLAPIKEY` header
- **Content-Type:** `application/json`
- **Dolibarr Version:** 21.0.1

---

## 1. Status Endpoint

### GET /status
**Purpose:** API health check and version information

**Request:**
```bash
curl -X GET "https://db.ginos.cloud/api/index.php/status" \
  -H "DOLAPIKEY: your_api_key"
```

**Response:**
```json
{
  "success": {
    "code": 200,
    "dolibarr_version": "21.0.1",
    "access_locked": "0"
  }
}
```

---

## 2. Users Endpoint

### GET /users
**Purpose:** Retrieve users list

**Parameters:**
- `limit` (int): Number of records to return
- `sortfield` (string): Field to sort by
- `sortorder` (string): ASC or DESC

**Request:**
```bash
curl -X GET "https://db.ginos.cloud/api/index.php/users?limit=5" \
  -H "DOLAPIKEY: your_api_key"
```

**Response Example (User Object):**
```json
{
  "id": "1",
  "entity": "0",
  "ref": "1",
  "statut": "1",
  "status": "1",
  "lastname": "SuperAdmin",
  "firstname": null,
  "civility_id": null,
  "civility_code": null,
  "gender": null,
  "birth": "",
  "email": null,
  "personal_email": null,
  "admin": "1",
  "login": "admin",
  "datec": "",
  "datem": 1750000134,
  "datelastlogin": 1752054907,
  "datepreviouslogin": 1751957906,
  "iplastlogin": "87.187.51.28",
  "ippreviouslogin": "87.187.51.28",
  "office_phone": null,
  "office_fax": null,
  "user_mobile": null,
  "personal_mobile": null,
  "job": null,
  "signature": null,
  "address": null,
  "zip": null,
  "town": null,
  "employee": "1",
  "fk_user": null,
  "rights": {
    "user": {
      "user": {},
      "self": {},
      "user_advance": {},
      "self_advance": {},
      "group_advance": {}
    }
  }
}
```

---

## 3. Third Parties Endpoint (Customers/Suppliers)

### GET /thirdparties
**Purpose:** Retrieve customers and suppliers

**Parameters:**
- `limit` (int): Number of records to return
- `sortfield` (string): Field to sort by
- `sortorder` (string): ASC or DESC
- `sqlfilters` (string): Advanced filtering

**Request:**
```bash
curl -X GET "https://db.ginos.cloud/api/index.php/thirdparties?limit=5" \
  -H "DOLAPIKEY: your_api_key"
```

**Response Example (Third Party Object):**
```json
{
  "module": "societe",
  "id": "1",
  "entity": "1",
  "ref": "1",
  "status": "1",
  "name": "Test Customer MCP",
  "name_alias": "",
  "phone": "+1-555-0123",
  "phone_mobile": null,
  "fax": null,
  "email": "test@mcp-dolibarr.com",
  "url": null,
  "address": "123 Test Street",
  "zip": "12345",
  "town": "Test City",
  "country_id": null,
  "country_code": "",
  "state_id": null,
  "region_id": null,
  "date_creation": 1752005684,
  "date_modification": 1752005684,
  "user_creation_id": "4",
  "user_modification_id": "4",
  "tva_assuj": "1",
  "tva_intra": "",
  "client": "0",
  "prospect": 0,
  "fournisseur": "0",
  "code_client": null,
  "code_fournisseur": null,
  "remise_percent": 0,
  "remise_supplier_percent": "0",
  "note_public": null,
  "note_private": null,
  "idprof1": "",
  "idprof2": "",
  "idprof3": "",
  "idprof4": "",
  "idprof5": "",
  "idprof6": ""
}
```

---

## 4. Products Endpoint

### GET /products
**Purpose:** Retrieve product catalog

**Parameters:**
- `limit` (int): Number of records to return
- `sortfield` (string): Field to sort by
- `sortorder` (string): ASC or DESC

**Request:**
```bash
curl -X GET "https://db.ginos.cloud/api/index.php/products?limit=5" \
  -H "DOLAPIKEY: your_api_key"
```

**Response:**
```json
[]
```
*Note: Currently empty in test instance*

---

## 5. Invoices Endpoint

### GET /invoices
**Purpose:** Retrieve invoices

**Parameters:**
- `limit` (int): Number of records to return
- `status` (string): Filter by invoice status

**Request:**
```bash
curl -X GET "https://db.ginos.cloud/api/index.php/invoices?limit=5" \
  -H "DOLAPIKEY: your_api_key"
```

**Response:**
```json
[]
```
*Note: Currently empty in test instance*

---

## 6. Orders Endpoint

### GET /orders
**Purpose:** Retrieve orders

**Parameters:**
- `limit` (int): Number of records to return
- `status` (string): Filter by order status

**Request:**
```bash
curl -X GET "https://db.ginos.cloud/api/index.php/orders?limit=5" \
  -H "DOLAPIKEY: your_api_key"
```

**Response:**
```json
[]
```
*Note: Currently empty in test instance*

---

## 7. Contacts Endpoint

### GET /contacts
**Purpose:** Retrieve contacts

**Parameters:**
- `limit` (int): Number of records to return
- `thirdparty` (int): Filter by third party ID

**Request:**
```bash
curl -X GET "https://db.ginos.cloud/api/index.php/contacts?limit=5" \
  -H "DOLAPIKEY: your_api_key"
```

**Response:**
```json
[]
```
*Note: Currently empty in test instance*

---

## Common Response Patterns

### Success Response Structure
```json
{
  "data": [...],
  "success": {
    "code": 200
  }
}
```

### Error Response Structure
```json
{
  "error": {
    "code": 404,
    "message": "Object not found"
  }
}
```

### Standard Object Fields
All business objects contain these common fields:
- `id`: Unique identifier
- `ref`: Reference number
- `entity`: Entity ID (multi-company)
- `status`/`statut`: Status code
- `date_creation`: Creation timestamp
- `date_modification`: Last modification timestamp
- `user_creation_id`: Creator user ID
- `user_modification_id`: Last modifier user ID
- `note_public`: Public notes
- `note_private`: Private notes
- `array_options`: Custom fields

---

## HTTP Methods Support

| Endpoint | GET | POST | PUT | DELETE |
|----------|-----|------|-----|--------|
| /status | ✅ | ❌ | ❌ | ❌ |
| /users | ✅ | ✅ | ✅ | ✅ |
| /thirdparties | ✅ | ✅ | ✅ | ✅ |
| /products | ✅ | ✅ | ✅ | ✅ |
| /invoices | ✅ | ✅ | ✅ | ✅ |
| /orders | ✅ | ✅ | ✅ | ✅ |
| /contacts | ✅ | ✅ | ✅ | ✅ |

---

## Authentication Details

### API Key Location
The API key must be passed in the `DOLAPIKEY` header:
```bash
-H "DOLAPIKEY: 7cxAAO835BF7bXy6DsQ2j2a7nT6ectGY"
```

### Permissions
API access is tied to the user's permissions in Dolibarr. Ensure the API user has appropriate rights for the endpoints you wish to access.

---

## Next Steps for MCP Implementation

Based on this testing, the MCP server should implement:

1. **Core CRUD Operations** for all confirmed endpoints
2. **Parameter Validation** for limit, sorting, and filtering
3. **Error Handling** for 4xx and 5xx responses
4. **Response Normalization** to handle Dolibarr's response format
5. **Authentication Management** via environment variables
6. **Logging** for debugging and monitoring

## Additional Endpoints to Test

These endpoints should be tested in future development:
- `/projects` - Project management
- `/proposals` - Commercial proposals  
- `/contracts` - Contract management
- `/categories` - Category management
- `/warehouses` - Inventory management
- `/payments` - Payment tracking
- `/expensereports` - Expense management
- `/documents` - Document management (with proper parameters)