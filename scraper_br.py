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


def get_yesterday_articles_br(target_date=None):
    yesterday = target_date if target_date else date.today() - timedelta(days=1)
    print(f"  [BR] Buscando notícias de {yesterday.strftime('%d/%m/%Y')}...")
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
            locale="pt-BR",
        )
        page = context.new_page()
        stealth_sync(page)

        for page_num in range(1, 6):
            url = BASE_URL + "/br/news/" if page_num == 1 else f"{BASE_URL}/br/news/?page={page_num}"
            print(f"  [BR] Verificando página {page_num}...")

            if not goto_with_retry(page, url):
                print(f"  [BR] Não foi possível acessar {url}. Pulando.")
                continue

            time.sleep(3)

            cards = page.query_selector_all("article")
            print(f"  [BR] {len(cards)} card(s) encontrado(s)")

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

                if article_date != yesterday:
                    continue

                link_tag = card.query_selector("a[href]")
                if not link_tag:
                    continue

                href = link_tag.get_attribute("href")
                if not href:
                    continue

                full_url = href if href.startswith("http") else BASE_URL + href

                if not full_url.startswith(BASE_URL + "/br/"):
                    continue

                title_tag = card.query_selector("h2, h3, h4")
                title = title_tag.inner_text().strip() if title_tag else link_tag.inner_text().strip()

                if not title or title.lower().startswith("sponsored") or title.lower().startswith("patrocinado"):
                    continue
                if any(a["url"] == full_url for a in articles):
                    continue

                print(f"  [BR] ✓ {title[:70]}")
                articles.append({
                    "title": title,
                    "url": full_url,
                    "date": str(article_date),
                    "description": "",
                    "content": "",
                })

            # Stop if the newest article on this page is older than yesterday
            all_dates = []
            for card2 in page.query_selector_all("article"):
                t2 = card2.query_selector("time")
                if t2 and t2.get_attribute("datetime"):
                    try:
                        d2 = datetime.strptime(t2.get_attribute("datetime")[:10], "%Y-%m-%d").date()
                        all_dates.append(d2)
                    except Exception:
                        pass
            if all_dates and max(all_dates) < yesterday:
                print(f"  [BR] Página {page_num} não tem artigos de ontem. Parando.")
                break

            time.sleep(2)

        print(f"  [BR] Total: {len(articles)} artigo(s) encontrado(s).")
        browser.close()

    return articles
