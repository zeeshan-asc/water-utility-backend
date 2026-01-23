# 🔐 Environment Variables Setup

Create a `.env` file in your project root with these variables:

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

## Getting API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy and paste into `.env`

### Pinecone API Key
1. Go to https://app.pinecone.io/
2. Sign up or log in
3. Create a new project
4. Copy API key and environment
5. Paste into `.env`

## Security Note

**Never commit `.env` file to git!**
- It's already in `.gitignore`
- Keep your API keys secret
- Use different keys for development/production


