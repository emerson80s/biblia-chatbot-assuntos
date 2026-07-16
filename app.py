import streamlit as st
from buscador import buscar_por_assunto, comparar_versoes, carregar_versoes_disponiveis

st.set_page_config(page_title="Bíblia por Assunto", page_icon="📖", layout="centered")

st.title("📖 Bíblia por Assunto")
st.caption("Busca semântica de passagens bíblicas por tema, não apenas por palavra exata — sobre traduções de domínio público.")

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

if assunto:
    with st.spinner("Buscando passagens..."):
        if modo_comparacao:
            resultados = comparar_versoes(assunto, versao_base, list(versoes.keys()), top_k=top_k)
        else:
            resultados = buscar_por_assunto(assunto, versao_base, top_k=top_k)

    st.subheader(f"Passagens sobre \"{assunto}\"")

    if modo_comparacao:
        colunas_keys = list(versoes.keys())
        for r in resultados:
            with st.container(border=True):
                st.markdown(f"**{r['ref']}**  ·  relevância: {r['score']:.2f}")
                cols = st.columns(len(colunas_keys))
                for col, k in zip(cols, colunas_keys):
                    with col:
                        st.caption(versoes[k])
                        texto = r["textos"].get(k)
                        if texto:
                            st.write(texto)
                        else:
                            st.write("_(versículo ausente nesta tradução)_")
    else:
        for r in resultados:
            with st.container(border=True):
                st.markdown(f"**{r['ref']}**")
                st.write(r["texto"])
                st.caption(f"relevância: {r['score']:.2f}")
else:
    st.info("Digite um assunto acima para começar a busca.")

st.divider()
st.caption("Projeto de estudo · busca por similaridade semântica · apenas traduções de domínio público · sem custo de API.")
