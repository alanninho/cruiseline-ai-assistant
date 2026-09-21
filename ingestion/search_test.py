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

model = SentenceTransformer("all-MiniLM-L6-v2")

query = "What is the cancellation policy if I need to change my cruise?"
query_embedding = model.encode(query).tolist()

cur.execute(
    "SELECT text, source_type, source_file, embedding <-> %s::vector AS distance FROM chunks ORDER BY distance LIMIT 5",
    (query_embedding,)
)

for row in cur.fetchall():
    text, source_type, source_file, distance = row
    print(f"[{distance:.3f}] ({source_type}/{source_file})")
    print(text[:200])
    print()

cur.close()
conn.close()