"""Configuración central del proyecto Cindy (agente IA de Trompitas Dental)."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "base_conocimiento"            # documentos fuente (.txt)
VECTORSTORE_DIR = BASE_DIR / "data" / "vectorstore"  # base vectorial Chroma (persistente)
COLLECTION_NAME = "luim-comercial_kb"

# Modelos de Google Gemini
EMBEDDING_MODEL = "models/gemini-embedding-001"  # vectorización de los fragmentos
CHAT_MODEL = "gemini-flash-latest"               # se usará en pasos 4-5 (respuestas)

# Parámetros de troceado (chunking)
CHUNK_SIZE = 1100      # caracteres por fragmento (secciones completas, no partidas)
CHUNK_OVERLAP = 150    # superposición entre fragmentos (mantiene contexto)

# Documentos que NO deben indexarse (son meta del proyecto, no conocimiento del negocio)
ARCHIVOS_EXCLUIDOS = {"00_indice.txt"}