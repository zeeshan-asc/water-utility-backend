# 🤖 AI/ML Complete Setup Guide

## ✅ What's Been Completed

All AI/ML components have been successfully created:

1. ✅ **Database Setup** - SQLite database from CSV (`database/water_data.db`)
2. ✅ **Core AI Components** - OpenAI, Pinecone, Custom Vanna
3. ✅ **AI Routes** - Natural language query endpoints
4. ✅ **Training Data** - DDL schema and question-SQL examples
5. ✅ **Training Script** - Script to populate Pinecone

---

## 🚀 Quick Start

### **Step 1: Install Dependencies**

```bash
pip install -r requirements.txt
```

### **Step 2: Set Up Environment Variables**

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

### **Step 3: Create Database** (Already Done ✅)

```bash
python database/csv_ingestion.py
```

### **Step 4: Train Vanna AI**

```bash
python train_vanna.py
```

This will:
- Load DDL schema from `schema/water_data.sql`
- Add documentation about the database
- Train with 20 question-SQL examples from `training_sql_data.json`
- Store everything in Pinecone vector database

### **Step 5: Start Server**

```bash
python app.py
```

---

## 📡 API Endpoints

### **1. Ask Question (Natural Language to SQL + Results)**

```bash
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
  "data": [{"total_revenue": 475.9}],
  "row_count": 1,
  "column_count": 1,
  "summary": "Total revenue in 2024 was $475.9M..."
}
```

### **2. Generate SQL Only**

```bash
GET /api/v0/ai/generate-sql?question=Show me revenue by quarter
```

### **3. Run SQL Query**

```bash
POST /api/v0/ai/run-sql
Content-Type: application/json

{
  "sql": "SELECT * FROM water_data WHERE year = 2024 LIMIT 10"
}
```

### **4. Health Check**

```bash
GET /api/v0/ai/health
```

---

## 📁 File Structure

```
waterbackend/
├── core/
│   └── custom_vanna.py          # Custom Vanna implementation
├── routes/
│   └── ai_routes.py              # AI endpoints
├── services/
│   └── sql_prompt_service.py    # SQL prompt generation
├── training/
│   ├── core/
│   │   └── openai_chat.py       # OpenAI integration
│   └── vector_stores/
│       └── pinecone_vector.py   # Pinecone integration
├── database/
│   ├── csv_ingestion.py          # CSV to SQLite
│   └── water_data.db             # SQLite database
├── schema/
│   └── water_data.sql            # DDL schema
├── training_sql_data.json        # Question-SQL examples
└── train_vanna.py                # Training script
```

---

## 🧪 Testing

### **Test Database:**
```bash
python database/test_db.py
```

### **Test AI Endpoint:**
```bash
curl -X POST http://localhost:8000/api/v0/ai/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What was the total revenue in 2024?", "run_sql": true}'
```

---

## 📝 Example Questions

Try these natural language questions:

1. "What was the total actual revenue in 2024?"
2. "Show me the revenue variance for Q1 2024"
3. "Which departments had the highest budget variance?"
4. "What is the average operating margin for 2023?"
5. "Show me months with non-revenue water above 25%"
6. "What are the projected revenues for all scenarios?"
7. "Calculate the collection rate trend over the last 12 months"
8. "Which scenarios show healthy financial viability?"

---

## 🔧 Troubleshooting

### **Error: "OPENAI_API_KEY environment variable is required"**
- Make sure `.env` file exists in project root
- Check that `OPENAI_API_KEY` is set correctly

### **Error: "Pinecone API key is required"**
- Set `PINECONE_API_KEY` in `.env` file
- Verify Pinecone account is active

### **Error: "SQLite database not found"**
- Run `python database/csv_ingestion.py` first
- Check that `database/water_data.db` exists

### **Error: "No training data found"**
- Run `python train_vanna.py` to populate Pinecone
- Check that `schema/water_data.sql` and `training_sql_data.json` exist

---

## 🎯 Next Steps

1. ✅ Set up environment variables
2. ✅ Train Vanna AI
3. ✅ Test AI endpoints
4. ✅ Integrate with frontend

**Your AI/ML backend is ready!** 🚀

