import requests
from pypdf import PdfReader
import json
from pathlib import Path



Path("data/raw").mkdir(parents=True, exist_ok=True)


def scrape_pdf(url, filename):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    pdf_path = f"data/raw/{filename}.pdf"
    with open(pdf_path, "wb") as f:
        f.write(response.content)

    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    data = {
        "source_url": url,
        "page_count": len(reader.pages),
        "text": text
    }

    with open(f"data/raw/{filename}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(reader.pages)} pages, {len(text)} characters")


if __name__ == '__main__':
    scrape_pdf(
    'https://www.mscbook.com/images/sdl/Terms%20and%20Conditions-121318.pdf',
    'shore_excursions_terms'
)
    scrape_pdf(
    'https://www.mscbook.com/pages/sdl/img/B2B_TA_29210_05_MSC_FOR_ME_PHASE_2_TRADE_KIT_FAQ.pdf',
    'msc_for_me_zoe_faq'
)