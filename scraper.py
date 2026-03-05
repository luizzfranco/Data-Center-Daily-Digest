from playwright.sync_api import sync_playwright
from datetime import date, timedelta
import time

BASE_URL = "https://www.datacenterdynamics.com"


def get_article_content(page, url):
    try:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(2)
        paragraphs = page.query_selector_all("article p")
        text = " ".join(p.inner_text() for p in paragraphs)
        return text[:4000]
    except Exception as e:
        print(f"  Erro ao buscar conteúdo de {url}: {e}")
        return ""


def get_yesterday_articles():
    yesterday = date.today() - timedelta(days=1)
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

        for page_num in range(1, 4):
            url = BASE_URL + "/en/news/" if page_num == 1 else f"{BASE_URL}/en/news/?page={page_num}"
            print(f"  Verificando página {page_num}: {url}")

            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                time.sleep(3)
            except Exception as e:
                print(f"  Erro ao acessar {url}: {e}")
                break

            cards = page.query_selector_all("article")
            if not cards:
                cards = page.query_selector_all("[class*='ArticleCard'], [class*='article-card'], [class*='card']")

            print(f"  {len(cards)} card(s) encontrado(s)")

            # DEBUG: print date info from first 5 cards
            print("  --- DEBUG: primeiros 5 cards ---")
            for i, card in enumerate(cards[:31]):
                time_tag = card.query_selector("time")
                if time_tag:
                    dt = time_tag.get_attribute("datetime")
                    txt = time_tag.inner_text()
                    print(f"  Card {i+1}: datetime='{dt}' text='{txt}'")
                else:
                    # Try to find any date-like element
                    html = card.inner_html()[:300]
                    print(f"  Card {i+1}: sem <time>. HTML parcial: {html}")
            print("  --- FIM DEBUG ---")

            found_older = False
            for card in cards:
                time_tag = card.query_selector("time")
                article_date = None
                if time_tag:
                    raw = time_tag.get_attribute("datetime")
                    if raw:
                        try:
                            from datetime import datetime
                            article_date = datetime.strptime(raw[:10], "%Y-%m-%d").date()
                        except Exception:
                            pass

                if article_date and article_date < yesterday:
                    found_older = True
                    break

                if article_date != yesterday:
                    continue

                link_tag = card.query_selector("a[href]")
                if not link_tag:
                    continue

                href = link_tag.get_attribute("href")
                if not href:
                    continue

                full_url = href if href.startswith("http") else BASE_URL + href

                if "/en/news/" not in full_url and "/en/analysis/" not in full_url:
                    continue

                title_tag = card.query_selector("h2, h3, h4")
                title = title_tag.inner_text().strip() if title_tag else link_tag.inner_text().strip()

                if any(a["url"] == full_url for a in articles):
                    continue

                articles.append({
                    "title": title,
                    "url": full_url,
                    "date": str(article_date),
                })

            if found_older:
                break

            time.sleep(2)

        print(f"  Buscando conteúdo completo de {len(articles)} artigo(s)...")
        for i, article in enumerate(articles):
            print(f"  [{i+1}/{len(articles)}] {article['title'][:60]}...")
            article["content"] = get_article_content(page, article["url"])
            time.sleep(2)

        browser.close()

    return articles
