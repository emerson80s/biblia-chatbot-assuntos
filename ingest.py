import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from livros_pt import LIVROS_ORDEM

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

VERSOES = {
    "acf": {
        "path": "data/acf.json",
        "encoding": "utf-8-sig",
        "nome": "Almeida Corrigida Fiel (ACF, 1994)",
    },
    "alm1911": {
        "path": "data/ALM1911.json",
        "encoding": "utf-8",
        "nome": "Almeida 1911",
    },
    "blivre": {
        "path": "data/BLIVRE.json",
        "encoding": "utf-8",
        "nome": "Bíblia Livre (BLIVRE, 2018)",
    },
}

def carregar_versiculos(versao: str):
    cfg = VERSOES[versao]
    livros = json.load(open(cfg["path"], encoding=cfg["encoding"]))
    if len(livros) != len(LIVROS_ORDEM):
        raise ValueError(f"{versao}: esperava {len(LIVROS_ORDEM)} livros, encontrou {len(livros)}")

    versiculos = []
    for nome, livro in zip(LIVROS_ORDEM, livros):
        for i, capitulo in enumerate(livro["chapters"], start=1):
            for j, texto in enumerate(capitulo, start=1):
                # Alguns manuscritos marcam versículos como ausentes (ex: "—"),
                # tradição textual antiga não inclui esse trecho — sem texto
                # real, não faz sentido indexar para busca semântica.
                if len(texto.strip(" —-")) < 3:
                    continue
                versiculos.append({
                    "livro": nome,
                    "capitulo": i,
                    "versiculo": j,
                    "texto": texto,
                    "ref": f"{nome} {i}:{j}",
                    "versao": versao,
                })
    return versiculos

def gerar_embeddings(versao: str, model: SentenceTransformer):
    out_emb = f"data/embeddings_{versao}.npy"
    out_json = f"data/versiculos_{versao}.json"
    if os.path.exists(out_emb) and os.path.exists(out_json):
        print(f"[{versao}] já processado, pulando.")
        return

    print(f"[{versao}] carregando versículos...")
    versiculos = carregar_versiculos(versao)
    print(f"[{versao}] {len(versiculos)} versículos carregados.")

    textos = [v["texto"] for v in versiculos]
    print(f"[{versao}] gerando embeddings...")
    embeddings = model.encode(
        textos,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    np.save(out_emb, embeddings.astype("float32"))
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(versiculos, f, ensure_ascii=False)
    print(f"[{versao}] pronto: {out_emb} e {out_json}")

def main():
    print(f"Carregando modelo de embeddings ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)

    for versao in VERSOES:
        gerar_embeddings(versao, model)

    with open("data/versoes.json", "w", encoding="utf-8") as f:
        json.dump({k: v["nome"] for k, v in VERSOES.items()}, f, ensure_ascii=False, indent=2)
    print("Manifesto de versões salvo em data/versoes.json")

if __name__ == "__main__":
    main()
