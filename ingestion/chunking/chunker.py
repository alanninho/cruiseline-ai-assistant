import json
import re

def fixed_size_chunk(text, chunk_size=500, overlap=50):
    # slide a window across `text`, step = chunk_size - overlap
    # each chunk is text[i : i+chunk_size]
    result = []
    step = chunk_size - overlap
    i = 0
    while i < len(text):
        result.append(text[i:i + chunk_size])
        i += step
    return result

def paragraph_chunk(text, min_chunk_size=100):
    # split on double newlines (or a regex for numbered clauses)
    # merge any paragraph under `min_chunk_size` into the next one,
    # so you don't end up with tiny orphan chunks
    ...


def clause_chunk(text):
    pattern = r'(?=\n?\•?\s*\d{1,2}\.\s+[A-Z])'
    pieces = re.split(pattern, text)
    result = []
    for p in pieces:
        stripped = p.strip()
        if stripped != '':
            result.append(stripped)
    return result


def merge_short_chunks(chunks, min_length=50):
    merged = []
    buffer = ""
    for chunk in chunks:
        buffer += (" " + chunk if buffer else chunk)
        if len(buffer) >= min_length:
            merged.append(buffer)
            buffer = ""
    if buffer:
        merged.append(buffer)
    return merged


def qmark_faq_chunk(text):
    pattern = r'(?=\nQ\s*[A-Z])'
    pieces = re.split(pattern, text)
    # same filtering as clause_chunk: strip, drop empties
    result = []
    for p in pieces:
        stripped = p.strip()
        if stripped != '':
            result.append(stripped)
    return result


def _flush_excursion(excursion):
    body_text = "\n".join(excursion["body"]).strip()

    duration = None
    if body_text.startswith("Duration:"):
        first_line, _, rest = body_text.partition("\n")
        duration = first_line.replace("Duration:", "").strip()
        body_text = rest.strip()

    return {
        "excursion_code": excursion["code"],
        "title": excursion["title"],
        "port": excursion["port"],
        "duration": duration,
        "description": body_text
    }


def excursion_chunk(text):
    excursion_pattern = re.compile(r'^(?=[A-Z0-9]*[A-Z])([A-Z0-9]{2,10})\s*[-–]\s*(.+)$')
    lines = text.split('\n')

    result = []
    current_port = None
    current_excursion = None

    for line in lines:
        stripped = line.strip()
        match = excursion_pattern.match(stripped)

        if match:
            if current_excursion is not None:
                result.append(_flush_excursion(current_excursion))
            current_excursion = {
                "code": match.group(1),
                "title": match.group(2),
                "port": current_port,
                "body": []
            }
        elif stripped.isupper() and stripped and len(stripped.split()) <= 6:
            current_port = stripped
        elif current_excursion is not None:
            current_excursion["body"].append(line)

    if current_excursion is not None:
        result.append(_flush_excursion(current_excursion))

    return result


if __name__ == '__main__':
    with open('data/raw/excursions_descriptions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    chunks = excursion_chunk(data['text'])
    
    sample = chunks[49]
    print("Code:", sample["excursion_code"])
    print("Port:", sample["port"])
    print("Title:", sample["title"])
    print("Duration:", sample["duration"])
    print("Description:", sample["description"])