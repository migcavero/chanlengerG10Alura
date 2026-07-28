"""Paso 3 — Indexación.

Lee la base de conocimiento (base_conocimiento/*.txt), separa el bloque de
METADATOS de cada documento, trocea el contenido en fragmentos (chunking),
genera embeddings con Gemini y los guarda en una base vectorial Chroma
persistente para su posterior búsqueda semántica (RAG).

Uso:
    cd src && python ingest.py
Requiere GOOGLE_API_KEY en un archivo .env (ver .env.example).
"""
import re
import shutil

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

import config

load_dotenv()

# Bloque de metadatos al inicio de cada documento
META_RE = re.compile(r"# METADATOS(.*?)# FIN METADATOS", re.S)

# Notas internas de trabajo (p. ej. "[PENDIENTE — CONFIRMAR ...]"). No son conocimiento
# del negocio, así que se eliminan para que no contaminen las respuestas de Cindy.
NOTA_INTERNA_RE = re.compile(r"\[PENDIENTE[^\]]*\]", re.S)

# Título del documento (línea "TÍTULO: ...")
TITULO_RE = re.compile(r"^T[ÍI]TULO:\s*(.+)$", re.M)


def parse_document(text: str, filename: str):
    """Devuelve (metadatos, cuerpo) separando la cabecera # METADATOS ... # FIN METADATOS."""
    meta = {"fuente_archivo": filename}
    m = META_RE.search(text)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.strip().startswith("#"):
                key, value = line.split(":", 1)
                key, value = key.strip(), value.strip()
                if key and value:
                    meta[key] = value
    body = META_RE.sub("", text)
    body = NOTA_INTERNA_RE.sub("", body)          # quita notas internas de trabajo
    body = re.sub(r"\n{3,}", "\n\n", body)        # colapsa saltos de línea sobrantes
    return meta, body.strip()


def build_chunks():
    """Carga los .txt, los trocea y devuelve listas paralelas (textos, metadatos)."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    texts, metadatas = [], []
    files = [p for p in sorted(config.KB_DIR.glob("*.txt"))
             if p.name not in config.ARCHIVOS_EXCLUIDOS]
    for path in files:
        meta, body = parse_document(path.read_text(encoding="utf-8"), path.name)

        # Cabecera de contexto: cada fragmento "sabe" de qué documento viene.
        # Mejora mucho la relevancia semántica de los fragmentos intermedios.
        titulo_match = TITULO_RE.search(body)
        titulo = titulo_match.group(1).strip() if titulo_match else meta.get("categoria", path.stem)
        cabecera = f"[{titulo} · Trompitas Dental]\n"

        for i, piece in enumerate(splitter.split_text(body)):
            chunk_meta = dict(meta)
            chunk_meta["chunk"] = i
            chunk_meta["titulo"] = titulo
            texts.append(cabecera + piece)
            metadatas.append(chunk_meta)
    print(f"📄 {len(files)} documentos  →  ✂️  {len(texts)} fragmentos (chunks)")
    return texts, metadatas


def main():
    texts, metadatas = build_chunks()
    if not texts:
        raise SystemExit(f"No se encontraron .txt en {config.KB_DIR}")

    embeddings = GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL)

    # Reconstruye la base desde cero para evitar duplicados
    if config.VECTORSTORE_DIR.exists():
        shutil.rmtree(config.VECTORSTORE_DIR)
    config.VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

    print("🧠 Generando embeddings con Gemini y guardando en Chroma...")
    Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        collection_name=config.COLLECTION_NAME,
        persist_directory=str(config.VECTORSTORE_DIR),
    )
    print(f"✅ Base vectorial creada en: {config.VECTORSTORE_DIR}")


if __name__ == "__main__":
    main()
