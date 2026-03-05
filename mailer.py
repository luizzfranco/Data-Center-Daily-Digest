import os
import smtplib
import markdown
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def markdown_to_html(text):
    """Converts markdown text to HTML with basic styling."""
    html_body = markdown.markdown(text, extensions=["extra"])

    return f"""
<!DOCTYPE html>
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
      letter-spacing: 0.5px;
    }}
    .header p {{
      margin: 4px 0 0;
      font-size: 13px;
      opacity: 0.7;
    }}
    .content {{
      padding: 28px 32px;
      line-height: 1.7;
    }}
    h2 {{
      color: #1a1a2e;
      border-bottom: 2px solid #e8e8e8;
      padding-bottom: 6px;
      margin-top: 28px;
      font-size: 16px;
    }}
    h3 {{
      color: #333;
      font-size: 15px;
      margin-top: 24px;
    }}
    p {{ margin: 8px 0; font-size: 14px; }}
    a {{ color: #0066cc; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    hr {{
      border: none;
      border-top: 1px solid #eee;
      margin: 20px 0;
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
      <p>Resumo diário — Data Center Dynamics</p>
    </div>
    <div class="content">
      {html_body}
    </div>
    <div class="footer">
      Gerado automaticamente via GitHub Actions + Google Gemini · 
      <a href="https://www.datacenterdynamics.com">datacenterdynamics.com</a>
    </div>
  </div>
</body>
</html>
"""


def send_digest(digest_text, date):
    """Sends the digest as a formatted HTML email via Gmail SMTP."""
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    recipient = os.environ.get("RECIPIENT_EMAIL")

    if not all([gmail_user, gmail_password, recipient]):
        raise ValueError("Variáveis de e-mail não configuradas: GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL")

    date_str = date.strftime("%d/%m/%Y")
    subject = f"📡 DCD Digest — {date_str}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = recipient

    # Plain text fallback
    msg.attach(MIMEText(digest_text, "plain", "utf-8"))

    # HTML version
    html_content = markdown_to_html(digest_text)
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipient, msg.as_string())
