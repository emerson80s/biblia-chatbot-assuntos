import json
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

@st.cache_resource
def carregar_modelo():
    return SentenceTransformer(MODEL_NAME)

@st.cache_resource
def carregar_versoes_disponiveis():
    return json.load(open("data/versoes.json", encoding="utf-8"))

@st.cache_resource
def carregar_base(versao: str):
    embeddings = np.load(f"data/embeddings_{versao}.npy")
    versiculos = json.load(open(f"data/versiculos_{versao}.json", encoding="utf-8"))
    return embeddings, versiculos

@st.cache_resource
def carregar_indice_por_ref(versao: str):
    _, versiculos = carregar_base(versao)
    return {v["ref"]: v["texto"] for v in versiculos}

def buscar_por_assunto(assunto: str, versao: str, top_k: int = 8):
    model = carregar_modelo()
    embeddings, versiculos = carregar_base(versao)

    consulta = model.encode([assunto], normalize_embeddings=True, convert_to_numpy=True)[0]
    scores = embeddings @ consulta
    indices = np.argsort(-scores)[:top_k]

    resultados = []
    for i in indices:
        v = versiculos[i]
        resultados.append({
            "ref": v["ref"],
            "texto": v["texto"],
            "score": float(scores[i]),
        })
    return resultados

def comparar_versoes(assunto: str, versao_base: str, versoes: list[str], top_k: int = 8):
    """Busca por assunto na versão base e traz a mesma referência nas demais versões.

    Como cada tradução pode omitir um versículo (ex: variante textual), a
    referência pode não existir em todas — nesse caso o texto vem como None.
    """
    resultados_base = buscar_por_assunto(assunto, versao_base, top_k=top_k)

    indices_outras = {v: carregar_indice_por_ref(v) for v in versoes if v != versao_base}

    comparacao = []
    for r in resultados_base:
        textos = {versao_base: r["texto"]}
        for v, indice in indices_outras.items():
            textos[v] = indice.get(r["ref"])
        comparacao.append({
            "ref": r["ref"],
            "score": r["score"],
            "textos": textos,
        })
    return comparacao
