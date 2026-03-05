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

                # DEBUG: show all links inside this card
                all_links = card.query_selector_all("a[href]")
                for lnk in all_links:
                    print(f"  DEBUG link: {lnk.get_attribute('href')}")

            if found_older:
                print("  (encontrou artigo mais antigo, parando paginação)")
                break

            time.sleep(2)

        browser.close()

    return articles
