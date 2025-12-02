
# Simple RAG Prototype

A lightweight Retrieval-Augmented Generation (RAG) API built with **Python**, **FastAPI**, and **OpenAI**.
It loads FAQ documents, embeds them for semantic search, retrieves the most relevant content, and generates grounded answers—avoiding hallucinations by ensuring responses come *only* from the provided documents.

This prototype exposes a simple HTTP API suitable for local testing, demos, or extending into a more robust RAG service.

---

## 🚀 Features

### **Core Functionality**

* **Text chunking** — Splits FAQ files into ~200-character, word-aligned chunks
* **Document ingestion** — Loads all `.md` files from the `faqs/` directory
* **Vector embeddings** — Uses `text-embedding-ada-002` for semantic search
* **Similarity search** — Fast cosine similarity via L2-normalized embeddings
* **LLM answer generation** — Uses GPT-3.5-turbo with citations
* **FastAPI HTTP API** — Typed request/response validation + health checks

### **Endpoints**

| Method | Path      | Description                                         |
| ------ | --------- | --------------------------------------------------- |
| GET    | `/health` | Service health indicator                            |
| POST   | `/ask`    | Ask a question; returns answer + cited source files |

Example request:

```json
{
  "question": "How do I reset my password?",
  "top_k": 4
}
```

---

## ⚙️ Configuration

All settings are controlled through environment variables:

| Variable         | Default                  | Description                        |
| ---------------- | ------------------------ | ---------------------------------- |
| `OPENAI_API_KEY` | —                        | **Required**                       |
| `FAQ_DIR`        | `faqs/`                  | Directory containing FAQ documents |
| `EMBED_MODEL`    | `text-embedding-ada-002` | Embedding model                    |
| `LLM_MODEL`      | `gpt-3.5-turbo`          | LLM for answer generation          |
| `CHUNK_SIZE`     | `200`                    | Chunk size in characters           |
| `TOP_K_DEFAULT`  | `4`                      | Default number of retrieved chunks |
| `RAG_TEST_MODE`  | `false`                  | Skips preload for tests            |

---

## 🛠️ Installation & Running

### **1. Set up a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **2. Add environment variables**

Create `.env`:

```bash
echo "OPENAI_API_KEY=your-api-key" > .env
```

### **3. Start the API server**

```bash
python run_server.py
```

This will:

* Load `.env`
* Validate your OpenAI key
* Load and embed FAQ documents
* Start FastAPI on `http://localhost:8000`

---

## 🧪 Testing the API

### Health check

```bash
curl http://localhost:8000/health
```

### Ask a question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I reset my password?"}'
```

### Custom `top_k`

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the PTO policy?", "top_k": 2}'
```

---

## 📁 Project Structure

```
simple-rag-api-prototype/
├── faqs/                 # FAQ markdown documents
├── api_server.py         # FastAPI HTTP server
├── rag_core.py           # Core RAG logic (chunking, embeddings, retrieval)
├── run_server.py         # Startup wrapper + env validation
├── requirements.txt
└── .env                  # Environment variables (not committed)
```

---

## 🔧 Implementation Details

### **Text Processing**

* Chunks on word boundaries for readability
* Tracks chunk-to-file mapping for citation output
* Gracefully handles empty or missing docs

### **Embedding & Search**

* Embeddings generated once at startup (in-memory index)
* L2-normalized vectors enable cosine similarity via dot product
* Retrieves top-k most semantically similar chunks

### **LLM Answer Generation**

* Strict system prompt prevents hallucination
* `temperature=0` ensures determinism
* Returns both the answer and list of source files

### **Error Handling**

* Validates questions and top-k values
* Proper HTTP status codes (400/500)
* Fails fast if API key or FAQ directory is missing

---

## 🧪 Sample Prompts

Try questions like:

* "How do I reset my password?"
* "What is the unlimited PTO policy?"
* "How do I enable SSO?"
* "What is the equity vesting schedule?"

---

## 🧠 Design Decisions & Trade-offs

* **In-memory index** keeps the system simple; suitable for small corpora
* **Single-pass embedding** at startup avoids repeated API calls
* **Minimal prompting** focuses on accuracy over style
* **Fail-fast startup** avoids serving incomplete/misleading answers
* **Optional test mode** supports fast unit testing without API calls

---

## 📌 Future Improvements (Optional Enhancements)

If you want, you could add a section like this to make the project feel more forward-looking.

Potential next steps:

* Add in Datadog LLM observability
* Swap in a real vector DB (e.g., Chroma, Weaviate, Pinecone)
* Support PDF ingestion
* Add citation highlighting or snippet extraction
* Add async embedding generation with concurrency
* Allow streaming answers
* Add Dockerfile + Compose setup

---

## About

A simple, extensible RAG API prototype demonstrating retrieval, semantic search, and grounded LLM answering using FastAPI and OpenAI.
