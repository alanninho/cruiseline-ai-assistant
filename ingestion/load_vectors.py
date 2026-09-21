import json
import psycopg
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

conn = psycopg.connect(
    host="localhost",
    port=5433,
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)
cur = conn.cursor()

cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
cur.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id SERIAL PRIMARY KEY,
        text TEXT NOT NULL,
        source_type TEXT NOT NULL,
        source_file TEXT NOT NULL,
        metadata JSONB,
        embedding VECTOR(384)
    );
""")
conn.commit()

with open("data/processed/corpus.json", "r", encoding="utf-8") as f:
    corpus = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")
texts = [chunk["text"] for chunk in corpus]
embeddings = model.encode(texts, show_progress_bar=True)

for chunk, embedding in zip(corpus, embeddings):
    metadata = {k: v for k, v in chunk.items() if k not in ("id", "text", "source_type", "source_file")}
    cur.execute(
        "INSERT INTO chunks (text, source_type, source_file, metadata, embedding) VALUES (%s, %s, %s, %s, %s)",
        (chunk["text"], chunk["source_type"], chunk["source_file"], json.dumps(metadata), embedding.tolist())
    )

conn.commit()
print(f"Inserted {len(corpus)} chunks into the database")

cur.close()
conn.close()