import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
from email.utils import parsedate_to_datetime

RSS_URL = "https://www.datacenterdynamics.com/en/rss/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def get_yesterday_articles():
    """Fetches DCD RSS feed and returns articles published yesterday."""
    yesterday = date.today() - timedelta(days=1)
    print(f"  Buscando notícias de {yesterday.strftime('%d/%m/%Y')}...")

    try:
        resp = requests.get(RSS_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"  Erro ao acessar RSS: {e}")
        return []

    soup = BeautifulSoup(resp.content, "xml")
    items = soup.find_all("item")
    print(f"  {len(items)} item(s) encontrado(s) no RSS.")

    articles = []
    for item in items:
        pub_date_raw = item.find("pubDate")
        if not pub_date_raw:
            continue

        try:
            pub_date = parsedate_to_datetime(pub_date_raw.text).date()
        except Exception:
            continue

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

        print(f"  ✓ {title[:70]}")
        articles.append({
            "title": title,
            "url": link,
            "date": str(pub_date),
            "description": desc_text,
        })

    print(f"  Total: {len(articles)} artigo(s) de ontem encontrado(s).")
    return articles
