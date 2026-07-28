"""Prueba rápida de recuperación semántica sobre la base vectorial (verifica el Paso 3).

Uso:
    cd src && python search_test.py "¿cuánto cuesta la consulta?"
"""
import sys

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

import config

load_dotenv()


def main():
    query = " ".join(sys.argv[1:]).strip() or "¿Cuánto cuesta la consulta?"
    embeddings = GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL)
    store = Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(config.VECTORSTORE_DIR),
    )
    results = store.similarity_search_with_score(query, k=3)
    print(f"\n🔎 Consulta: {query}\n" + "=" * 60)
    for doc, score in results:
        cat = doc.metadata.get("categoria", "?")
        src = doc.metadata.get("fuente_archivo", "?")
        print(f"\n[distancia {score:.3f}]  ({cat} · {src})")
        print(doc.page_content[:240].strip())
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
