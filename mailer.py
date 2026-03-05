import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def build_html(digest, date):
    date_str = date.strftime("%d/%m/%Y")
    visao_geral = digest.get("visao_geral", "")
    noticias = digest.get("noticias", [])

    noticias_html = ""
    for n in noticias:
        noticias_html += f"""
        <div class="article">
            <div class="article-title">{n['titulo']}</div>
            <div class="article-summary">{n['resumo']}</div>
            <div class="article-link"><a href="{n['url']}">🔗 Ler artigo completo</a></div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: #f5f5f5;
      margin: 0;
      padding: 20px;
      color: #222;
    }}
    .container {{
      max-width: 680px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .header {{
      background-color: #1a1a2e;
      color: white;
      padding: 24px 32px;
    }}
    .header h1 {{
      margin: 0;
      font-size: 20px;
      font-weight: 600;
    }}
    .header p {{
      margin: 4px 0 0;
      font-size: 13px;
      opacity: 0.7;
    }}
    .content {{
      padding: 28px 32px;
    }}
    .overview {{
      background: #f8f9fa;
      border-left: 4px solid #1a1a2e;
      padding: 16px 20px;
      margin-bottom: 28px;
      border-radius: 0 6px 6px 0;
      font-size: 14px;
      line-height: 1.7;
    }}
    .overview-label {{
      font-weight: 700;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #1a1a2e;
      margin-bottom: 8px;
    }}
    .article {{
      padding: 20px 0;
      border-bottom: 1px solid #eee;
    }}
    .article:last-child {{
      border-bottom: none;
    }}
    .article-title {{
      font-weight: 700;
      font-size: 15px;
      color: #1a1a2e;
      margin-bottom: 8px;
      line-height: 1.4;
    }}
    .article-summary {{
      font-size: 14px;
      color: #444;
      line-height: 1.6;
      margin-bottom: 10px;
    }}
    .article-link a {{
      font-size: 13px;
      color: #0066cc;
      text-decoration: none;
    }}
    .footer {{
      background: #f9f9f9;
      border-top: 1px solid #eee;
      padding: 16px 32px;
      font-size: 12px;
      color: #888;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📡 Data Center Daily Digest</h1>
      <p>Resumo diário — {date_str}</p>
    </div>
    <div class="content">
      <div class="overview">
        <div class="overview-label">Visão geral do dia</div>
        {visao_geral}
      </div>
      {noticias_html}
    </div>
    <div class="footer">
      Gerado automaticamente via GitHub Actions · 
      <a href="https://www.datacenterdynamics.com">datacenterdynamics.com</a>
    </div>
  </div>
</body>
</html>"""


def send_digest(digest, date):
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("RECIPIENT_EMAIL")

    if not all([gmail_user, gmail_password, recipient]):
        raise ValueError("Variáveis de e-mail não configuradas.")

    date_str = date.strftime("%d/%m/%Y")
    subject = f"📡 Data Center Daily Digest — {date_str}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = recipient

    html_content = build_html(digest, date)
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipient, msg.as_string())
