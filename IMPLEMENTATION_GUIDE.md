# RAG System Implementation Guide

## ✅ Implementation Status

The RAG (Retrieval-Augmented Generation) system has been **fully implemented** with all required functionality:

### Core Features Implemented
- ✅ **Text chunking**: Splits FAQ documents into ~200 character chunks with word boundaries
- ✅ **Document loading**: Loads all `.md` files from the `faqs/` directory  
- ✅ **Vector embeddings**: Uses OpenAI's `text-embedding-ada-002` for semantic search
- ✅ **Cosine similarity**: L2-normalized embeddings for efficient similarity search
- ✅ **LLM answer generation**: Uses GPT-3.5-turbo with proper prompting and citations
- ✅ **HTTP API**: FastAPI server with required endpoints and validation

### API Endpoints
- `GET /health` → Returns `{"status": "ok"}`
- `POST /ask` → Accepts `{"question": "string", "top_k": number}` and returns `{"answer": "string", "sources": ["file1.md", "file2.md"]}`

### Configuration
All settings are configurable via environment variables:
- `OPENAI_API_KEY` (required)
- `FAQ_DIR` (default: `faqs/`)
- `EMBED_MODEL` (default: `text-embedding-ada-002`)
- `LLM_MODEL` (default: `gpt-3.5-turbo`)
- `CHUNK_SIZE` (default: `200`)
- `TOP_K_DEFAULT` (default: `4`)


## 🚀 How to Run

### 1. Set up environment
```bash
cd RAG_API_Skeleton
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables
Create a `.env` file with your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your-actual-api-key-here" > .env
```

### 3. Test the core RAG system (CLI)
```bash
python rag_core.py
```
This will prompt you for a question and return a JSON response.

### 4. Start the HTTP API server

**Option A: Using the run server script (Recommended)**
```bash
python run_server.py
```
This script will:
- Load environment variables from `.env` file
- Validate your OpenAI API key is configured
- Display current configuration
- Start the server automatically

**Option B: Manual uvicorn command**
```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the API endpoints

**Health check:**
```bash
curl http://localhost:8000/health
```

**Ask a question:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?"}'
```

**Ask with custom top_k:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the PTO policy?", "top_k": 2}'
```

## 📁 File Structure
```
RAG_API_Skeleton/
├── faqs/                    # FAQ documents (copied from parent dir)
│   ├── faq_auth.md         # Authentication FAQ
│   ├── faq_employee.md     # Employee handbook  
│   └── faq_sso.md          # SSO FAQ
├── api_server.py           # FastAPI HTTP server
├── rag_core.py             # Core RAG implementation
├── run_server.py           # Server runner with env validation
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
└── venv/                   # Virtual environment (create this)
```

## 🔧 Implementation Details

### Text Processing
- Chunks text at word boundaries to maintain readability
- Handles empty documents gracefully
- Preserves source file mapping for citations

### Vector Search
- Uses OpenAI embeddings API with batching
- L2-normalizes embeddings for cosine similarity via dot product
- Retrieves top-k most similar chunks

### Answer Generation
- System prompt ensures answers stay within provided context
- Temperature=0 for deterministic responses
- Includes source file citations
- Handles API errors gracefully

### Error Handling
- Validates input (non-empty questions, reasonable top_k)
- Proper HTTP status codes (200, 400, 500)
- Fails fast on missing API key
- Graceful fallbacks for missing documents

## 🧪 Sample Questions to Test
- "How do I reset my password?"
- "What is the unlimited PTO policy?"
- "How do I enable SSO?"
- "What is the equity vesting schedule?"
