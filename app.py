import streamlit as st
from buscador import buscar_por_assunto, carregar_versoes_disponiveis

st.set_page_config(page_title="Bíblia por Assunto", page_icon="📖", layout="centered")

st.title("📖 Bíblia por Assunto")
st.caption("Busca semântica de passagens bíblicas por tema, não apenas por palavra exata — sobre traduções de domínio público.")

versoes = carregar_versoes_disponiveis()
versao_key = st.selectbox(
    "Tradução",
    options=list(versoes.keys()),
    format_func=lambda k: versoes[k],
    index=0,
)

assunto = st.text_input("Sobre qual assunto você quer encontrar passagens?", placeholder="ex: perdão, medo, sabedoria, família...")
top_k = st.slider("Quantas passagens mostrar", 3, 20, 8)

if assunto:
    with st.spinner("Buscando passagens..."):
        resultados = buscar_por_assunto(assunto, versao_key, top_k=top_k)

    st.subheader(f"Passagens sobre \"{assunto}\" — {versoes[versao_key]}")
    for r in resultados:
        with st.container(border=True):
            st.markdown(f"**{r['ref']}**")
            st.write(r["texto"])
            st.caption(f"relevância: {r['score']:.2f}")
else:
    st.info("Digite um assunto acima para começar a busca.")

st.divider()
st.caption("Projeto de estudo · busca por similaridade semântica · apenas traduções de domínio público · sem custo de API.")
