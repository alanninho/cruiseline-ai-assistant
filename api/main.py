from fastapi import FastAPI
from pydantic import BaseModel
import psycopg
import os
import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, CrossEncoder

load_dotenv()

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list

SIMILARITY_THRESHOLD = 1.2

@app.post("/query")
def query(request: QueryRequest):
    conn = psycopg.connect(
        host="localhost",
        port=5433,
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    cur = conn.cursor()

    query_embedding = model.encode(request.question).tolist()

    cur.execute(
        "SELECT text, source_type, source_file, metadata, embedding <-> %s::vector AS distance FROM chunks ORDER BY distance LIMIT %s",
        (query_embedding, 15)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Guardrail: if even the best match is too far, don't hallucinate
    if not rows or rows[0][4] > SIMILARITY_THRESHOLD:
        return {
            "question": request.question,
            "answer": "I don't have enough information to answer that question confidently.",
            "sources": []
        }

    pairs = [(request.question, row[0]) for row in rows]
    scores = reranker.predict(pairs)
    reranked = sorted(zip(rows, scores), key=lambda x: x[1], reverse=True)[:request.top_k]
    rows = [r[0] for r in reranked]
    context_chunks = [row[0] for row in rows]
    context = "\n\n---\n\n".join(context_chunks)

    prompt = f"""You are a helpful cruise assistant. Answer the question using ONLY the context below. If the context doesn't contain the answer, say so.

Context:
{context}

Question: {request.question}

Answer:"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3.2:3b", "prompt": prompt, "stream": False}
    )
    answer = response.json()["response"]

    sources = [
        {"source_type": row[1], "source_file": row[2], "distance": round(row[4], 3)}
        for row in rows
    ]

    return {"question": request.question, "answer": answer, "sources": sources}