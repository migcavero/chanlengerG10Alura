"""Paso 6 — Backend web (FastAPI) para la interfaz de Cindy.

Sirve la interfaz (web/index.html) y expone el endpoint POST /chat que usa el
AGENTE real (RAG + agenda + logs). Así la UI diseñada deja de tener respuestas
"escritas a mano" y responde con IA de verdad, citando la base de conocimiento.

Uso:
    cd src && ../.venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

import config
from agent import CindyAgent

app = FastAPI(title="Cindy · Trompitas Dental")
WEB_DIR = config.BASE_DIR / "web"

# El agente se crea una sola vez al arrancar el servidor.
cindy = CindyAgent()


class ChatRequest(BaseModel):
    mensaje: str
    historial: list[dict] = []


@app.get("/")
def home():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    # Reconstruye el historial de la conversación para el agente
    historial = []
    for m in req.historial:
        rol, contenido = m.get("role"), m.get("content", "")
        if rol == "user":
            historial.append(HumanMessage(content=contenido))
        elif rol in ("assistant", "bot"):
            historial.append(AIMessage(content=contenido))

    respuesta, herramientas = cindy.responder(req.mensaje, historial)
    return {
        "respuesta": respuesta,
        "uso_rag": "buscar_informacion" in herramientas,
        "agendo": "agendar_cita" in herramientas,
    }
