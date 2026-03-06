import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def build_section(noticias):
    html = ""
    for n in noticias:
        html += f"""
        <div class="article">
            <div class="article-title">
                {n['titulo']} <a class="article-link-inline" href="{n['url']}">🔗 Link</a>
            </div>
        </div>
        """
    return html


def build_html(digest, date):
    date_str = date.strftime("%d/%m/%Y")

    br_html = ""
    if digest.get("br"):
        br_html = f"""
        <div class="section-header br">🇧🇷 Brasil</div>
        {build_section(digest["br"])}
        <div class="divider"></div>
        """

    global_html = ""
    if digest.get("global"):
        global_html = f"""
        <div class="section-header global">🌍 Global</div>
        {build_section(digest["global"])}
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
    .header h1 {{ margin: 0; font-size: 20px; font-weight: 600; }}
    .header p {{ margin: 4px 0 0; font-size: 13px; opacity: 0.7; }}
    .content {{ padding: 28px 32px; }}
    .section-header {{
      font-size: 16px;
      font-weight: 700;
      padding: 10px 0 14px;
      margin-top: 8px;
    }}
    .section-header.br {{ color: #006400; border-bottom: 3px solid #009c3b; margin-bottom: 16px; }}
    .section-header.global {{ color: #1a1a2e; border-bottom: 3px solid #1a1a2e; margin-bottom: 16px; }}
    .article {{
      padding: 14px 0;
      border-bottom: 1px solid #eee;
    }}
    .article:last-child {{ border-bottom: none; }}
    .article-title {{
      font-weight: 700;
      font-size: 15px;
      color: #1a1a2e;
      line-height: 1.4;
      margin-bottom: 6px;
    }}
    .article-link-inline {{
      font-size: 12px;
      color: #0066cc;
      text-decoration: none;
      font-weight: 400;
      white-space: nowrap;
      margin-left: 6px;
    }}
    .divider {{ border-top: 2px solid #eee; margin: 28px 0; }}
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
      {br_html}
      {global_html}
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
