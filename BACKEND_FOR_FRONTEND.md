# Backend API Guide for Frontend

## Quick Overview

**AquaSentinel Backend API** - Flask-based REST API with AI/ML capabilities for water utility financial and operational data.

- **Base URL:** `http://localhost:8084`
- **Port:** `8084`
- **API Version:** `v0`
- **Response Format:** JSON

---

## Main Endpoints

### Dashboard Endpoints (`/api/v0/dashboard/`)

#### Financial KPIs
```http
GET /api/v0/dashboard/kpis
```
Returns current financial KPIs (revenue, margin, DSO, etc.)

#### Revenue Summary
```http
GET /api/v0/dashboard/revenue/summary?period=monthly
```
Returns revenue summary with variance and trends.

#### Revenue Trends
```http
GET /api/v0/dashboard/revenue/trends?period=monthly|quarterly|yearly
```
Returns revenue trends over time.

#### Budget Variance
```http
GET /api/v0/dashboard/budget-variance?date=2024-01-01&department=Operations
```
Returns budget vs actual variance by department.

#### AR Aging
```http
GET /api/v0/dashboard/ar-aging
```
Returns accounts receivable aging breakdown.

#### Debt Metrics
```http
GET /api/v0/dashboard/debt
```
Returns debt service coverage and related metrics.

#### Alerts
```http
GET /api/v0/dashboard/alerts?limit=10&confidence_min=0.8
```
Returns system-generated alerts and forecasts.

#### Scenarios
```http
GET /api/v0/dashboard/scenarios?date=2024-01-01
```
Returns financial scenario projections.

---

### AI/ML Endpoints (via VannaFlaskApp)

#### Natural Language Query
```http
POST /api/v0/vanna/generate_sql
Content-Type: application/json

{
  "question": "What was the total revenue in 2024?"
}
```

#### Run SQL Query
```http
POST /api/v0/vanna/run_sql
Content-Type: application/json

{
  "sql": "SELECT SUM(actual_revenue) FROM water_data WHERE year = 2024"
}
```

#### Generate Summary
```http
POST /api/v0/vanna/generate_summary
Content-Type: application/json

{
  "question": "What was the total revenue in 2024?",
  "sql": "SELECT SUM(actual_revenue) FROM water_data WHERE year = 2024"
}
```

**Alternative:** Provide pre-executed data instead of SQL:
```http
POST /api/v0/vanna/generate_summary
Content-Type: application/json

{
  "question": "What was the total revenue in 2024?",
  "data": [
    {"total_revenue": 497.41}
  ]
}
```

**Note:** VannaFlaskApp provides a UI at `http://localhost:8084/` for testing AI queries.

---

### Utility Endpoints

#### Health Check
```http
GET /health
```
Returns: `{"status": "healthy", "timestamp": "..."}`

#### API Info
```http
GET /api/info
```
Returns list of available endpoints.

---

## Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data here
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message here"
}
```

### Response Headers
- `X-Request-ID`: Unique request identifier (UUID)
- `Content-Type`: `application/json`
- `Access-Control-Allow-Origin`: `*` (CORS enabled)

---

## Example Usage

### JavaScript/Fetch
```javascript
// Get Financial KPIs
const response = await fetch('http://localhost:8084/api/v0/dashboard/kpis');
const { success, data } = await response.json();

if (success) {
  console.log('Total Revenue:', data.total_revenue);
  console.log('Operating Margin:', data.operating_margin);
}

// Get Revenue Trends
const trendsResponse = await fetch(
  'http://localhost:8084/api/v0/dashboard/revenue/trends?period=quarterly'
);
const trends = await trendsResponse.json();

// AI Query - Generate SQL
const aiResponse = await fetch('http://localhost:8084/api/v0/vanna/generate_sql', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'What was the total revenue in 2024?'
  })
});
const aiData = await aiResponse.json();

// Generate Summary
const summaryResponse = await fetch('http://localhost:8084/api/v0/vanna/generate_summary', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'What was the total revenue in 2024?',
    sql: 'SELECT SUM(actual_revenue) FROM water_data WHERE year = 2024'
  })
});
const summaryData = await summaryResponse.json();
```

### Axios
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8084',
  headers: { 'Content-Type': 'application/json' }
});

// Get KPIs
const { data } = await api.get('/api/v0/dashboard/kpis');

// AI Query - Generate SQL
const { data: aiData } = await api.post('/api/v0/vanna/generate_sql', {
  question: 'Show me revenue by quarter'
});

// Generate Summary
const { data: summaryData } = await api.post('/api/v0/vanna/generate_summary', {
  question: 'What was the total revenue in 2024?',
  sql: 'SELECT SUM(actual_revenue) FROM water_data WHERE year = 2024'
});
```

---

## Key Features

✅ **CORS Enabled** - All origins allowed  
✅ **Request ID Tracking** - Every response includes `X-Request-ID` header  
✅ **Caching** - Dashboard endpoints cached for 5 minutes  
✅ **Error Handling** - Consistent error response format  
✅ **Logging** - Comprehensive request/response logging  

---

## Data Structure

### KPI Response Example
```json
{
  "success": true,
  "data": {
    "total_revenue": 497.41,
    "operating_margin": 0.17,
    "days_sales_outstanding": 42,
    "non_revenue_water_pct": 0.25,
    "debt_service_coverage": 2.85
  }
}
```

### Revenue Trends Example
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

## Testing

- **Health Check:** `http://localhost:8084/health`
- **Vanna UI:** `http://localhost:8084/` (for testing AI queries)
- **API Info:** `http://localhost:8084/api/info`

---

## Notes

1. **Port:** Server runs on `8084` (not 8000)
2. **Vanna UI:** Built-in UI available at root URL for testing
3. **Request IDs:** Use `X-Request-ID` header for debugging
4. **Caching:** Dashboard data cached for performance
5. **Error Handling:** Always check `success` field in responses

---

**Last Updated:** 2026-01-20

