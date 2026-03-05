import os
import json
import google.generativeai as genai


def _call_gemini(model, prompt):
    response = model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text)


def summarize_articles(articles_global, articles_br, date):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    date_str = date.strftime("%d/%m/%Y")

    # --- Brasil ---
    br_text = ""
    for i, a in enumerate(articles_br, 1):
        br_text += f"\n---\nArtigo {i}: {a['title']}\nDescrição: {a.get('description', '')}\nURL: {a['url']}\n"

    br_prompt = f"""Você é um assistente especializado em tecnologia e infraestrutura de data centers.

Abaixo estão as notícias publicadas em {date_str} no site Data Center Dynamics — edição Brasil/Latam. Já estão em português.

Responda APENAS com JSON válido, sem texto antes ou depois, sem blocos de código:

{{
  "visao_geral": "parágrafo de 4 a 6 linhas resumindo os principais temas do dia na região Brasil/Latam",
  "noticias": [
    {{
      "titulo": "título original em português (não traduza)",
      "resumo": "resumo elaborado de 4 a 5 linhas em português",
      "url": "url original"
    }}
  ]
}}

{br_text}
"""

    # --- Global ---
    global_text = ""
    for i, a in enumerate(articles_global, 1):
        global_text += f"\n---\nArtigo {i}: {a['title']}\nDescrição: {a.get('description', '')}\nURL: {a['url']}\n"

    global_prompt = f"""Você é um assistente especializado em tecnologia e infraestrutura de data centers.

Abaixo estão as notícias publicadas em {date_str} no site Data Center Dynamics (edição global).

Responda APENAS com JSON válido, sem texto antes ou depois, sem blocos de código:

{{
  "visao_geral": "parágrafo de 4 a 6 linhas resumindo os principais temas e tendências globais do dia",
  "noticias": [
    {{
      "titulo": "título traduzido para o português",
      "resumo": "resumo de 2 a 3 linhas em português",
      "url": "url original"
    }}
  ]
}}

{global_text}
"""

    result = {}

    if articles_br:
        print("  Gerando resumos BR...")
        result["br"] = _call_gemini(model, br_prompt)
    else:
        result["br"] = None

    if articles_global:
        print("  Gerando resumos Global...")
        result["global"] = _call_gemini(model, global_prompt)
    else:
        result["global"] = None

    return result
