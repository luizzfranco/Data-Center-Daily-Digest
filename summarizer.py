import os
import json
import google.generativeai as genai


def summarize_articles(articles, date):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    date_str = date.strftime("%d/%m/%Y")
    articles_text = ""
    for i, a in enumerate(articles, 1):
        articles_text += f"\n---\nArtigo {i}: {a['title']}\nDescrição: {a.get('description', '')}\nURL: {a['url']}\n"

    prompt = f"""Você é um assistente especializado em tecnologia e infraestrutura de data centers.

Abaixo estão as notícias publicadas em {date_str} no site Data Center Dynamics.

Responda APENAS com um JSON válido, sem texto antes ou depois, sem blocos de código, sem markdown. O JSON deve ter este formato:

{{
  "visao_geral": "parágrafo de 4 a 6 linhas resumindo os principais temas do dia",
  "noticias": [
    {{
      "titulo": "título traduzido para o português",
      "resumo": "resumo de 2 a 3 linhas em português",
      "url": "url original"
    }}
  ]
}}

{articles_text}
"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    return json.loads(text)
