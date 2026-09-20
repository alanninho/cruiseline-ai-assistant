import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path



Path("data/raw").mkdir(parents=True, exist_ok=True)


def scrape_faq_page(url):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    
    questions = soup.find_all("h3")
    
    data = []
    for q in questions:
        question_text = q.get_text(strip=True)
        answer_parts = []
        for sibling in q.find_next_siblings():
            if sibling.name == "h3":
                break
            if sibling.name == "p":
                answer_parts.append(sibling.get_text(strip=True))
        answer_text = " ".join(answer_parts)
        
        data.append({
            "question": question_text,
            "answer": answer_text,
            "source_url": url
        })
    
    with open("data/raw/cabins_faq_page.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    scrape_faq_page('https://www.msccruisesusa.com/faq/cabins')