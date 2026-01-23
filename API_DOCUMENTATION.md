# API Documentation

Complete API reference for AquaSentinel Backend.

**Base URL:** `http://localhost:8000`

---

## Table of Contents

1. [Dashboard Endpoints](#dashboard-endpoints)
2. [AI/ML Endpoints](#aiml-endpoints)
3. [Health & Status](#health--status)
4. [Error Handling](#error-handling)
5. [Request/Response Format](#requestresponse-format)

---

## Dashboard Endpoints

### Get Financial KPIs

Get key financial performance indicators.

```http
GET /api/v0/dashboard/kpis
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_revenue": 497.41,
    "budgeted_revenue": 520.0,
    "revenue_variance": -22.59,
    "operating_margin": 0.17,
    "days_sales_outstanding": 42,
    "non_revenue_water_pct": 0.25,
    "cost_per_gallon": 4.15,
    "collection_rate": 0.92,
    "debt_service_coverage": 2.85,
    "water_revenue": 380.5,
    "cash_reserve": 45.2,
    "total_ar": 12.5,
    "outstanding_debt": 8.5
  }
}
```

---

### Get Revenue Summary

Get revenue summary with trends.

```http
GET /api/v0/dashboard/revenue/summary
```

**Query Parameters:**
- `period` (optional): `monthly`, `quarterly`, `yearly` (default: `monthly`)

**Response:**
```json
{
  "success": true,
  "data": {
    "total_revenue": 497.41,
    "budgeted_revenue": 520.0,
    "variance": -22.59,
    "variance_pct": -0.043,
    "trend": "increasing",
    "periods": [
      {
        "period": "2024-01",
        "revenue": 18.4,
        "budgeted": 22.44,
        "variance": -4.04
      }
    ]
  }
}
```

---

### Get Revenue Trends

Get revenue trends over time.

```http
GET /api/v0/dashboard/revenue/trends
```

**Query Parameters:**
- `period` (optional): `monthly`, `quarterly`, `yearly` (default: `monthly`)
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "period": "2024-Q1",
      "revenue": 88.57,
      "budgeted": 95.0,
      "variance": -6.43
    }
  ]
}
```

---

### Get Budget Variance

Get budget vs actual variance by department.

```http
GET /api/v0/dashboard/budget-variance
```

**Query Parameters:**
- `date` (optional): Specific date (YYYY-MM-DD)
- `department` (optional): Filter by department

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-01-01",
      "department": "Operations",
      "budget": 781.59,
      "actual": 871.15,
      "variance": 89.56,
      "variance_pct": 0.1146
    }
  ]
}
```

---

### Get AR Aging

Get accounts receivable aging analysis.

```http
GET /api/v0/dashboard/ar-aging
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_ar": 12.5,
    "current_pct": 0.59,
    "days_30_pct": 0.29,
    "days_60_pct": 0.12,
    "aging_breakdown": [
      {
        "bucket": "current",
        "amount": 7.38,
        "percentage": 0.59
      }
    ]
  }
}
```

---

### Get Debt Metrics

Get debt service coverage and related metrics.

```http
GET /api/v0/dashboard/debt
```

**Response:**
```json
{
  "success": true,
  "data": {
    "outstanding_debt": 8.5,
    "debt_service_coverage": 2.85,
    "projected_coverage": 1.4,
    "required_minimum": 1.25,
    "actual_coverage": 1.43,
    "status": "healthy"
  }
}
```

---

### Get Alerts

Get system-generated alerts and forecasts.

```http
GET /api/v0/dashboard/alerts
```

**Query Parameters:**
- `date` (optional): Filter by date (YYYY-MM-DD)
- `confidence_min` (optional): Minimum confidence level (0-1)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-01-01",
      "alert_type": "Q1 Profitability Forecast",
      "description": "Q1 net income expected to reach target",
      "potential_impact_k": 258.7,
      "confidence_level": 0.81
    }
  ]
}
```

---

### Get Scenarios

Get financial scenario projections.

```http
GET /api/v0/dashboard/scenarios
```

**Query Parameters:**
- `date` (optional): Filter by date (YYYY-MM-DD)
- `scenario` (optional): Filter by scenario type

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-01-01",
      "scenario": "Base Case",
      "projected_revenue": 24.5,
      "projected_expenses": 18.5,
      "debt_service_coverage": 2.89,
      "net_income": 6.0,
      "financial_viability": "Healthy"
    }
  ]
}
```

---

## AI/ML Endpoints

### Ask Question

Convert natural language question to SQL and execute.

```http
POST /api/v0/ai/ask
Content-Type: application/json
```

**Request Body:**
```json
{
  "question": "What was the total revenue in 2024?",
  "run_sql": true
}
```

**Parameters:**
- `question` (required): Natural language question
- `run_sql` (optional): Execute SQL and return data (default: `true`)

**Response:**
```json
{
  "success": true,
  "question": "What was the total revenue in 2024?",
  "sql": "SELECT SUM(actual_revenue) as total_revenue FROM water_data WHERE year = 2024",
  "type": "sql",
  "data": [
    {
      "total_revenue": 497.41
    }
  ],
  "row_count": 1,
  "column_count": 1,
  "summary": "Total revenue in 2024 was $497.41M..."
}
```

**Example Questions:**
- "What was the total revenue in 2024?"
- "Show me revenue by quarter for 2023"
- "Which departments had the highest budget variance?"
- "What is the average operating margin?"
- "Show me months with non-revenue water above 25%"

---

### Generate SQL

Generate SQL from natural language without executing.

```http
GET /api/v0/ai/generate-sql
```

**Query Parameters:**
- `question` (required): Natural language question

**Response:**
```json
{
  "success": true,
  "question": "Show me revenue by quarter",
  "sql": "SELECT quarter, SUM(actual_revenue) as total_revenue FROM water_data GROUP BY quarter ORDER BY quarter",
  "type": "sql"
}
```

---

### Run SQL

Execute a SQL query directly.

```http
POST /api/v0/ai/run-sql
Content-Type: application/json
```

**Request Body:**
```json
{
  "sql": "SELECT * FROM water_data WHERE year = 2024 LIMIT 10"
}
```

**Response:**
```json
{
  "success": true,
  "sql": "SELECT * FROM water_data WHERE year = 2024 LIMIT 10",
  "data": [
    {
      "date": "2024-01-01",
      "year": 2024,
      "actual_revenue": 18.4,
      ...
    }
  ],
  "row_count": 10,
  "column_count": 26
}
```

---

### AI Health Check

Check AI service health and connectivity.

```http
GET /api/v0/ai/health
```

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "service": "Vanna AI",
  "database": "connected",
  "vector_store": "connected"
}
```

---

## Health & Status

### Health Check

Basic health check endpoint.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-19T18:08:01.091032"
}
```

---

### Root Endpoint

Get API information and available endpoints.

```http
GET /
```

**Response:**
```json
{
  "message": "AquaSentinel API",
  "version": "1.0.0",
  "endpoints": {
    "kpis": "/api/v0/dashboard/kpis",
    "revenue": "/api/v0/dashboard/revenue/summary",
    "ai_ask": "/api/v0/ai/ask",
    ...
  }
}
```

---

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": "Error message description"
}
```

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Endpoint not found
- `500 Internal Server Error` - Server error

### Common Errors

**Missing Question:**
```json
{
  "success": false,
  "error": "Question is required"
}
```

**Database Error:**
```json
{
  "success": false,
  "error": "SQL execution failed: ..."
}
```

**AI Service Error:**
```json
{
  "success": false,
  "error": "Failed to initialize Vanna AI: ..."
}
```

---

## Request/Response Format

### Request Headers

```
Content-Type: application/json
Accept: application/json
```

### Response Headers

```
Content-Type: application/json
X-Request-ID: <uuid>
Access-Control-Allow-Origin: *
```

### Request ID

Every request includes a unique Request ID in the response header:
- `X-Request-ID: <uuid>`
- Used for logging and debugging
- Included in all log entries

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider:
- API key authentication
- Rate limiting middleware
- Request throttling

---

## CORS

CORS is enabled for all origins (`*`). For production:
- Configure specific allowed origins
- Set proper CORS headers
- Enable credentials if needed

---

## Authentication

Currently no authentication is required. For production:
- Implement API key authentication
- Use JWT tokens
- Add role-based access control

---

## Versioning

API version is included in the path: `/api/v0/`

Future versions will use `/api/v1/`, `/api/v2/`, etc.

---

## Best Practices

1. **Always check `success` field** in responses
2. **Use Request IDs** for debugging (from `X-Request-ID` header)
3. **Handle errors gracefully** - check status codes
4. **Use appropriate HTTP methods** - GET for reads, POST for writes
5. **Include proper headers** - Content-Type for POST requests

---

## Examples

See `README.md` for usage examples and code samples.

---

**Last Updated:** 2026-01-19

