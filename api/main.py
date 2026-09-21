from fastapi import FastAPI
from pydantic import BaseModel
import psycopg
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")

@app.get("/health")
def health_check():
    return {"status": "ok"}

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

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
        (query_embedding, request.top_k)
    )

    results = []
    for row in cur.fetchall():
        text, source_type, source_file, metadata, distance = row
        results.append({
            "text": text,
            "source_type": source_type,
            "source_file": source_file,
            "metadata": metadata,
            "distance": round(distance, 3)
        })

    cur.close()
    conn.close()

    return {"question": request.question, "results": results}