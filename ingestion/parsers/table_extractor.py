import requests, json, re, pypdf

def is_numeric(token):
    # a token like "1.511" or "42" should return True
    # a token like "Zeus" or "/" should return False
    token = token.replace('.', '')
    return token.isdigit()



def find_deck_start(tokens):
    for i in range(len(tokens) - 1):
        current = tokens[i]
        next_token = tokens[i + 1]
        if is_numeric(current) and not is_numeric(next_token):
            return i
    return None


def find_name_end(tokens):
    for i in range(len(tokens)):
        if is_numeric(tokens[i]):
            return i
    return None


def parse_venue_line(line):
    tokens = line.split()
    name_end = find_name_end(tokens)
    if name_end is None:
        return None  # no numbers at all — not a data row (e.g. a section header)
    
    name = " ".join(tokens[:name_end])
    rest = tokens[name_end:]
    
    deck_start = find_deck_start(rest)
    if deck_start is None:
        return None  # couldn't find where the deck starts — malformed line
    
    values = rest[:deck_start]
    deck = " ".join(rest[deck_start:])
    
    return {
        "name": name,
        "values": values,
        "deck": deck
    }


def assign_seats_surface(values):
    if len(values) >= 2:
        return {"seats": values[-2], "surface": values[-1]}
    elif len(values) == 1:
        return {"seats": None, "surface": None, "value": values[0]}
    else:
        return {"seats": None, "surface": None}


KNOWN_SECTIONS = [
    "VARIOUS SERVICES", "CONFERENCE ROOMS", "RESTAURANTS",
    "BARS / LOUNGES", "OUTDOOR BARS", "SHOPS", "ENTERTAINMENT",
    "FAMILY ENTERTAINMENT", "MSC AUREA SPA", "SPORT & FITNESS", "POOLS"
]


def parse_technical_sheet(text, ship_name):
    lines = text.split('\n')
    result = []
    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        matched_section = None
        for section in KNOWN_SECTIONS:
            if stripped.startswith(section):
                matched_section = section
                break

        if matched_section:
            current_section = matched_section
            continue

        row = parse_venue_line(stripped)
        if row is not None:
            row.update(assign_seats_surface(row["values"]))
            row["section"] = current_section
            row["ship"] = ship_name
            result.append(row)

    return result


if __name__ == '__main__':
    ships = ["divina", "splendida", "virtuosa", "seascape"]
    all_venues = []

    for ship in ships:
        with open(f'data/raw/{ship}_technical_sheet.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        venues = parse_technical_sheet(data['text'], ship)
        all_venues.extend(venues)
        print(f"{ship}: {len(venues)} venues parsed")
    
    clean_venues = [
    v for v in all_venues
    if v["section"] is not None and v["name"].strip() != ""
]

    with open('data/raw/technical_sheets_parsed.json', 'w', encoding='utf-8') as f:
        json.dump(clean_venues, f, indent=2, ensure_ascii=False)

    print(f"Total: {len(clean_venues)} venues across {len(ships)} ships")