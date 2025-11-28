
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from rag_core import ask_faq_core

app = FastAPI(title="FAQ RAG API", version="1.0.0")

class AskBody(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: int = Field(4, ge=1, le=10)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(body: AskBody):
    try:
        result = ask_faq_core(body.question.strip(), top_k=body.top_k)
        return {"answer": result["answer"], "sources": result["sources"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        # Don't leak internals
        raise HTTPException(status_code=500, detail="Internal error")
