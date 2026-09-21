import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("data/processed/corpus.json", "r", encoding="utf-8") as f:
    corpus = json.load(f)

texts = [chunk["text"] for chunk in corpus]
embeddings = model.encode(texts, show_progress_bar=True)

print(f"Number of embeddings: {len(embeddings)}")
print(f"Embedding shape: {embeddings.shape}")