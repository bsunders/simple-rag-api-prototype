import os
import json
from typing import Dict, List, Tuple
from pathlib import Path

import numpy as np
#from tqdm import tqdm
from openai import OpenAI

# --- Config ---
FAQ_DIR = os.getenv("FAQ_DIR", str(Path(__file__).parent / "faqs"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-ada-002")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "200"))
TOP_K_DEFAULT = int(os.getenv("TOP_K_DEFAULT", "4"))

# Initialize the OpenAI client (fail fast if key missing)
_API_KEY = os.getenv("OPENAI_API_KEY")
if not _API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")
client = OpenAI(api_key=_API_KEY)

# Globals (preloaded at import)
_CHUNKS: List[str] = []
_SOURCES: List[str] = []
_CHUNK_EMBEDS: np.ndarray | None = None  # shape: (N, d)
_READY: bool = False


# ---------------- Core utilities ----------------
def _chunk_text(text: str, size: int = CHUNK_SIZE) -> List[str]:
    """Split text into fixed-size chunks and return the list of chunks."""
    if not text.strip():
        return []
    
    # Simple chunking by characters with word boundaries
    chunks = []
    words = text.split()
    current_chunk = ""
    
    for word in words:
        # If adding this word would exceed size, save current chunk and start new one
        if len(current_chunk) + len(word) + 1 > size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = word
        else:
            if current_chunk:
                current_chunk += " " + word
            else:
                current_chunk = word
    
    # Add the last chunk if it exists
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def _load_and_chunk_faqs(faq_dir: str) -> Tuple[List[str], List[str]]:
    """Load *.md files, chunk each, and return (chunks, matching_source_filenames)."""
    chunks = []
    sources = []
    
    faq_path = Path(faq_dir)
    if not faq_path.exists():
        print(f"Warning: FAQ directory {faq_dir} does not exist")
        return chunks, sources
    
    # Find all .md files in the directory
    md_files = list(faq_path.glob("*.md"))
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chunk the content
            file_chunks = _chunk_text(content)
            
            # Add chunks and corresponding source filenames
            chunks.extend(file_chunks)
            sources.extend([md_file.name] * len(file_chunks))
            
        except Exception as e:
            print(f"Warning: Could not read {md_file}: {e}")
            continue
    
    return chunks, sources

def _embed_texts(texts: List[str]) -> np.ndarray:
    """Create embeddings for texts and return a (N, d) float32 numpy array."""
    if not texts:
        return np.array([], dtype=np.float32).reshape(0, 1536)  # ada-002 has 1536 dims
    
    try:
        # Create embeddings using OpenAI API
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=texts
        )
        
        # Extract embeddings and convert to numpy array
        embeddings = np.array([item.embedding for item in response.data], dtype=np.float32)
        return embeddings
        
    except Exception as e:
        print(f"Error creating embeddings: {e}")
        raise

def _embed_query(q: str) -> np.ndarray:
    """Create an embedding for the query and return a (d,) float32 vector."""
    try:
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=[q]  # API expects a list
        )
        
        # Extract the single embedding and return as 1D array
        embedding = np.array(response.data[0].embedding, dtype=np.float32)
        return embedding
        
    except Exception as e:
        print(f"Error creating query embedding: {e}")
        raise

def _generate_answer(context: str, question: str) -> str:
    """Call the chat model to answer using only context and cite filenames."""
    system_prompt = """You are a helpful assistant that answers questions based only on the provided context. 

Rules:
1. Answer using ONLY the information provided in the context below
2. If the context doesn't contain enough information to answer the question, say so
3. Be concise and direct
4. Mention which files contain the relevant information when possible
5. Do not make up information not present in the context"""

    user_prompt = f"""Context:
{context}

Question: {question}

Please provide a helpful answer based only on the context above."""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,  # Deterministic responses
            max_tokens=300  # Keep answers concise
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "Sorry, I encountered an error while generating the answer."

# ---------------- Public API ----------------
def ask_faq_core(question: str, top_k: int = TOP_K_DEFAULT) -> Dict[str, object]:
    q = (question or "").strip()
    if not q:
        raise ValueError("question is required")
    if top_k <= 0:
        top_k = TOP_K_DEFAULT

    # If not yet implemented, return a safe placeholder so wrappers run.
    if not _READY or _CHUNK_EMBEDS is None or len(_CHUNKS) == 0:
        raise RuntimeError("RAG system is not initialized or no FAQ documents are loaded.")


    q_emb = _embed_query(q)

    sims = _CHUNK_EMBEDS @ q_emb  # cosine if rows are normalized
    top_idx = np.argsort(sims)[-top_k:][::-1]
    top_files = [_SOURCES[i] for i in top_idx]
    context_parts = [f"From {_SOURCES[i]}:\n{_CHUNKS[i]}" for i in top_idx]
    context = "\n\n".join(context_parts)

    answer = _generate_answer(context, q)
    distinct_sources = sorted(list({f for f in top_files}))
    sources_out = distinct_sources[:2] if len(distinct_sources) >= 2 else distinct_sources
    return {"answer": answer, "sources": sources_out}

# ---------------- Module preload ----------------
def _preload() -> None:
    """Load and chunk FAQs, compute embeddings, L2-normalize rows, assign globals."""
    global _CHUNKS, _SOURCES, _CHUNK_EMBEDS, _READY
    
    print("Loading and processing FAQ documents...")
    
    # Load and chunk the FAQ files
    chunks, sources = _load_and_chunk_faqs(FAQ_DIR)
    
    if not chunks:
        msg = f"No FAQ markdown chunks found in directory: {FAQ_DIR}"
        print(f"ERROR: {msg}")
        # Fail fast so the API doesn't serve bogus answers
        raise RuntimeError(msg)
    
    print(f"Found {len(chunks)} chunks from {len(set(sources))} files")
    
    # Create embeddings for all chunks
    print("Creating embeddings...")
    embeddings = _embed_texts(chunks)
    
    # L2-normalize embeddings for cosine similarity (dot product = cosine when normalized)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized_embeddings = embeddings / (norms + 1e-8)  # Add small epsilon to avoid division by zero
    
    # Assign to global variables
    _CHUNKS = chunks
    _SOURCES = sources
    _CHUNK_EMBEDS = normalized_embeddings
    _READY = True

    print(f"Initialization complete! Ready to answer questions.")

# Run preload at import time (enable after implementation)
# Skip preload in test mode
if not os.getenv("RAG_TEST_MODE"):
    _preload()

# ---------------- Optional CLI runner ----------------
def main_cli():
    q = input("Enter your question: ")
    print(json.dumps(ask_faq_core(q), indent=2))

if __name__ == "__main__":
    main_cli()
