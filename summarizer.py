import os
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
        articles_text += f"\n---\nArtigo {i}: {a['title']}\nDescrição: {a.get('description', '')}\nConteúdo: {a.get('content', '')}\nURL: {a['url']}\n"

    prompt = f"""Você é um assistente especializado em tecnologia e infraestrutura de data centers.

Abaixo estão as notícias publicadas em {date_str} no site Data Center Dynamics.

Produza um digest em PORTUGUÊS BRASILEIRO com este formato exato:

**Visão geral do dia**
[parágrafo de 4 a 6 linhas resumindo os principais temas e tendências do dia]

---

[Para cada notícia, use exatamente este formato:]

**[Título traduzido para o português]**
[Resumo de 2 a 3 linhas em português]
[URL original]

---

Sem títulos de seção como "Resumo por notícia". Sem rótulos como "Título:", "Resumo:", "Link:". Direto ao ponto. Linguagem profissional e objetiva.

{articles_text}
"""

    response = model.generate_content(prompt)
    return response.text
