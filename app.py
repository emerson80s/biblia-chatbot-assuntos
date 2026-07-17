import base64
import html
import json
import re
from string import Template

import streamlit as st
import streamlit.components.v1 as components
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

[data-testid="stTooltipIcon"],
[data-testid="stTooltipIcon"] *,
[data-testid="stTooltipIcon"] svg,
[data-testid="stTooltipIcon"] svg path,
[data-testid="stTooltipIcon"] svg circle {
    background: none !important;
    background-color: transparent !important;
    box-shadow: none !important;
    filter: none !important;
    -webkit-mask-image: none !important;
    mask-image: none !important;
    opacity: 1 !important;
    fill: none !important;
    stroke: ${acento} !important;
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


# O Streamlit sanitiza o HTML de st.markdown e remove atributos onclick, então
# os botões não podem carregar o handler inline. Em vez disso, acumulamos o texto
# de cada botão e religamos os cliques no fim via um componente (ver rodapé).
ACOES_CLIPBOARD: list[dict] = []


def botoes_acao(ref: str, texto: str, nome_versao: str) -> str:
    texto_limpo = limpar_travessoes(texto)
    citacao = f"“{texto_limpo}”\n\n📖 {ref} — {nome_versao}"
    idx = len(ACOES_CLIPBOARD)
    ACOES_CLIPBOARD.append({"copiar": citacao, "ouvir": texto_limpo})
    return (
        '<div class="verse-actions">'
        f'<button class="verse-btn" id="acao-copiar-{idx}">📋 Copiar</button>'
        f'<button class="verse-btn" id="acao-ouvir-{idx}">🔊 Ouvir</button>'
        '</div>'
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

# Religa os cliques de Copiar/Ouvir. Como o Streamlit remove o onclick inline do
# HTML sanitizado, um componente (iframe do mesmo domínio) alcança o documento pai
# via window.parent e anexa os handlers usando o texto acumulado em ACOES_CLIPBOARD.
if ACOES_CLIPBOARD:
    dados_js = json.dumps(ACOES_CLIPBOARD)
    components.html(
        """
<script>
const dados = __DADOS__;
const w = window.parent;
const doc = w.document;

// Dispara o carregamento assíncrono das vozes para já estarem prontas no clique.
try { w.speechSynthesis.getVoices(); } catch (e) {}

function copiar(texto) {
  // execCommand é síncrono e funciona dentro do gesto do clique — mais confiável
  // aqui do que o clipboard assíncrono, que fica pendente sem ativação de usuário.
  let ok = false;
  try {
    const ta = doc.createElement('textarea');
    ta.value = texto;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.top = '0';
    ta.style.left = '0';
    ta.style.width = '1px';
    ta.style.height = '1px';
    ta.style.padding = '0';
    ta.style.border = 'none';
    ta.style.opacity = '0';
    doc.body.appendChild(ta);
    ta.focus({ preventScroll: true });
    ta.select();
    ok = doc.execCommand('copy');
    doc.body.removeChild(ta);
  } catch (e) { ok = false; }
  // Bônus para navegadores modernos em contexto seguro (não bloqueia o feedback).
  if (w.navigator.clipboard && w.navigator.clipboard.writeText) {
    try { w.navigator.clipboard.writeText(texto).catch(() => {}); } catch (e) {}
  }
  return ok;
}

function feedback(btn) {
  if (btn.dataset.mostrando) return;
  const orig = btn.innerHTML;
  btn.dataset.mostrando = '1';
  btn.innerHTML = '✓ Copiado';
  setTimeout(() => { btn.innerHTML = orig; delete btn.dataset.mostrando; }, 1500);
}

// As vozes disponíveis são as do dispositivo do usuário (a Web Speech API roda no
// cliente). Preferimos as mais naturais: vozes masculinas neurais quando houver
// (ex.: Microsoft Antônio no Windows/Edge), senão a voz de rede do Google, senão
// qualquer pt-BR local. Nenhuma iguala um locutor profissional (ver observação).
function escolherVoz() {
  const vs = w.speechSynthesis.getVoices();
  // Só vozes em português — evita pegar uma voz homônima em outro idioma
  // (ex.: "Daniel" no macOS é inglês) que leria o texto com sotaque errado.
  const pt = vs.filter(v => /^pt/i.test(v.lang));
  const ptBR = pt.filter(v => /pt(-|_)?BR/i.test(v.lang));
  const pool = ptBR.length ? ptBR : pt;
  const achar = (frag) => pool.find(v => v.name.toLowerCase().includes(frag));
  return achar('antonio') || achar('antônio')   // voz masculina neural (Windows/Edge)
      || achar('google português')              // voz de rede natural (Chrome)
      || achar('luciana')                       // voz local do macOS
      || pool.find(v => v.localService)         // qualquer pt-BR local
      || pool[0]
      || null;
}

function restaurarOuvir() {
  const b = w.__bibliaOuvirBtn;
  if (b) { b.innerHTML = w.__bibliaOuvirOrig || '🔊 Ouvir'; w.__bibliaOuvirBtn = null; }
}

function falar(texto, btn) {
  const ss = w.speechSynthesis;
  // Segundo clique enquanto lê: interrompe a leitura.
  if (ss.speaking || ss.pending) { ss.cancel(); restaurarOuvir(); return; }
  restaurarOuvir();
  w.__bibliaOuvirBtn = btn;
  w.__bibliaOuvirOrig = btn.innerHTML;
  btn.innerHTML = '⏸ Parar';
  const voz = escolherVoz();
  // Divide em frases: contorna o bug do Chrome que corta vozes de rede após ~15s.
  const partes = (texto.match(/[^.!?…]+[.!?…]*/g) || [texto])
    .map(s => s.trim()).filter(Boolean);
  partes.forEach((parte, idx) => {
    const u = new w.SpeechSynthesisUtterance(parte);
    u.lang = 'pt-BR';
    if (voz) u.voice = voz;
    u.rate = 0.92;   // leitura pausada, de narração
    u.pitch = 0.9;   // levemente mais grave
    if (idx === partes.length - 1) u.onend = restaurarOuvir;
    u.onerror = restaurarOuvir;
    ss.speak(u);
  });
}

// Delegação de evento no body do documento pai: um único listener que resolve o
// botão pelo id (acao-copiar-N / acao-ouvir-N). É imune à troca/reuso de nós do
// DOM entre reruns do Streamlit — problema que um guard por-nó não resolve. O
// listener é re-registrado a cada rerun para usar os dados atuais.
function handler(e) {
  const btn = e.target.closest('.verse-btn');
  if (!btn || !btn.id) return;
  const m = btn.id.match(/^acao-(copiar|ouvir)-(\\d+)$/);
  if (!m) return;
  const a = dados[parseInt(m[2], 10)];
  if (!a) return;
  if (m[1] === 'copiar') { copiar(a.copiar); feedback(btn); }
  else { falar(a.ouvir, btn); }
}

if (w.__bibliaHandler) doc.body.removeEventListener('click', w.__bibliaHandler);
w.__bibliaHandler = handler;
doc.body.addEventListener('click', handler);
</script>
""".replace("__DADOS__", dados_js),
        height=0,
    )
