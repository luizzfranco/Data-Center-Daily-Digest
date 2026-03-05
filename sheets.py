import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "1dq-1f2WBy1zEXM9ZMWQxSwTinrGOk_SPXtqXW8Mc1MQ"
RANGE = "Sheet1!A:F"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_sheets_service():
    creds_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
    if not creds_json:
        raise ValueError("GOOGLE_SHEETS_CREDENTIALS não encontrada.")
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def save_to_sheets(articles_br, articles_global, digest):
    service = get_sheets_service()
    sheet = service.spreadsheets()

    rows = []

    # BR articles
    br_summaries = {}
    if digest.get("br") and digest["br"].get("noticias"):
        for n in digest["br"]["noticias"]:
            br_summaries[n["url"]] = n.get("resumo", "")

    for article in articles_br:
        tags = ", ".join(article.get("tags", []))
        resumo = br_summaries.get(article["url"], "")
        rows.append([
            article["date"],
            "BR",
            article["title"],
            article["url"],
            resumo,
            tags,
        ])

    # Global articles
    global_summaries = {}
    if digest.get("global") and digest["global"].get("noticias"):
        for n in digest["global"]["noticias"]:
            global_summaries[n["url"]] = n.get("resumo", "")

    for article in articles_global:
        tags = ", ".join(article.get("tags", []))
        resumo = global_summaries.get(article["url"], "")
        rows.append([
            article["date"],
            "Global",
            article["title"],
            article["url"],
            resumo,
            tags,
        ])

    if not rows:
        print("  Nenhuma linha para salvar no Sheets.")
        return

    body = {"values": rows}
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()

    print(f"  {len(rows)} linha(s) salva(s) no Google Sheets.")
