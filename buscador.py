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
