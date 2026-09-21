import json
from ingestion.chunking.chunker import clause_chunk, merge_short_chunks, qmark_faq_chunk, excursion_chunk
from ingestion.parsers.table_extractor import parse_technical_sheet


def load_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)['text']

corpus = []
chunk_id = 0

def add_chunks(texts, source_type, source_file):
    global chunk_id
    for text in texts:
        chunk_id += 1
        corpus.append({
            "id": chunk_id,
            "text": text,
            "source_type": source_type,
            "source_file": source_file
        })

# Legal documents
text = load_text("data/raw/booking_terms.json")
chunks = merge_short_chunks(clause_chunk(text))
add_chunks(chunks, "legal", "booking_terms")

# Numbered FAQs (reuse clause_chunk)
for f in ["ocean_cay_faq", "msc_for_me_zoe_faq"]:
    text = load_text(f"data/raw/{f}.json")
    chunks = clause_chunk(text)
    add_chunks(chunks, "faq", f)

# Q-prefixed FAQ
text = load_text("data/raw/general_faqs.json")
chunks = qmark_faq_chunk(text)
add_chunks(chunks, "faq", "general_faqs")

# Excursions (structured records, not plain strings)
text = load_text("data/raw/excursions_descriptions.json")
excursions = excursion_chunk(text)
for exc in excursions:
    chunk_id += 1
    exc_text = f"{exc['title']} ({exc['port']}). Duration: {exc['duration']}. {exc['description']}"
    corpus.append({
        "id": chunk_id,
        "text": exc_text,
        "source_type": "excursion",
        "source_file": "excursions_descriptions",
        "port": exc["port"],
        "excursion_code": exc["excursion_code"]
    })
    
    
# Technical sheets (structured records)
for ship in ["divina", "splendida", "virtuosa", "seascape"]:
    text = load_text(f"data/raw/{ship}_technical_sheet.json")
    venues = parse_technical_sheet(text, ship)
    for v in venues:
        if v["section"] is None or v["name"].strip() == "":
            continue
        chunk_id += 1
        v_text = f"{v['name']} is located on {v['deck']}."
        if v["seats"]:
            v_text += f" Seats: {v['seats']}."
        if v["surface"]:
            v_text += f" Surface: {v['surface']} m²."
        corpus.append({
            "id": chunk_id,
            "text": v_text,
            "source_type": "venue",
            "source_file": f"{ship}_technical_sheet",
            "ship": ship,
            "section": v["section"]
        })


with open("data/processed/corpus.json", "w", encoding="utf-8") as f:
    json.dump(corpus, f, indent=2, ensure_ascii=False)

print(f"Saved corpus: {len(corpus)} chunks")