import html
import re

import streamlit as st
from buscador import buscar_por_assunto, comparar_versoes, carregar_versoes_disponiveis

st.set_page_config(page_title="Bíblia por Assunto", page_icon="📖", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Nunito+Sans:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito Sans', sans-serif;
}

[data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background:
        radial-gradient(ellipse at 20% 0%, rgba(90,30,36,0.55) 0%, rgba(0,0,0,0) 55%),
        radial-gradient(ellipse at 100% 30%, rgba(20,8,10,0.6) 0%, rgba(0,0,0,0) 60%),
        linear-gradient(160deg, #33161A 0%, #2B1418 45%, #241014 100%);
}

.hero {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    padding: 1.6rem 0 0.6rem;
    border-bottom: 1px solid #5A3439;
    margin-bottom: 1.4rem;
}
.hero .icon {
    font-size: 2.4rem;
    line-height: 1;
}
.hero h1 {
    font-family: 'Lora', serif;
    font-weight: 600;
    font-size: 2rem;
    margin: 0;
    color: #F1DFAE;
}
.hero p {
    margin: 0.15rem 0 0;
    color: #C29B85;
    font-size: 0.95rem;
}

[data-testid="stTextInput"] input {
    font-family: 'Lora', serif;
    font-size: 1.05rem;
    border: 1px solid #5A3439 !important;
    background: #331519 !important;
    color: #EAD9AF !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #C9992B !important;
    box-shadow: 0 0 0 1px #C9992B !important;
}

[data-testid="stSelectbox"] label, [data-testid="stSlider"] label, .stToggle label {
    font-weight: 600;
    color: #EAD9AF;
}

.verse-card {
    background: linear-gradient(160deg, #3D1B1F 0%, #331519 100%);
    border: 1px solid #5A3439;
    border-left: 4px solid #C9992B;
    border-radius: 4px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
}
.verse-ref {
    font-family: 'Lora', serif;
    font-weight: 700;
    font-size: 1.05rem;
    color: #D9A93B;
    text-shadow: 0 1px 1px rgba(0,0,0,0.45);
    margin-bottom: 0.45rem;
}
.verse-score {
    font-size: 0.75rem;
    color: #9C7A6E;
    font-variant-numeric: tabular-nums;
    margin-left: 0.5rem;
    font-weight: 400;
}
.verse-text {
    font-family: 'Lora', serif;
    font-size: 1.08rem;
    line-height: 1.6;
    color: #EAD9AF;
}
.verse-text mark {
    background: #7A4A22;
    color: #F8E9BE;
    padding: 0 0.15em;
    border-radius: 2px;
}
.verse-missing {
    font-family: 'Nunito Sans', sans-serif;
    font-size: 0.9rem;
    font-style: italic;
    color: #9C7A6E;
}

.compare-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-top: 0.6rem;
}
.compare-col .versao-label {
    font-family: 'Nunito Sans', sans-serif;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #9C7A6E;
    margin-bottom: 0.35rem;
}

.footer-note {
    font-size: 0.82rem;
    color: #9C7A6E;
    border-top: 1px solid #5A3439;
    padding-top: 1rem;
    margin-top: 1.6rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="icon">📖</div>
    <div>
        <h1>Bíblia por Assunto</h1>
        <p>Busca semântica de passagens por tema, não apenas por palavra exata, entre traduções de domínio público.</p>
    </div>
</div>
""", unsafe_allow_html=True)

versoes = carregar_versoes_disponiveis()

modo_comparacao = st.toggle("Comparar as 3 traduções lado a lado", value=False)

if modo_comparacao:
    versao_base = st.selectbox(
        "Tradução usada para a busca (as outras aparecem lado a lado)",
        options=list(versoes.keys()),
        format_func=lambda k: versoes[k],
        index=0,
    )
else:
    versao_base = st.selectbox(
        "Tradução",
        options=list(versoes.keys()),
        format_func=lambda k: versoes[k],
        index=0,
    )

assunto = st.text_input("Sobre qual assunto você quer encontrar passagens?", placeholder="ex: perdão, medo, sabedoria, família...")
top_k = st.slider("Quantas passagens mostrar", 3, 20, 8)


def limpar_travessoes(texto: str) -> str:
    # remove travessões usados como pontuação (ex: aposto, fala) sem afetar
    # hifens internos de palavras (ex: "multiplicai-vos")
    texto = re.sub(r"\s*[—–]\s*", " ", texto)
    return re.sub(r"\s{2,}", " ", texto).strip()


def destacar(texto: str, termo: str) -> str:
    texto = limpar_travessoes(texto)
    escapado = html.escape(texto)
    if not termo.strip():
        return escapado
    padrao = re.compile(re.escape(html.escape(termo)), re.IGNORECASE)
    return padrao.sub(lambda m: f"<mark>{m.group(0)}</mark>", escapado)


if assunto:
    with st.spinner("Buscando passagens..."):
        if modo_comparacao:
            resultados = comparar_versoes(assunto, versao_base, list(versoes.keys()), top_k=top_k)
        else:
            resultados = buscar_por_assunto(assunto, versao_base, top_k=top_k)

    st.markdown(f"#### Passagens sobre “{assunto}”")

    if modo_comparacao:
        colunas_keys = list(versoes.keys())
        for r in resultados:
            colunas_html = ""
            for k in colunas_keys:
                texto = r["textos"].get(k)
                if texto:
                    corpo = f'<div class="verse-text">{destacar(texto, assunto)}</div>'
                else:
                    corpo = '<div class="verse-missing">(versículo ausente nesta tradução)</div>'
                colunas_html += f'<div class="compare-col"><div class="versao-label">{html.escape(versoes[k])}</div>{corpo}</div>'

            st.markdown(f"""
            <div class="verse-card">
                <div class="verse-ref">{html.escape(r['ref'])}<span class="verse-score">relevância {r['score']:.2f}</span></div>
                <div class="compare-grid">{colunas_html}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        for r in resultados:
            st.markdown(f"""
            <div class="verse-card">
                <div class="verse-ref">{html.escape(r['ref'])}<span class="verse-score">relevância {r['score']:.2f}</span></div>
                <div class="verse-text">{destacar(r['texto'], assunto)}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Digite um assunto acima para começar a busca.")

st.markdown(
    '<div class="footer-note">Projeto de estudo · busca por similaridade semântica · '
    'apenas traduções de domínio público · sem custo de API.</div>',
    unsafe_allow_html=True,
)
