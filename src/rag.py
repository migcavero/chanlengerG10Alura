"""Paso 4 — Capa de recuperación (RAG).

Conecta la base vectorial (Chroma) con el modelo Gemini para que Cindy responda
preguntas usando EXCLUSIVAMENTE la base de conocimiento, citando sus fuentes.

Uso:
    cd src && python rag.py                       # modo conversación
    cd src && python rag.py "¿cuánto cuesta?"     # una sola pregunta
"""
import sys

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

import config
from prompts import SYSTEM_PROMPT

load_dotenv()

RETRIEVER_K = 4  # cuántos fragmentos recuperar por pregunta


def get_retriever():
    embeddings = GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL)
    store = Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(config.VECTORSTORE_DIR),
    )
    return store.as_retriever(search_kwargs={"k": RETRIEVER_K})


def to_text(content) -> str:
    """Normaliza la respuesta del modelo a texto plano.

    Los modelos Gemini con 'thinking' devuelven el contenido como lista de bloques
    ({'type': 'text', 'text': ...}) en vez de un string. Aquí extraemos solo el texto.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        partes = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(p for p in partes if p).strip()
    return str(content)


def format_context(docs) -> str:
    """Une los fragmentos recuperados etiquetando su fuente para poder citarla."""
    bloques = []
    for d in docs:
        fuente = d.metadata.get("titulo") or d.metadata.get("categoria", "info")
        bloques.append(f"[Fuente: {fuente} · {d.metadata.get('fuente_archivo','?')}]\n{d.page_content}")
    return "\n\n---\n\n".join(bloques)


class CindyRAG:
    def __init__(self):
        self.retriever = get_retriever()
        self.llm = ChatGoogleGenerativeAI(model=config.CHAT_MODEL, temperature=0.3)
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", SYSTEM_PROMPT), ("human", "{question}")]
        )

    def responder(self, pregunta: str):
        docs = self.retriever.invoke(pregunta)
        context = format_context(docs)
        mensajes = self.prompt.format_messages(context=context, question=pregunta)
        respuesta = to_text(self.llm.invoke(mensajes).content)
        fuentes = sorted({d.metadata.get("fuente_archivo", "?") for d in docs})
        return respuesta, fuentes


def main():
    cindy = CindyRAG()

    if len(sys.argv) > 1:
        pregunta = " ".join(sys.argv[1:])
        respuesta, fuentes = cindy.responder(pregunta)
        print(f"\n🧑 {pregunta}\n\n🐘 {respuesta}\n\n📎 Fuentes: {', '.join(fuentes)}")
        return

    print("🐘 Cindy — asistente de Trompitas Dental (escribe 'salir' para terminar)\n")
    while True:
        try:
            pregunta = input("🧑 Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not pregunta or pregunta.lower() in {"salir", "exit", "quit"}:
            break
        respuesta, fuentes = cindy.responder(pregunta)
        print(f"\n🐘 Cindy: {respuesta}\n📎 Fuentes: {', '.join(fuentes)}\n")


if __name__ == "__main__":
    main()
