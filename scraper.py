import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
from email.utils import parsedate_to_datetime

RSS_URL = "https://www.datacenterdynamics.com/en/rss/"
BASE_URL = "https://www.datacenterdynamics.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def get_article_content(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        paragraphs = soup.select("article p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs)
        return text[:4000]
    except Exception as e:
        print(f"  Erro ao buscar conteúdo de {url}: {e}")
        return ""


def get_yesterday_articles():
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

    # Also scrape news page directly to catch articles not in RSS
    print(f"  Complementando com scraping direto...")
    for page_num in range(1, 4):
        url = BASE_URL + "/en/news/" if page_num == 1 else f"{BASE_URL}/en/news/?page={page_num}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Erro ao acessar {url}: {e}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        found_older = False

        for card in soup.find_all("article"):
            time_tag = card.find("time")
            article_date = None
            if time_tag and time_tag.get("datetime"):
                try:
                    from datetime import datetime
                    article_date = datetime.strptime(time_tag["datetime"][:10], "%Y-%m-%d").date()
                except Exception:
                    pass

            if article_date and article_date < yesterday:
                found_older = True
                break

            if article_date != yesterday:
                continue

            link_tag = card.find("a", href=True)
            if not link_tag:
                continue

            href = link_tag["href"]
            full_url = href if href.startswith("http") else BASE_URL + href

            if not full_url.startswith(BASE_URL + "/en/"):
                continue

            title_tag = card.find(["h2", "h3", "h4"])
            title = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)

            if not title or title.lower().startswith("sponsored"):
                continue
            if any(a["url"] == full_url for a in articles):
                continue

            print(f"  ✓ {title[:70]}")
            articles.append({
                "title": title,
                "url": full_url,
                "date": str(article_date),
                "description": "",
            })

        if found_older:
            break

    print(f"  Total: {len(articles)} artigo(s) encontrado(s).")

    print(f"  Buscando conteúdo completo...")
    for i, article in enumerate(articles):
        print(f"  [{i+1}/{len(articles)}] {article['title'][:60]}...")
        article["content"] = get_article_content(article["url"])

    return articles
