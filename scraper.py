from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from datetime import date, timedelta, datetime
import time

BASE_URL = "https://www.datacenterdynamics.com"


def goto_with_retry(page, url, retries=3, timeout=90000):
    for attempt in range(1, retries + 1):
        try:
            page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            return True
        except Exception as e:
            print(f"  Tentativa {attempt}/{retries} falhou: {e}")
            if attempt < retries:
                time.sleep(5)
    return False


def get_article_tags(page, url):
    try:
        if not goto_with_retry(page, url):
            return []
        time.sleep(2)
        meta = page.query_selector('meta[itemprop="keywords"]')
        if not meta:
            return []
        content = meta.get_attribute("content")
        if not content:
            return []
        return [t.strip() for t in content.split(",") if t.strip()]
    except Exception as e:
        print(f"  Erro ao coletar tags de {url}: {e}")
        return []


def get_yesterday_articles(target_date=None):
    yesterday = target_date if target_date else date.today() - timedelta(days=1)
    print(f"  Buscando notícias de {yesterday.strftime('%d/%m/%Y')}...")
    articles = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        page = context.new_page()
        stealth_sync(page)

        for page_num in range(1, 6):
            url = BASE_URL + "/en/news/" if page_num == 1 else f"{BASE_URL}/en/news/?page={page_num}"
            print(f"  Verificando página {page_num}...")

            if not goto_with_retry(page, url):
                print(f"  Não foi possível acessar {url}. Pulando.")
                continue

            time.sleep(3)

            cards = page.query_selector_all("article")
            print(f"  {len(cards)} card(s) encontrado(s)")

            # Collect all article data from this page first (no navigation)
            page_articles = []
            all_dates = []

            for card in cards:
                time_tag = card.query_selector("time")
                article_date = None
                if time_tag:
                    raw = time_tag.get_attribute("datetime")
                    if raw:
                        try:
                            article_date = datetime.strptime(raw[:10], "%Y-%m-%d").date()
                        except Exception:
                            pass

                if article_date:
                    all_dates.append(article_date)

                if article_date != yesterday:
                    continue

                link_tag = card.query_selector("a[href]")
                if not link_tag:
                    continue

                href = link_tag.get_attribute("href")
                if not href:
                    continue

                full_url = href if href.startswith("http") else BASE_URL + href

                if not full_url.startswith(BASE_URL + "/en/"):
                    continue

                title_tag = card.query_selector("h2, h3, h4")
                title = title_tag.inner_text().strip() if title_tag else link_tag.inner_text().strip()

                if not title or title.lower().startswith("sponsored"):
                    continue
                if any(a["url"] == full_url for a in articles) or any(a["url"] == full_url for a in page_articles):
                    continue

                print(f"  ✓ {title[:70]}")
                page_articles.append({
                    "title": title,
                    "url": full_url,
                    "date": str(article_date),
                    "description": "",
                    "content": "",
                    "tags": [],
                })

            # Now fetch tags for each article (navigation happens here, after iteration)
            for article in page_articles:
                tags = get_article_tags(page, article["url"])
                article["tags"] = tags
                print(f"  Tags de '{article['title'][:40]}': {tags}")
                time.sleep(1)

            articles.extend(page_articles)

            if all_dates and max(all_dates) < yesterday:
                print(f"  Página {page_num} não tem artigos de ontem ou mais recentes. Parando.")
                break

            time.sleep(2)

        print(f"  Total: {len(articles)} artigo(s) encontrado(s).")
        browser.close()

    return articles
