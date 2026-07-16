# Bíblia por Assunto

Projeto de estudo: chatbot/buscador que encontra passagens bíblicas por **assunto/tema** (busca semântica), não apenas por palavra exata — evitando o problema de uma IA genérica "inventar" uma referência de memória.

Zero custo: roda com um modelo de embeddings local (sem chave de API) e é hospedado gratuitamente no Streamlit Community Cloud.

## Traduções disponíveis

Todas em **domínio público** (via [damarals/biblias](https://github.com/damarals/biblias) e [thiagobodruk/biblia](https://github.com/thiagobodruk/biblia)):

| Sigla | Tradução | Ano |
|---|---|---|
| ACF | Almeida Corrigida Fiel | 1994 |
| ALM1911 | Almeida 1911 | 1911 |
| BLIVRE | Bíblia Livre | 2018 |

Traduções como NVI, NVT, NTLH, Bíblia de Jerusalém etc. têm direitos autorais e **não** podem ser redistribuídas livremente em um dataset/app sem licença da editora — por isso não entram no projeto.

## Como funciona

1. O texto integral de cada tradução foi baixado como dataset aberto (`data/acf.json`, `data/ALM1911.json`, `data/BLIVRE.json`).
2. `ingest.py` mapeia os livros pela **posição canônica** (66 livros, mesma ordem em todas as fontes) — evita colisão de abreviação entre fontes diferentes (ex: "Jó" e "Jo" após remover acento) — e filtra versículos sem texto real (marcados como omitidos por tradição textual, ex: alguns manuscritos não trazem Atos 8:37).
3. Para cada tradução, gera um embedding (vetor semântico) por versículo usando o modelo local `paraphrase-multilingual-MiniLM-L12-v2` (roda offline, sem API): `data/embeddings_<versao>.npy` + `data/versiculos_<versao>.json`.
4. `buscador.py` recebe um assunto digitado pelo usuário, gera o embedding da busca e retorna os versículos mais próximos por similaridade de cosseno, na tradução escolhida.
5. `app.py` é a interface Streamlit, com um seletor de tradução.

## Rodar localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 ingest.py        # gera embeddings + versículos para cada tradução (uma vez só)
streamlit run app.py
```

## Deploy no Streamlit Community Cloud (gratuito)

1. Suba este repositório para o GitHub (público).
2. Garanta que `data/embeddings_*.npy`, `data/versiculos_*.json` e `data/versoes.json` estão commitados (evita reprocessar tudo a cada deploy).
3. Acesse [share.streamlit.io](https://share.streamlit.io), conecte sua conta GitHub e aponte para este repositório, arquivo principal `app.py`.
4. O Streamlit Cloud instala as dependências de `requirements.txt` e gera um link público.

## Próximos passos possíveis

- Camada opcional de LLM (ex: API Claude) para sintetizar uma resposta em linguagem natural em cima dos versículos encontrados — sempre citando apenas o que foi de fato recuperado, para não alucinar referências.
- Comparar lado a lado o mesmo versículo nas 3 traduções.
