# Bíblia por Assunto

Projeto de estudo: chatbot/buscador que encontra passagens bíblicas por **assunto/tema** (busca semântica), não apenas por palavra exata — evitando o problema de uma IA genérica "inventar" uma referência de memória.

Zero custo: roda com um modelo de embeddings local (sem chave de API) e é hospedado gratuitamente no Streamlit Community Cloud.

## Como funciona

1. O texto integral da Bíblia (**ACF — Almeida Corrigida Fiel**, tradução em domínio público) foi baixado como dataset aberto (`data/acf.json`).
2. `ingest.py` gera um embedding (vetor semântico) para cada um dos ~31 mil versículos, usando o modelo local `paraphrase-multilingual-MiniLM-L12-v2` (roda offline, sem API).
3. `buscador.py` recebe um assunto digitado pelo usuário, gera o embedding da busca e retorna os versículos mais próximos por similaridade de cosseno.
4. `app.py` é a interface Streamlit.

## Rodar localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 ingest.py        # gera data/embeddings.npy e data/versiculos.json (uma vez só)
streamlit run app.py
```

## Deploy no Streamlit Community Cloud (gratuito)

1. Suba este repositório para o GitHub (público).
2. Garanta que `data/embeddings.npy` e `data/versiculos.json` estão commitados (evita reprocessar tudo a cada deploy).
3. Acesse [share.streamlit.io](https://share.streamlit.io), conecte sua conta GitHub e aponte para este repositório, arquivo principal `app.py`.
4. O Streamlit Cloud instala as dependências de `requirements.txt` e gera um link público.

## Licenciamento dos dados

Só usamos traduções em **domínio público** (ACF). Traduções como NVI, NVT, NTLH, Bíblia de Jerusalém etc. têm direitos autorais e não podem ser redistribuídas livremente em um dataset/app sem licença da editora.

## Próximos passos possíveis

- Adicionar a **ARC de 1911** (também domínio público) para comparar duas traduções.
- Camada opcional de LLM (ex: API Claude) para sintetizar uma resposta em linguagem natural em cima dos versículos encontrados — sempre citando apenas o que foi de fato recuperado, para não alucinar referências.
