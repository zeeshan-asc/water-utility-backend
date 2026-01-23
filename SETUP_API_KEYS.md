# 🔑 Quick API Keys Setup Guide

## Step 1: Get Your API Keys

### OpenAI API Key
1. Visit: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### Pinecone API Key
1. Visit: https://app.pinecone.io/
2. Sign up or log in (free tier available)
3. Create a new project
4. Go to API Keys section
5. Copy your API key and environment (e.g., `us-east-1`)

## Step 2: Update .env File

Edit the `.env` file in your project root and replace the placeholder values:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Pinecone Configuration
PINECONE_API_KEY=your-actual-pinecone-key-here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=aquasentinel-index

# Database Configuration
SQLITE_DB_PATH=database/water_data.db
```

## Step 3: Verify Setup

After updating `.env`, verify the keys are loaded:

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'); print('Pinecone:', 'SET' if os.getenv('PINECONE_API_KEY') else 'NOT SET')"
```

## Step 4: Run Training

Once keys are set, run:

```bash
python train_vanna.py
```

---

**Note:** The `.env` file is already in `.gitignore` so your keys won't be committed to git.

