import sys
from scraper import get_yesterday_articles
from scraper_br import get_yesterday_articles_br
from summarizer import summarize_articles
from mailer import send_digest
from sheets import save_to_sheets
from datetime import date, timedelta, datetime


def main():
    if len(sys.argv) > 1:
        target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
    else:
        target_date = date.today() - timedelta(days=1)

    print(f"Buscando notícias de {target_date.strftime('%d/%m/%Y')}...")

    articles_br = get_yesterday_articles_br(target_date)
    articles_global = get_yesterday_articles(target_date)

    if not articles_br and not articles_global:
        print("Nenhuma notícia encontrada. Encerrando.")
        return

    print(f"{len(articles_br)} notícia(s) BR e {len(articles_global)} global(is) encontrada(s). Gerando resumos...")
    digest = summarize_articles(articles_global, articles_br, target_date)

    print("Enviando e-mail...")
    send_digest(digest, target_date)
    print("E-mail enviado com sucesso!")

    print("Salvando no Google Sheets...")
    save_to_sheets(articles_br, articles_global, digest)


if __name__ == "__main__":
    main()
