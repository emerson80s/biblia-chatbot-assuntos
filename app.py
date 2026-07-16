import streamlit as st
from buscador import buscar_por_assunto

st.set_page_config(page_title="Bíblia por Assunto", page_icon="📖", layout="centered")

st.title("📖 Bíblia por Assunto")
st.caption("Busca semântica de passagens bíblicas (tradução ACF — domínio público) por tema, não apenas por palavra exata.")

assunto = st.text_input("Sobre qual assunto você quer encontrar passagens?", placeholder="ex: perdão, medo, sabedoria, família...")
top_k = st.slider("Quantas passagens mostrar", 3, 20, 8)

if assunto:
    with st.spinner("Buscando passagens..."):
        resultados = buscar_por_assunto(assunto, top_k=top_k)

    st.subheader(f"Passagens sobre \"{assunto}\"")
    for r in resultados:
        with st.container(border=True):
            st.markdown(f"**{r['ref']}**")
            st.write(r["texto"])
            st.caption(f"relevância: {r['score']:.2f}")
else:
    st.info("Digite um assunto acima para começar a busca.")

st.divider()
st.caption("Projeto de estudo · busca por similaridade semântica sobre o texto integral da Bíblia (ACF) · sem custo de API.")
