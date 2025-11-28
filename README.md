# Simple RAG Prototype README


Objective:
    Build a minimal Retrieval-Augmented Generation (RAG) prototype that answers questions using a small corpus of FAQ documents, and expose it as a local HTTP API callable on your machine (e.g., via curl or Postman). 
    The emphasis is on sound approach, correctness, and clear trade-offs—not production polish.


This RAG (Retrieval-Augmented Generation) system has been  implemented with the following functionality:

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

### 3. Start the HTTP API server

```bash
python run_server.py
```
This script will:
- Load environment variables from `.env` file
- Validate your OpenAI API key is configured
- Display current configuration
- Start the server automatically



### 4. Test the API endpoints

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



## Key Design Decisions & Trade-Offs

### In-memory index vs. external store
    For simplicity and given the small FAQ corpus, everything (chunks, embeddings, 
    and filenames) is kept in memory. This keeps the implementation lightweight and 
    avoids introducing a dependency on a separate vector store. It would need to be 
    revisited for larger corpora or multi-tenant scenarios.

### Single-pass embedding vs. batching/streaming
    All chunk embeddings are created in a single embeddings call at startup. This is 
    acceptable for a small set of FAQ documents; for larger datasets, this would be 
    refactored into batched calls or an offline pre-processing step.

### Cosine similarity via dot product
    Instead of implementing cosine similarity explicitly, embeddings are L2-normalized 
    once and a simple dot product is used. This keeps retrieval fast and mathematically 
    equivalent for ranking purposes.

### Simple, constrained schema and responses
    The API always returns deterministic JSON with two fields: "answer" and "sources". 
    This matches the task spec and makes the contract easy to consume (e.g., by curl 
    or Postman) without extra metadata.

### Fail-fast configuration and initialization
    The service validates OPENAI_API_KEY and the presence of FAQ content at startup. 
    If misconfigured or if no documents are available, it fails immediately rather than 
    serving placeholder or potentially misleading responses. This favors correctness 
    over availability, which is appropriate for a small, local prototype.

### LLM prompting kept intentionally minimal
    The prompts are deliberately short and conservative. They focus on grounding in 
    context and avoiding hallucinations, rather than stylistic richness. For a more 
    advanced system, we could add explicit citation formatting and more structured 
    outputs, but that felt beyond the scope of this exercise.

### Testability
    A RAG_TEST_MODE environment flag is provided to optionally skip preload in 
    automated tests, allowing tests to construct small in-memory corpora without 
    incurring API calls or file I/O on import.

