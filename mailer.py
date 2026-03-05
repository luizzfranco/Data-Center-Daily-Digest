import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def build_section(noticias, resumo_longo=False):
    html = ""
    for n in noticias:
        html += f"""
        <div class="article">
            <div class="article-title">{n['titulo']}</div>
            <div class="article-summary">{n['resumo']}</div>
            <div class="article-link"><a href="{n['url']}">🔗 Ler artigo completo</a></div>
        </div>
        """
    return html


def build_html(digest, date):
    date_str = date.strftime("%d/%m/%Y")

    br_html = ""
    if digest.get("br"):
        br = digest["br"]
        br_html = f"""
        <div class="section-header br">🇧🇷 Brasil</div>
        <div class="overview">
            <div class="overview-label">Visão geral do dia</div>
            {br["visao_geral"]}
        </div>
        {build_section(br["noticias"], resumo_longo=True)}
        <div class="divider"></div>
        """

    global_html = ""
    if digest.get("global"):
        g = digest["global"]
        global_html = f"""
        <div class="section-header global">🌍 Global</div>
        <div class="overview">
            <div class="overview-label">Visão geral do dia</div>
            {g["visao_geral"]}
        </div>
        {build_section(g["noticias"])}
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
    .overview {{
      background: #f8f9fa;
      border-left: 4px solid #ccc;
      padding: 14px 18px;
      margin-bottom: 24px;
      border-radius: 0 6px 6px 0;
      font-size: 14px;
      line-height: 1.7;
    }}
    .overview-label {{
      font-weight: 700;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #555;
      margin-bottom: 8px;
    }}
    .article {{
      padding: 18px 0;
      border-bottom: 1px solid #eee;
    }}
    .article:last-child {{ border-bottom: none; }}
    .article-title {{ font-weight: 700; font-size: 15px; color: #1a1a2e; margin-bottom: 8px; line-height: 1.4; }}
    .article-summary {{ font-size: 14px; color: #444; line-height: 1.6; margin-bottom: 10px; }}
    .article-link a {{ font-size: 13px; color: #0066cc; text-decoration: none; }}
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
