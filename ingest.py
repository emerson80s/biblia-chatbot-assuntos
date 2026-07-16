import json
import numpy as np
from sentence_transformers import SentenceTransformer
from livros_pt import LIVROS

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

def carregar_versiculos(path="data/acf.json"):
    livros = json.load(open(path, encoding="utf-8-sig"))
    versiculos = []
    for livro in livros:
        abbrev = livro["abbrev"]
        nome = LIVROS.get(abbrev, abbrev)
        for i, capitulo in enumerate(livro["chapters"], start=1):
            for j, texto in enumerate(capitulo, start=1):
                versiculos.append({
                    "livro": nome,
                    "abbrev": abbrev,
                    "capitulo": i,
                    "versiculo": j,
                    "texto": texto,
                    "ref": f"{nome} {i}:{j}",
                })
    return versiculos

def main():
    print("Carregando versículos...")
    versiculos = carregar_versiculos()
    print(f"{len(versiculos)} versículos carregados.")

    print(f"Carregando modelo de embeddings ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)

    textos = [v["texto"] for v in versiculos]
    print("Gerando embeddings (pode levar alguns minutos)...")
    embeddings = model.encode(
        textos,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    np.save("data/embeddings.npy", embeddings.astype("float32"))
    with open("data/versiculos.json", "w", encoding="utf-8") as f:
        json.dump(versiculos, f, ensure_ascii=False)

    print("Pronto: data/embeddings.npy e data/versiculos.json")

if __name__ == "__main__":
    main()
