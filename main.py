import sys
from scraper import get_yesterday_articles
from scraper_br import get_yesterday_articles_br
from tagger import tag_articles
from mailer import send_digest
from sheets import save_to_sheets
from datetime import date, timedelta, datetime


def build_digest(articles_br, articles_global):
    """Monta a estrutura esperada pelo mailer a partir dos artigos tagueados."""
    digest = {}

    if articles_br:
        digest["br"] = [
            {"titulo": a["title"], "url": a["url"], "tags": a.get("tags", [])}
            for a in articles_br
        ]
    else:
        digest["br"] = None

    if articles_global:
        digest["global"] = [
            {"titulo": a["title"], "url": a["url"], "tags": a.get("tags", [])}
            for a in articles_global
        ]
    else:
        digest["global"] = None

    return digest


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

    print(f"{len(articles_br)} notícia(s) BR e {len(articles_global)} global(is) encontrada(s). Gerando tags...")
    articles_br, articles_global = tag_articles(articles_global, articles_br)

    digest = build_digest(articles_br, articles_global)

    print("Enviando e-mail...")
    send_digest(digest, target_date)
    print("E-mail enviado com sucesso!")

    print("Salvando no Google Sheets...")
    save_to_sheets(articles_br, articles_global)
    print("Concluído.")


if __name__ == "__main__":
    main()
