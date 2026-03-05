import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
import time

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

BASE_URL = "https://www.datacenterdynamics.com"


def get_article_content(url):
    """Fetches the full text content of a single article."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # DCD article body is inside article tag
        article_body = soup.find("article")
        if not article_body:
            return ""

        paragraphs = article_body.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs)
        return text[:4000]  # limit to avoid huge payloads
    except Exception as e:
        print(f"  Erro ao buscar conteúdo de {url}: {e}")
        return ""


def parse_article_date(article):
    """Tries to extract a date from an article element."""
    time_tag = article.find("time")
    if time_tag and time_tag.get("datetime"):
        raw = time_tag["datetime"][:10]  # "YYYY-MM-DD"
        try:
            from datetime import datetime
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except Exception:
            return None
    return None


def get_yesterday_articles():
    """Scrapes DCD news page and returns articles published yesterday."""
    yesterday = date.today() - timedelta(days=1)
    articles = []

    # DCD lists news at /en/news/ — we'll check first 3 pages to be safe
    for page in range(1, 4):
        url = f"{BASE_URL}/en/news/" if page == 1 else f"{BASE_URL}/en/news/?page={page}"
        print(f"  Verificando página {page}: {url}")

        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Erro ao acessar {url}: {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")

        # Find all article cards — DCD uses <article> tags in the listing
        cards = soup.find_all("article")
        if not cards:
            # Fallback: look for links with date metadata
            cards = soup.select("[class*='article']") or soup.select("[class*='card']")

        found_older = False
        for card in cards:
            article_date = parse_article_date(card)

            # If we find articles older than yesterday, stop paginating
            if article_date and article_date < yesterday:
                found_older = True
                break

            if article_date != yesterday:
                continue

            # Extract title and link
            link_tag = card.find("a", href=True)
            if not link_tag:
                continue

            title_tag = card.find(["h2", "h3", "h4"])
            title = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)

            href = link_tag["href"]
            full_url = href if href.startswith("http") else BASE_URL + href

            # Skip non-article links
            if "/en/news/" not in full_url and "/en/analysis/" not in full_url:
                continue

            articles.append({
                "title": title,
                "url": full_url,
                "date": str(article_date),
            })

        if found_older:
            break

        time.sleep(1)  # be polite to the server

    # Fetch full content for each article
    print(f"  Buscando conteúdo completo de {len(articles)} artigo(s)...")
    for i, article in enumerate(articles):
        print(f"  [{i+1}/{len(articles)}] {article['title'][:60]}...")
        article["content"] = get_article_content(article["url"])
        time.sleep(1)

    return articles
