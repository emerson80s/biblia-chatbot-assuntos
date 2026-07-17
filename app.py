import base64
import html
import json
import re
from string import Template

import streamlit as st
from buscador import (
    buscar_por_assunto,
    comparar_versoes,
    carregar_versoes_disponiveis,
    versiculo_aleatorio,
    obter_passagem,
    TESTAMENTOS,
)
from livros_pt import LIVROS_ORDEM

st.set_page_config(page_title="Bíblia por Assunto", page_icon="📖", layout="centered")

PALETA_CLARA = {
    "bg": "#F6EFE0",
    "bg2": "#FFFBF2",
    "border": "#E6D8B4",
    "border_forte": "#D8C79A",
    "tinta": "#9C8A63",
    "tinta_suave": "#9C8A63",
    "tinta_fraca": "#9C8A63",
    "acento": "#9A6B24",
    "acento_texto": "#9C8A63",
    "marca_bg": "#F1D999",
    "marca_tinta": "#4A3B1E",
    "titulo": "#9C8A63",
    "fundo_css": (
        "background: radial-gradient(ellipse at center, #F7EFDC 0%, #F2E5C4 45%, "
        "#DFC98F 72%, #A9814A 90%, #6B4A24 100%);"
    ),
}

PALETA_ESCURA = {
    "bg": "#121212",
    "bg2": "#1E1E1E",
    "border": "#333333",
    "border_forte": "#454545",
    "tinta": "#E0E0E0",
    "tinta_suave": "#AFAFAF",
    "tinta_fraca": "#888888",
    "acento": "#D9A93B",
    "acento_texto": "#D9A93B",
    "marca_bg": "#4A3B1E",
    "marca_tinta": "#F8E9BE",
    "titulo": "#F2C744",
    "fundo_css": "background: #121212;",
}

if "tema_toggle_valor" not in st.session_state:
    st.session_state["tema_toggle_valor"] = True

toggle_wrap = st.container(key="theme_toggle_wrap")
with toggle_wrap:
    st.toggle(
        "🌙" if st.session_state["tema_toggle_valor"] else "☀️",
        key="tema_toggle_valor",
    )

st.session_state["modo_escuro"] = st.session_state["tema_toggle_valor"]
P = PALETA_ESCURA if st.session_state["modo_escuro"] else PALETA_CLARA

CSS = Template("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Nunito+Sans:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito Sans', sans-serif;
    letter-spacing: 0.02em;
}
.verse-text, .hero-text p, .secao-label, .verse-ref, .hero-text h1 {
    letter-spacing: 0.025em;
}

:root, .stApp {
    --primary-color: ${acento};
    --background-color: ${bg};
    --secondary-background-color: ${bg2};
    --text-color: ${tinta};
}

[data-testid="stAppViewContainer"], [data-testid="stApp"] {
    ${fundo_css}
}
[data-testid="stHeader"] {
    background: ${bg} !important;
}

.st-key-theme_toggle_wrap {
    position: fixed;
    top: 68px;
    right: 18px;
    z-index: 999999;
    width: auto !important;
}

[data-testid="stSelectbox"] * {
    background-color: ${bg2} !important;
    color: ${tinta} !important;
    border-color: ${border_forte} !important;
    fill: ${tinta} !important;
}
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] * {
    background-color: transparent !important;
}
[data-baseweb="popover"] *, [data-baseweb="menu"] * {
    background-color: ${bg2} !important;
    color: ${tinta} !important;
}
[role="option"]:hover, [aria-selected="true"] {
    background-color: ${border} !important;
}
[data-testid="stSelectbox"] svg {
    background-color: transparent !important;
    fill: ${tinta_fraca} !important;
}
[data-testid="stSelectbox"] svg path[fill="none"] {
    fill: none !important;
}
[data-testid="stSelectbox"] button[aria-label="Open"],
[data-testid="stSelectbox"] button[aria-label="Close"] {
    background-color: transparent !important;
}
[data-testid="stSelectbox"] .react-aria-ComboBox {
    background-color: ${bg2} !important;
    border-radius: 8px;
}
[data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {
    color: ${tinta_fraca} !important;
}

[data-testid="stAlert"], [data-testid="stAlertContainer"] {
    background-color: ${bg2} !important;
    border: 1px solid ${border_forte} !important;
    color: ${tinta} !important;
}
[data-testid="stAlert"] *, [data-testid="stAlertContainer"] * {
    color: ${tinta} !important;
    fill: ${acento} !important;
}

.hero {
    padding: 1.2rem 0 0.6rem;
    border-bottom: 1px solid ${border_forte};
    margin-bottom: 1.4rem;
}
.hero-banner {
    width: 100%;
    max-height: 260px;
    object-fit: cover;
    display: block;
    border-radius: 10px;
    box-shadow: 0 6px 22px rgba(0,0,0,0.35);
    margin-bottom: 1.1rem;
}
.hero-text h1 {
    font-family: 'Lora', serif;
    font-weight: 600;
    font-size: 2.3rem;
    margin: 0;
    color: ${titulo};
}
.hero-text p {
    margin: 0.15rem 0 0;
    color: ${tinta_suave};
    font-size: 0.95rem;
}

[data-testid="stTextInput"] input {
    font-family: 'Lora', serif;
    font-size: 1.05rem;
    border: 1px solid ${border_forte} !important;
    background: ${bg2} !important;
    color: ${tinta} !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: ${acento} !important;
    box-shadow: 0 0 0 1px ${acento} !important;
}

[data-testid="stSelectbox"] label {
    font-weight: 600;
    color: ${tinta};
}

.secao-label {
    font-family: 'Nunito Sans', sans-serif;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: ${tinta_fraca};
    margin: 0.4rem 0 0.3rem;
}

[data-testid="stCheckbox"] p, [data-testid="stTextInput"] label, [data-testid="stSlider"] label {
    font-family: 'Nunito Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: ${tinta_fraca} !important;
}

[data-testid="stTooltipIcon"] svg path {
    stroke: ${tinta_fraca} !important;
}

[data-testid="stHorizontalBlock"] {
    flex-direction: row !important;
    flex-wrap: wrap !important;
}
[data-testid="stHorizontalBlock"] [data-testid="stColumn"] {
    width: auto !important;
    min-width: 0 !important;
    flex: 1 1 0 !important;
}

[data-testid="stButton"] button {
    background: ${bg2};
    border: 1px solid ${border_forte};
    color: ${tinta_fraca};
    font-family: 'Nunito Sans', sans-serif;
    font-size: 0.85rem;
    padding: 0.25rem 0.8rem;
    border-radius: 999px;
}
[data-testid="stButton"] button:hover {
    border-color: ${acento};
}

.verse-card {
    background: ${bg2};
    border: 1px solid ${border};
    border-left: 4px solid ${acento};
    border-radius: 4px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.18);
}
.verse-ref {
    font-family: 'Lora', serif;
    font-weight: 700;
    font-size: 1.05rem;
    color: ${acento_texto};
    margin-bottom: 0.45rem;
}
.verse-score {
    font-size: 0.75rem;
    color: ${tinta_fraca};
    font-variant-numeric: tabular-nums;
    margin-left: 0.5rem;
    font-weight: 400;
}
.verse-text {
    font-family: 'Lora', serif;
    font-size: 1.08rem;
    line-height: 1.6;
    color: ${tinta};
}
.verse-text mark {
    background: ${marca_bg};
    color: ${marca_tinta};
    padding: 0 0.15em;
    border-radius: 2px;
}
.verse-text sup {
    font-size: 0.68em;
    color: ${tinta_fraca};
    margin-right: 0.1em;
}
.verso-central {
    font-weight: 700;
}
.verse-missing {
    font-family: 'Nunito Sans', sans-serif;
    font-size: 0.9rem;
    font-style: italic;
    color: ${tinta_fraca};
}

.verse-actions {
    margin-top: 0.65rem;
}
.verse-btn {
    font-family: 'Nunito Sans', sans-serif;
    font-size: 0.78rem;
    background: transparent;
    border: 1px solid ${border_forte};
    color: ${tinta_suave};
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    cursor: pointer;
    margin-right: 0.5rem;
}
.verse-btn:hover {
    border-color: ${acento};
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
    color: ${tinta_fraca};
    margin-bottom: 0.35rem;
}

.footer-note {
    font-size: 0.82rem;
    color: ${tinta_fraca};
    border-top: 1px solid ${border_forte};
    padding-top: 1rem;
    margin-top: 1.6rem;
}
</style>
""").substitute(P)

st.markdown(CSS, unsafe_allow_html=True)

BANNER_B64 = base64.b64encode(open("assets/biblia-banner.jpg", "rb").read()).decode()

st.markdown(
    '<div class="hero">'
    f'<img class="hero-banner" src="data:image/jpeg;base64,{BANNER_B64}" alt="Bíblia de capa de couro preta com crucifixo"/>'
    '<div class="hero-text">'
    '<h1>Bíblia por Assunto</h1>'
    '<p>Busca semântica de passagens por tema, não apenas por palavra exata, entre traduções de domínio público.</p>'
    '</div></div>',
    unsafe_allow_html=True,
)

versoes = carregar_versoes_disponiveis()

ASSUNTOS_POPULARES = ["perdão", "família", "gratidão", "amor"]

if "assunto_input" not in st.session_state:
    st.session_state["assunto_input"] = ""
if "historico" not in st.session_state:
    st.session_state["historico"] = []

campo_busca = st.container()

st.markdown('<div class="secao-label">Sugestões</div>', unsafe_allow_html=True)
cols = st.columns(len(ASSUNTOS_POPULARES))
for i, topico in enumerate(ASSUNTOS_POPULARES):
    with cols[i]:
        if st.button(topico, key=f"pop_{topico}"):
            st.session_state["assunto_input"] = topico

if st.session_state["historico"]:
    st.markdown('<div class="secao-label">Buscas recentes</div>', unsafe_allow_html=True)
    hist_cols = st.columns(min(5, len(st.session_state["historico"])) or 1)
    for i, termo in enumerate(st.session_state["historico"][:5]):
        with hist_cols[i]:
            if st.button(termo, key=f"hist_{i}_{termo}"):
                st.session_state["assunto_input"] = termo

with campo_busca:
    assunto = st.text_input(
        "Sobre qual assunto você quer encontrar passagens?",
        placeholder="ex: perdão, medo, sabedoria, família...",
        key="assunto_input",
        help="Digite um tema livre — não precisa ser a palavra exata do texto bíblico. A busca entende o significado.",
    )

col_aleatorio, _ = st.columns([1, 3])
with col_aleatorio:
    aleatorio_clicado = st.button("✨ Versículo surpresa", help="Mostra um versículo qualquer, sem precisar buscar por assunto.")

modo_comparacao = st.toggle(
    "Comparar as 3 traduções lado a lado",
    value=False,
    help="Mostra a mesma passagem encontrada nas 3 traduções ao mesmo tempo, para comparar as palavras usadas em cada uma.",
)

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
        help="Todas as traduções disponíveis são de domínio público — podem ser usadas livremente.",
    )

escopo = st.selectbox(
    "Buscar em",
    ["Toda a Bíblia", "Antigo Testamento", "Novo Testamento", "Um livro específico"],
    help="Restringe a busca a uma parte específica da Bíblia, em vez de procurar no texto todo.",
)
livros_filtro = None
if escopo in TESTAMENTOS:
    livros_filtro = TESTAMENTOS[escopo]
elif escopo == "Um livro específico":
    livro_escolhido = st.selectbox("Livro", LIVROS_ORDEM)
    livros_filtro = [livro_escolhido]

top_k = st.slider(
    "Quantas passagens mostrar",
    3, 20, 8,
    help="Quantos versículos diferentes (resultados) aparecem na tela, do mais ao menos relevante para o assunto buscado.",
)
contexto = 3  # versículos de contexto ao redor de cada resultado (fixo)

if aleatorio_clicado:
    st.session_state["ultimo_aleatorio"] = versiculo_aleatorio(versao_base, livros_filtro)


def limpar_travessoes(texto: str) -> str:
    # remove travessões usados como pontuação (ex: aposto, fala) sem afetar
    # hifens internos de palavras (ex: "multiplicai-vos")
    texto = re.sub(r"\s*[—–]\s*", " ", texto)
    return re.sub(r"\s{2,}", " ", texto).strip()


def texto_passagem_plano(versao: str, livro: str, capitulo: int, versiculo: int, janela: int) -> str:
    passagem = obter_passagem(versao, livro, capitulo, versiculo, janela=janela)
    return " ".join(f'{v["num"]} {limpar_travessoes(v["texto"])}' for v in passagem)


def renderizar_passagem(versao: str, livro: str, capitulo: int, versiculo: int, termo: str, janela: int) -> str:
    passagem = obter_passagem(versao, livro, capitulo, versiculo, janela=janela)
    partes = []
    for verso in passagem:
        texto_html = html.escape(limpar_travessoes(verso["texto"]))
        if verso["central"]:
            partes.append(f'<span class="verso-central"><sup>{verso["num"]}</sup> {texto_html}</span>')
        else:
            partes.append(f'<sup>{verso["num"]}</sup> {texto_html}')
    return " ".join(partes)


def botoes_acao(ref: str, texto: str, nome_versao: str) -> str:
    texto_limpo = limpar_travessoes(texto)
    citacao = f"“{texto_limpo}” — {ref} ({nome_versao})"
    citacao_js = json.dumps(citacao)
    texto_js = json.dumps(texto_limpo)
    return (
        '<div class="verse-actions">'
        f"<button class=\"verse-btn\" onclick='navigator.clipboard.writeText({citacao_js})'>📋 Copiar</button>"
        f"<button class=\"verse-btn\" onclick='speechSynthesis.cancel(); var u = new SpeechSynthesisUtterance({texto_js}); u.lang=\"pt-BR\"; speechSynthesis.speak(u);'>🔊 Ouvir</button>"
        "</div>"
    )


if "ultimo_aleatorio" in st.session_state:
    v = st.session_state["ultimo_aleatorio"]
    cartao = (
        '<div class="verse-card">'
        f'<div class="verse-ref">✨ {html.escape(v["ref"])}</div>'
        f'<div class="verse-text">{limpar_travessoes(v["texto"])}</div>'
        f'{botoes_acao(v["ref"], v["texto"], versoes[versao_base])}'
        '</div>'
    )
    st.markdown(cartao, unsafe_allow_html=True)

if assunto:
    historico = st.session_state["historico"]
    if not historico or historico[0] != assunto:
        st.session_state["historico"] = [assunto] + [t for t in historico if t != assunto][:7]

    with st.spinner("Buscando passagens..."):
        if modo_comparacao:
            resultados = comparar_versoes(assunto, versao_base, list(versoes.keys()), top_k=top_k, livros_filtro=livros_filtro)
        else:
            resultados = buscar_por_assunto(assunto, versao_base, top_k=top_k, livros_filtro=livros_filtro)

    st.markdown(f"#### Passagens sobre “{assunto}”")

    if not resultados:
        st.warning("Nenhuma passagem encontrada com esse filtro. Tente ampliar o escopo da busca.")

    if modo_comparacao:
        colunas_keys = list(versoes.keys())
        for r in resultados:
            colunas_html = ""
            for k in colunas_keys:
                texto = r["textos"].get(k)
                if texto:
                    passagem_html = renderizar_passagem(k, r["livro"], r["capitulo"], r["versiculo"], assunto, contexto)
                    passagem_plana = texto_passagem_plano(k, r["livro"], r["capitulo"], r["versiculo"], contexto)
                    corpo = f'<div class="verse-text">{passagem_html}</div>{botoes_acao(r["ref"], passagem_plana, versoes[k])}'
                else:
                    corpo = '<div class="verse-missing">(versículo ausente nesta tradução)</div>'
                colunas_html += f'<div class="compare-col"><div class="versao-label">{html.escape(versoes[k])}</div>{corpo}</div>'

            cartao = (
                '<div class="verse-card">'
                f'<div class="verse-ref">{html.escape(r["ref"])}<span class="verse-score">relevância {r["score"]:.2f}</span></div>'
                f'<div class="compare-grid">{colunas_html}</div>'
                '</div>'
            )
            st.markdown(cartao, unsafe_allow_html=True)
    else:
        for r in resultados:
            passagem_html = renderizar_passagem(versao_base, r["livro"], r["capitulo"], r["versiculo"], assunto, contexto)
            passagem_plana = texto_passagem_plano(versao_base, r["livro"], r["capitulo"], r["versiculo"], contexto)
            cartao = (
                '<div class="verse-card">'
                f'<div class="verse-ref">{html.escape(r["ref"])}<span class="verse-score">relevância {r["score"]:.2f}</span></div>'
                f'<div class="verse-text">{passagem_html}</div>'
                f'{botoes_acao(r["ref"], passagem_plana, versoes[versao_base])}'
                '</div>'
            )
            st.markdown(cartao, unsafe_allow_html=True)

st.markdown(
    '<div class="footer-note">Projeto de estudo · busca por similaridade semântica · '
    'apenas traduções de domínio público · sem custo de API.</div>',
    unsafe_allow_html=True,
)
