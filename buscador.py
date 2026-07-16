import json
import random

import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

from livros_pt import LIVROS_ORDEM

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

TESTAMENTOS = {
    "Antigo Testamento": LIVROS_ORDEM[:39],
    "Novo Testamento": LIVROS_ORDEM[39:],
}

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

@st.cache_resource
def carregar_indice_por_capitulo(versao: str):
    _, versiculos = carregar_base(versao)
    indice: dict[tuple[str, int], dict[int, str]] = {}
    for v in versiculos:
        chave = (v["livro"], v["capitulo"])
        indice.setdefault(chave, {})[v["versiculo"]] = v["texto"]
    return indice

def obter_passagem(versao: str, livro: str, capitulo: int, versiculo_central: int, janela: int = 3):
    """Retorna os versículos ao redor do versículo central, dentro do mesmo capítulo.

    Alguns números podem faltar (versículo omitido por tradição textual em
    certas traduções) — nesse caso o número é simplesmente pulado.
    """
    indice = carregar_indice_por_capitulo(versao)
    versos_cap = indice.get((livro, capitulo), {})
    inicio = max(1, versiculo_central - janela)
    fim = versiculo_central + janela
    passagem = []
    for num in range(inicio, fim + 1):
        if num in versos_cap:
            passagem.append({
                "num": num,
                "texto": versos_cap[num],
                "central": num == versiculo_central,
            })
    return passagem

def buscar_por_assunto(assunto: str, versao: str, top_k: int = 8, livros_filtro: list[str] | None = None):
    model = carregar_modelo()
    embeddings, versiculos = carregar_base(versao)

    if livros_filtro:
        filtro = set(livros_filtro)
        indices_validos = np.array([i for i, v in enumerate(versiculos) if v["livro"] in filtro])
        embeddings_busca = embeddings[indices_validos]
    else:
        indices_validos = np.arange(len(versiculos))
        embeddings_busca = embeddings

    consulta = model.encode([assunto], normalize_embeddings=True, convert_to_numpy=True)[0]
    scores = embeddings_busca @ consulta
    ordem_local = np.argsort(-scores)[:top_k]

    resultados = []
    for pos in ordem_local:
        i = indices_validos[pos]
        v = versiculos[i]
        resultados.append({
            "ref": v["ref"],
            "texto": v["texto"],
            "score": float(scores[pos]),
            "livro": v["livro"],
            "capitulo": v["capitulo"],
            "versiculo": v["versiculo"],
        })
    return resultados

def comparar_versoes(assunto: str, versao_base: str, versoes: list[str], top_k: int = 8, livros_filtro: list[str] | None = None):
    """Busca por assunto na versão base e traz a mesma referência nas demais versões.

    Como cada tradução pode omitir um versículo (ex: variante textual), a
    referência pode não existir em todas — nesse caso o texto vem como None.
    """
    resultados_base = buscar_por_assunto(assunto, versao_base, top_k=top_k, livros_filtro=livros_filtro)

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
            "livro": r["livro"],
            "capitulo": r["capitulo"],
            "versiculo": r["versiculo"],
        })
    return comparacao

def versiculo_aleatorio(versao: str, livros_filtro: list[str] | None = None):
    _, versiculos = carregar_base(versao)
    if livros_filtro:
        filtro = set(livros_filtro)
        candidatos = [v for v in versiculos if v["livro"] in filtro]
    else:
        candidatos = versiculos
    v = random.choice(candidatos)
    return {"ref": v["ref"], "texto": v["texto"]}
