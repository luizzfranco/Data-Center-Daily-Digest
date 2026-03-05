# 📡 Data Center Daily Digest

Resumo diário automático de notícias sobre Data Centers, gerado pelo Google Gemini e enviado por e-mail todo dia de manhã.

---

## Passo a passo para configurar

### 1. Obter a chave da API do Google Gemini (gratuita)

1. Acesse [aistudio.google.com](https://aistudio.google.com)
2. Faça login com sua conta Google
3. Clique em **"Get API Key"** → **"Create API key"**
4. Copie a chave gerada (começa com `AIza...`)

---

### 2. Configurar o Gmail para envio automático

O Gmail não permite usar sua senha normal em scripts. Você precisa criar uma **senha de app**:

1. Acesse [myaccount.google.com/security](https://myaccount.google.com/security)
2. Ative a **verificação em duas etapas** (se ainda não tiver)
3. Busque por **"Senhas de app"** na página de segurança
4. Crie uma nova senha de app — escolha "Outro" e nomeie como "DCD Digest"
5. Copie a senha de 16 caracteres gerada

---

### 3. Criar o repositório no GitHub

1. Acesse [github.com](https://github.com) e crie um **novo repositório** (pode ser privado)
2. Faça upload de todos os arquivos deste projeto para o repositório

---

### 4. Adicionar os Secrets no GitHub

No seu repositório, vá em **Settings → Secrets and variables → Actions → New repository secret** e adicione:

| Nome do Secret | Valor |
|---|---|
| `GEMINI_API_KEY` | Chave do Google AI Studio |
| `GMAIL_USER` | Seu e-mail Gmail (ex: voce@gmail.com) |
| `GMAIL_APP_PASSWORD` | Senha de app de 16 caracteres |
| `RECIPIENT_EMAIL` | E-mail que receberá o digest (pode ser o mesmo) |

---

### 5. Testar manualmente

Antes de esperar o agendamento automático:

1. No GitHub, vá em **Actions** → **DCD Daily Digest**
2. Clique em **"Run workflow"** → **"Run workflow"**
3. Aguarde ~1 minuto e verifique seu e-mail

---

## Agendamento

O digest é enviado automaticamente todo dia às **07:00 (horário de Brasília)**.

Para mudar o horário, edite a linha `cron` no arquivo `.github/workflows/daily_digest.yml`.  
Conversor útil: [crontab.guru](https://crontab.guru)

---

## Estrutura dos arquivos

```
dcd-digest/
├── .github/workflows/daily_digest.yml  # agendamento automático
├── main.py          # orquestra o processo
├── scraper.py       # coleta notícias do site
├── summarizer.py    # gera resumos com Gemini
├── mailer.py        # envia o e-mail formatado
└── requirements.txt # dependências Python
```
