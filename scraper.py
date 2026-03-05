import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
from email.utils import parsedate_to_datetime

BASE_URL = "https://www.datacenterdynamics.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def get_yesterday_articles():
    yesterday = date.today() - timedelta(days=1)
    print(f"  Buscando notícias de {yesterday.strftime('%d/%m/%Y')}...")

    articles = []

    for page_num in range(1, 6):  # up to 5 RSS pages
        url = f"{BASE_URL}/en/rss/" if page_num == 1 else f"{BASE_URL}/en/rss/?page={page_num}"
        print(f"  Verificando RSS página {page_num}...")

        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Erro ao acessar {url}: {e}")
            break

        soup = BeautifulSoup(resp.content, "xml")
        items = soup.find_all("item")
        print(f"  {len(items)} item(s) encontrado(s).")

        if not items:
            break

        found_older = False
        for item in items:
            pub_date_raw = item.find("pubDate")
            if not pub_date_raw:
                continue
            try:
                pub_date = parsedate_to_datetime(pub_date_raw.text).date()
            except Exception:
                continue

            # Stop if we've gone past yesterday
            if pub_date < yesterday:
                found_older = True
                break

            if pub_date != yesterday:
                continue

            title = item.find("title").get_text(strip=True) if item.find("title") else ""
            link = item.find("link").get_text(strip=True) if item.find("link") else ""
            description = item.find("description")
            desc_text = BeautifulSoup(description.text, "html.parser").get_text(strip=True) if description else ""

            if not title or not link:
                continue
            if title.lower().startswith("sponsored"):
                continue
            if any(a["url"] == link for a in articles):
                continue

            print(f"  ✓ {title[:70]}")
            articles.append({
                "title": title,
                "url": link,
                "date": str(pub_date),
                "description": desc_text,
                "content": "",
            })

        if found_older:
            break

    print(f"  Total: {len(articles)} artigo(s) encontrado(s).")
    return articles
