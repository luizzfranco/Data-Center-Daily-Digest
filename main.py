from scraper import get_yesterday_articles
from summarizer import summarize_articles
from mailer import send_digest
from datetime import date, timedelta

def main():
    yesterday = date.today() - timedelta(days=1)
    print(f"Buscando notícias de {yesterday.strftime('%d/%m/%Y')}...")

    articles = get_yesterday_articles()

    if not articles:
        print("Nenhuma notícia encontrada para ontem. Encerrando.")
        return

    print(f"{len(articles)} notícia(s) encontrada(s). Gerando resumos...")
    digest = summarize_articles(articles, yesterday)

    print("Enviando e-mail...")
    send_digest(digest, yesterday)
    print("E-mail enviado com sucesso!")

if __name__ == "__main__":
    main()
