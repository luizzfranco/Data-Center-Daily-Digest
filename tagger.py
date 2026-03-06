import os
import time
import google.generativeai as genai

PROMPT_TEMPLATE = """Você é um assistente especializado em data centers e infraestrutura digital.
Dado o título de uma notícia, gere as tags relevantes em letras minúsculas.
As tags devem capturar: empresas, países/regiões, temas e conceitos-chave.
Use quantas tags forem necessárias — nem mais, nem menos.
Nunca omita substantivos e nomes próprios relevantes presentes no título.
Responda APENAS com as tags separadas por vírgula, sem explicações.

Exemplos:
Título: "Chile suspende projeto Chile-China Express devido a riscos geopolíticos"
Tags: chile, china, chile-china express, cabo submarino, geopolítica

Título: "Desenvolvedora de data centers Edged busca isenções fiscais para potencial instalação em Fort Worth, Texas"
Tags: edged, data center, fort worth, texas, eua, isenção fiscal, política econômica

Título: "Equinix fecha acordo de autoprodução com a Auren Energia"
Tags: equinix, auren energia, brasil, energia, autoprodução, ppa, sustentabilidade

Título: "Google seeks land annexation for data center campus in Linn County, Iowa"
Tags: google, linn county, iowa, eua, expansão, data center

Título: "NDC acquires data center in Rennes from French insurance firm Groupama"
Tags: ndc, groupama, rennes, frança, aquisição, m&a, data center, colocation

Título: "Oracle plans to again cut thousands of jobs to free up AI data center spending"
Tags: oracle, eua, demissões, ia, data center, investimento, fluxo de caixa

Título: "{titulo}"
Tags:"""


RATE_LIMIT = 10        # requests por minuto (free tier)
RATE_LIMIT_PAUSE = 62  # segundos de pausa ao atingir o limite


def tag_articles(articles_global, articles_br):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    request_count = 0

    def get_tags(title):
        nonlocal request_count
        if request_count > 0 and request_count % RATE_LIMIT == 0:
            print(f"  [Tagger] Rate limit atingido ({RATE_LIMIT} req/min). Aguardando {RATE_LIMIT_PAUSE}s...")
            time.sleep(RATE_LIMIT_PAUSE)
        try:
            prompt = PROMPT_TEMPLATE.format(titulo=title)
            response = model.generate_content(prompt)
            raw = response.text.strip()
            request_count += 1
            return [t.strip() for t in raw.split(",") if t.strip()]
        except Exception as e:
            print(f"  [Tagger] Erro ao gerar tags para '{title[:50]}': {e}")
            request_count += 1
            return []

    if articles_br:
        print("  Gerando tags BR via Gemini...")
        for article in articles_br:
            tags = get_tags(article["title"])
            article["tags"] = tags
            print(f"  [BR] Tags de '{article['title'][:50]}': {tags}")

    if articles_global:
        print("  Gerando tags Global via Gemini...")
        for article in articles_global:
            tags = get_tags(article["title"])
            article["tags"] = tags
            print(f"  [Global] Tags de '{article['title'][:50]}': {tags}")

    return articles_br, articles_global
