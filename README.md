# AquaSentinel Backend API

**CFO Command Intelligence API for Water Utility Financial, Operational, Billing & Compliance Oversight**

A comprehensive Flask-based backend API with AI/ML capabilities for natural language to SQL queries, providing real-time insights into water utility operations, financial performance, and compliance metrics.

---

## 🚀 Features

- **📊 Dashboard API** - Financial KPIs, revenue trends, budget variance, AR aging, debt metrics
- **🤖 AI/ML Integration** - Natural language to SQL queries using Vanna AI, OpenAI GPT-4o-mini, and Pinecone
- **💾 SQLite Database** - Normalized data structure with departments, alerts, and scenarios
- **📈 Real-time Analytics** - Caching, request tracking, comprehensive logging
- **🧪 Testing** - Unit and integration tests with pytest
- **🔒 Production Ready** - CORS enabled, request IDs, error handling

---

## 📁 Project Structure

```
waterbackend/
├── app.py                      # Main Flask application
├── waterdata.py                # Data generator script
├── train_vanna.py              # AI training script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
│
├── core/                       # Core utilities
│   ├── custom_vanna.py        # Custom Vanna AI implementation
│   └── logging_utils.py        # Logging configuration
│
├── routes/                     # API route handlers
│   ├── dashboard_routes.py     # Dashboard endpoints
│   └── ai_routes.py           # AI/ML endpoints
│
├── services/                   # Business logic layer
│   ├── dashboard_service.py    # Dashboard data operations
│   └── sql_prompt_service.py  # SQL prompt generation
│
├── database/                   # Database files
│   ├── csv_ingestion.py       # CSV to SQLite converter
│   └── water_data.db          # SQLite database
│
├── training/                   # AI training components
│   ├── core/
│   │   └── openai_chat.py     # OpenAI integration
│   └── vector_stores/
│       └── pinecone_vector.py # Pinecone integration
│
├── schema/                     # Database schemas
│   └── water_data.sql         # DDL schema
│
├── data/                       # Data files
│   └── data.csv               # Source CSV data
│
└── tests/                      # Test files
    ├── test_dashboard_service.py
    └── test_routes.py
```

---

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key (free tier available)

### Step 1: Clone and Install Dependencies

```bash
# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=aquasentinel-index

# Database Configuration
SQLITE_DB_PATH=database/water_data.db
```

**Get API Keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Pinecone**: https://app.pinecone.io/

### Step 3: Create Database

```bash
python database/csv_ingestion.py
```

This creates `database/water_data.db` from `data/data.csv`.

### Step 4: Train AI Model

```bash
python train_vanna.py
```

This trains Vanna AI with:
- DDL schema
- Documentation
- 20 question-SQL examples

### Step 5: Start Server

```bash
python app.py
```

Server runs on `http://localhost:8000`

---

## 📡 API Endpoints

### Dashboard Endpoints

#### Get Financial KPIs
```http
GET /api/v0/dashboard/kpis
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_revenue": 497.41,
    "operating_margin": 0.17,
    "debt_service_coverage": 2.85,
    ...
  }
}
```

#### Get Revenue Summary
```http
GET /api/v0/dashboard/revenue/summary
```

#### Get Revenue Trends
```http
GET /api/v0/dashboard/revenue/trends?period=quarterly
```

#### Get Budget Variance
```http
GET /api/v0/dashboard/budget-variance
```

#### Get AR Aging
```http
GET /api/v0/dashboard/ar-aging
```

#### Get Debt Metrics
```http
GET /api/v0/dashboard/debt
```

#### Get Alerts
```http
GET /api/v0/dashboard/alerts
```

#### Get Scenarios
```http
GET /api/v0/dashboard/scenarios
```

---

### AI/ML Endpoints

#### Ask Question (Natural Language to SQL)
```http
POST /api/v0/ai/ask
Content-Type: application/json

{
  "question": "What was the total revenue in 2024?",
  "run_sql": true
}
```

**Response:**
```json
{
  "success": true,
  "question": "What was the total revenue in 2024?",
  "sql": "SELECT SUM(actual_revenue) as total_revenue FROM water_data WHERE year = 2024",
  "type": "sql",
  "data": [{"total_revenue": 497.41}],
  "row_count": 1,
  "column_count": 1,
  "summary": "Total revenue in 2024 was $497.41M..."
}
```

#### Generate SQL Only
```http
GET /api/v0/ai/generate-sql?question=Show me revenue by quarter
```

#### Run SQL Query
```http
POST /api/v0/ai/run-sql
Content-Type: application/json

{
  "sql": "SELECT * FROM water_data WHERE year = 2024 LIMIT 10"
}
```

#### AI Health Check
```http
GET /api/v0/ai/health
```

---

## 💡 Usage Examples

### Example 1: Natural Language Query

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v0/ai/ask",
    json={
        "question": "What was the total revenue in 2024?",
        "run_sql": True
    }
)

data = response.json()
print(f"SQL: {data['sql']}")
print(f"Result: {data['data']}")
print(f"Summary: {data['summary']}")
```

### Example 2: Get Financial KPIs

```python
import requests

response = requests.get("http://localhost:8000/api/v0/dashboard/kpis")
kpis = response.json()['data']

print(f"Total Revenue: ${kpis['total_revenue']}M")
print(f"Operating Margin: {kpis['operating_margin']*100:.1f}%")
```

### Example 3: Revenue Trends

```python
import requests

response = requests.get(
    "http://localhost:8000/api/v0/dashboard/revenue/trends",
    params={"period": "quarterly"}
)

trends = response.json()['data']
for trend in trends:
    print(f"{trend['period']}: ${trend['revenue']}M")
```

---

## 🤖 AI/ML Examples

Try these natural language questions:

1. **Revenue Analysis**
   - "What was the total revenue in 2024?"
   - "Show me revenue by quarter for 2023"
   - "Which year had the highest revenue?"

2. **Budget Analysis**
   - "Which departments had the highest budget variance?"
   - "Show me departments exceeding budget by more than 10%"

3. **Operational Metrics**
   - "What is the average operating margin?"
   - "Show me months with non-revenue water above 25%"
   - "What is the collection rate trend?"

4. **Debt & Financial**
   - "What is the debt service coverage ratio?"
   - "Show me scenarios with healthy financial viability"

5. **Alerts & Scenarios**
   - "Show me all alerts with confidence above 0.8"
   - "What are the projected revenues for all scenarios?"

---

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Test AI Endpoints

```bash
python test_ai.py
```

### Test API Endpoints

```bash
python test_api.py
```

---

## 📊 Database Schema

### Main Tables

1. **water_data** - Core financial and operational metrics
   - Financial: `actual_revenue`, `budgeted_revenue`, `revenue_variance`, `operating_margin`
   - Operational: `days_sales_outstanding`, `non_revenue_water_pct`, `cost_per_gallon`, `collection_rate`
   - Debt: `debt_service_coverage`, `outstanding_debt`

2. **departments** - Department-level budget vs actual
   - Columns: `date`, `department`, `budget`, `actual`, `variance`, `variance_pct`

3. **alerts** - System-generated alerts
   - Columns: `date`, `alert_type`, `description`, `potential_impact_k`, `confidence_level`

4. **scenarios** - Financial scenario projections
   - Columns: `date`, `scenario`, `projected_revenue`, `financial_viability`

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini | Yes |
| `PINECONE_API_KEY` | Pinecone API key | Yes |
| `PINECONE_ENVIRONMENT` | Pinecone environment/region | No (default: us-east-1) |
| `PINECONE_INDEX_NAME` | Pinecone index name | No (default: aquasentinel-index) |
| `SQLITE_DB_PATH` | Path to SQLite database | No (default: database/water_data.db) |

### Model Configuration

The AI model is configured in:
- `train_vanna.py` - Training script
- `routes/ai_routes.py` - API routes

Default: `gpt-4o-mini` (cost-effective)

---

## 🐛 Troubleshooting

### Server Won't Start

**Port Already in Use:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill
```

### Database Not Found

```bash
# Recreate database
python database/csv_ingestion.py
```

### AI Training Fails

**Missing API Keys:**
- Check `.env` file exists
- Verify API keys are correct
- Ensure keys have proper permissions

**Pinecone Index Issues:**
- Check Pinecone dashboard
- Verify index name matches `.env`
- Ensure index exists or has correct dimensions

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## 📝 Logging

Logs are stored in:
- `logs/aquasentinel_api.log` - API requests/responses
- `logs/aquasentinel_data.log` - Data operations

Each request includes:
- Request ID (UUID)
- Timestamp
- Method and URL
- Response time
- Status code

---

## 🚀 Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Environment Variables

Set production environment variables:
- Use secure API keys
- Configure CORS for your domain
- Set up proper logging
- Enable HTTPS

---

## 📚 Additional Documentation

- **AI/ML Setup**: See `AI_ML_COMPLETE_SETUP.md`
- **Environment Setup**: See `ENV_SETUP.md`
- **API Keys Setup**: See `SETUP_API_KEYS.md`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

This project is proprietary software.

---

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs in `logs/`
3. Check API health endpoints
4. Verify environment variables

---

## ✨ Features Summary

- ✅ RESTful API with Flask
- ✅ Natural Language to SQL (Vanna AI)
- ✅ OpenAI GPT-4o-mini integration
- ✅ Pinecone vector database
- ✅ SQLite data storage
- ✅ Caching for performance
- ✅ Request ID tracking
- ✅ Comprehensive logging
- ✅ Unit and integration tests
- ✅ CORS enabled
- ✅ Production ready

---

**Built with ❤️ for Water Utility Management**
