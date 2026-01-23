# Complete API Endpoints Reference

This document lists all available endpoints in the AquaSentinel Backend API.

**Base URL:** `http://localhost:8084`

---

## 📊 Dashboard Endpoints

All dashboard endpoints are prefixed with `/api/v0/dashboard`

### 1. Financial KPIs
**GET** `/api/v0/dashboard/kpis`

Get current financial KPIs for the dashboard header.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_revenue": {...},
    "budget_variance": {...},
    "ar_aging": {...},
    "debt_metrics": {...}
  }
}
```

---

### 2. Revenue Summary
**GET** `/api/v0/dashboard/revenue/summary`

Get revenue performance summary with variance analysis.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_revenue": 1234567.89,
    "budgeted_revenue": 1200000.00,
    "variance": 34567.89,
    "variance_percent": 2.88
  }
}
```

---

### 3. Revenue Trends
**GET** `/api/v0/dashboard/revenue/trends`

Get revenue trends over time for charting.

**Query Parameters:**
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)
- `period` (optional): Period aggregation - `monthly`, `quarterly`, or `yearly` (default: `monthly`)

**Example:**
```
GET /api/v0/dashboard/revenue/trends?period=quarterly&start_date=2023-01-01
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "period": "2024-Q1",
      "revenue": 123456.78,
      "budgeted": 120000.00
    },
    ...
  ]
}
```

---

### 4. Budget Variance
**GET** `/api/v0/dashboard/budget-variance`

Get budget variance by department.

**Query Parameters:**
- `department` (optional): Department filter
- `year` (optional): Year filter (integer)

**Example:**
```
GET /api/v0/dashboard/budget-variance?department=Water%20Treatment&year=2024
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "department": "Water Treatment",
      "actual": 500000.00,
      "budgeted": 480000.00,
      "variance": 20000.00,
      "variance_percent": 4.17
    },
    ...
  ]
}
```

---

### 5. AR Aging
**GET** `/api/v0/dashboard/ar-aging`

Get current accounts receivable aging distribution.

**Response:**
```json
{
  "success": true,
  "data": {
    "current": 100000.00,
    "days_30": 50000.00,
    "days_60": 30000.00,
    "days_90": 20000.00,
    "over_90": 10000.00,
    "total": 210000.00
  }
}
```

---

### 6. Debt Metrics
**GET** `/api/v0/dashboard/debt`

Get current debt sustainability metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_debt": 5000000.00,
    "debt_to_revenue_ratio": 0.45,
    "debt_service_coverage": 2.5,
    "maturity_schedule": {...}
  }
}
```

---

### 7. Efficiency Alerts
**GET** `/api/v0/dashboard/alerts`

Get efficiency alerts and optimization opportunities.

**Query Parameters:**
- `alert_type` (optional): Alert type filter
- `limit` (optional): Maximum number of alerts (default: 10)

**Example:**
```
GET /api/v0/dashboard/alerts?alert_type=budget&limit=5
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "type": "budget_variance",
      "severity": "high",
      "message": "Department X exceeded budget by 15%",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    ...
  ]
}
```

---

### 8. Scenarios
**GET** `/api/v0/dashboard/scenarios`

Get scenario planning projections.

**Query Parameters:**
- `year` (optional): Year filter (integer)

**Example:**
```
GET /api/v0/dashboard/scenarios?year=2024
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "scenario_name": "Optimistic",
      "year": 2024,
      "projected_revenue": 1500000.00,
      "assumptions": {...}
    },
    ...
  ]
}
```

---

## 🤖 AI/ML Endpoints

All AI endpoints are prefixed with `/api/v0/ai`

### 9. Ask Question (Natural Language Query)
**POST** `/api/v0/ai/ask`

Ask a natural language question and get SQL + results with automatic flow handling.

**Request Body:**
```json
{
  "question": "What was the total revenue in 2024?",
  "run_sql": true
}
```

**Parameters:**
- `question` (required): Natural language question
- `run_sql` (optional): Whether to execute SQL and return data (default: `true`)

**Flow Logic:**
- **If SQL is generated**: Execute SQL, then generate summary automatically
- **If no SQL (text response)**: Generate summary directly from question

**Response (with SQL execution):**
```json
{
  "success": true,
  "question": "What was the total revenue in 2024?",
  "sql": "SELECT SUM(actual_revenue) as total_revenue FROM water_data WHERE year = 2024",
  "type": "sql",
  "data": [
    {
      "total_revenue": 1234567.89
    }
  ],
  "row_count": 1,
  "column_count": 1,
  "summary": "Based on the question: 'What was the total revenue in 2024?' The query returned 1 row(s)..."
}
```

**Response (text response, no SQL):**
```json
{
  "success": true,
  "question": "What is the weather today?",
  "sql": "I cannot answer that question with SQL.",
  "type": "text",
  "text": "I cannot answer that question with SQL.",
  "data": null,
  "row_count": 0,
  "column_count": 0,
  "summary": "Summary generated from question..."
}
```

**Response (SQL only, no execution):**
```json
{
  "success": true,
  "question": "What was the total revenue in 2024?",
  "sql": "SELECT SUM(actual_revenue) as total_revenue FROM water_data WHERE year = 2024",
  "type": "sql"
}
```

---

### 10. Generate SQL
**GET** or **POST** `/api/v0/ai/generate-sql`

Generate SQL from natural language question (without executing).

**GET Request:**
```
GET /api/v0/ai/generate-sql?question=What%20is%20the%20total%20revenue
```

**POST Request:**
```json
{
  "question": "What is the total revenue?"
}
```

**Response:**
```json
{
  "success": true,
  "question": "What is the total revenue?",
  "sql": "SELECT SUM(actual_revenue) as total_revenue FROM water_data",
  "type": "sql"
}
```

---

### 11. Run SQL
**POST** `/api/v0/ai/run-sql`

Execute a SQL query and return results with optional summary generation.

**Request Body:**
```json
{
  "sql": "SELECT COUNT(*) as total FROM water_data WHERE year = 2024",
  "question": "What is the total count?",  // Optional: for summary generation
  "generate_summary": true  // Optional: whether to generate summary (default: true)
}
```

**Flow Logic:**
- **If SQL is provided**: Execute SQL, then generate summary (if `generate_summary=true` and `question` is provided)
- **If SQL is empty/null**: Generate summary directly from question (if `question` is provided)

**Response (with SQL):**
```json
{
  "success": true,
  "sql": "SELECT COUNT(*) as total FROM water_data WHERE year = 2024",
  "data": [
    {
      "total": 48
    }
  ],
  "row_count": 1,
  "column_count": 1,
  "summary": "Based on the question: 'What is the total count?' The query returned 1 row(s)..."
}
```

**Response (no SQL, summary only):**
```json
{
  "success": true,
  "sql": null,
  "type": "text",
  "question": "What is the total revenue?",
  "data": null,
  "row_count": 0,
  "column_count": 0,
  "summary": "Summary generated from question..."
}
```

---

### 12. AI Health Check
**GET** `/api/v0/ai/health`

Check AI service health.

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

## 📝 Summary Generation Endpoint

### 13. Generate Summary
**POST** `/api/v0/vanna/generate_summary`

Generate natural language summary from SQL query results.

**Request Body:**
```json
{
  "question": "What was the total revenue in 2024?",
  "sql": "SELECT SUM(actual_revenue) FROM water_data WHERE year = 2024",
  "data": [...]  // Optional: pre-executed data
}
```

**Response:**
```json
{
  "success": true,
  "summary": "Based on the question: 'What was the total revenue in 2024?' The query returned 1 row(s) with 1 column(s). The total revenue for 2024 was $1,234,567.89.",
  "question": "What was the total revenue in 2024?",
  "sql": "SELECT SUM(actual_revenue) FROM water_data WHERE year = 2024",
  "row_count": 1,
  "column_count": 1
}
```

---

## 🔧 System Endpoints

### 14. Health Check
**GET** `/health`

Check server health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T15:30:00.123456"
}
```

---

### 15. API Info
**GET** `/api/info`

Get API information and endpoint list.

**Response:**
```json
{
  "message": "AquaSentinel API",
  "version": "1.0.0",
  "endpoints": {
    "kpis": "/api/v0/dashboard/kpis",
    "revenue": "/api/v0/dashboard/revenue/summary",
    "revenue_trends": "/api/v0/dashboard/revenue/trends",
    "budget_variance": "/api/v0/dashboard/budget-variance",
    "ar_aging": "/api/v0/dashboard/ar-aging",
    "debt": "/api/v0/dashboard/debt",
    "alerts": "/api/v0/dashboard/alerts",
    "scenarios": "/api/v0/dashboard/scenarios",
    "vanna_ui": "/",
    "vanna_api": "/api/v0/vanna"
  }
}
```

---

## 🎨 Vanna UI Endpoints

These endpoints are provided by VannaFlaskApp for the AI chat interface.

### 16. Vanna UI
**GET** `/`

The main Vanna AI chat interface (HTML page).

---

### 17. Vanna API Endpoints
**Various** `/api/v0/vanna/*`

VannaFlaskApp provides additional endpoints under `/api/v0/vanna/` for its internal UI functionality. These are managed by VannaFlaskApp and may include:
- Training data management
- Question history
- SQL validation
- Other Vanna-specific features

**Note:** Custom routes take precedence over VannaFlaskApp routes. If a route matches both, the custom route will be used.

---

## 📋 Static Assets

### 18. Local Assets
**GET** `/assets/local/<filename>`

Serve custom static assets from the project's static directory.

**Example:**
```
GET /assets/local/aquasentinel-logo.jpg
```

---

### 19. Favicon
**GET** `/favicon.ico`

Serve custom favicon for browser tab.

---

## 🔐 Request Headers

All endpoints support the following headers:

- `Content-Type: application/json` (for POST requests)
- `X-Request-ID` (automatically generated, returned in response headers)

---

## 📤 Response Headers

All responses include:

- `X-Request-ID`: Unique request identifier
- `Access-Control-Allow-Origin: *` (CORS enabled)
- `Content-Type: application/json`

---

## ⚠️ Error Responses

All endpoints return errors in the following format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (missing/invalid parameters)
- `404`: Not Found (route doesn't exist)
- `500`: Internal Server Error

---

## 📝 Notes

1. **Caching**: Dashboard endpoints use 5-minute caching for performance
2. **Request IDs**: Every request gets a unique UUID for tracking
3. **Logging**: All requests are logged with full details
4. **CORS**: Enabled for all origins (`*`)
5. **Port**: Default port is `8084` (VannaFlaskApp default)

---

## 🧪 Testing

Use the provided test scripts:
- `test_all_comprehensive.py` - Test all endpoints
- `test_questions.py` - Interactive question testing
- `demo_questions.py` - Quick demo of sample questions

---

**Last Updated:** 2024-01-20

