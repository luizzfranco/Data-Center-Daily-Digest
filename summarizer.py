import os
import google.generativeai as genai

def summarize_articles(articles, date):
    """Uses Gemini to generate an overview + per-article summaries in Portuguese."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Build the prompt
    date_str = date.strftime("%d/%m/%Y")
    articles_text = ""
    for i, a in enumerate(articles, 1):
        articles_text += f"""
---
Artigo {i}: {a['title']}
URL: {a['url']}
Conteúdo: {a['content'] or '(conteúdo não disponível)'}
"""

    prompt = f"""Você é um assistente especializado em tecnologia e infraestrutura de data centers.

Abaixo estão as notícias publicadas em {date_str} no site Data Center Dynamics (datacenterdynamics.com).

Sua tarefa é produzir um digest em PORTUGUÊS BRASILEIRO com:

1. **VISÃO GERAL DO DIA** — Um parágrafo de 4 a 6 linhas resumindo os principais temas e tendências do dia.

2. **RESUMO POR NOTÍCIA** — Para cada artigo, escreva:
   - O título original
   - Um resumo de 3 a 5 linhas em português
   - O link original

Seja claro, objetivo e informativo. Não inclua opiniões. Use linguagem profissional.

{articles_text}
"""

    response = model.generate_content(prompt)
    return response.text
