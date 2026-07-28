"""Paso 5 — Agente Cindy (tool-calling) + Paso 8 — Trazabilidad.

Cindy decide por sí misma si responde una duda (herramienta buscar_informacion)
o agenda una cita (herramienta agendar_cita). Implementado con un bucle de
herramientas manual sobre Gemini (bind_tools), robusto entre versiones de LangChain.
Cada interacción se registra en un log para auditoría (trazabilidad del challenge).

Uso:
    cd src && python agent.py                    # modo conversación
    cd src && python agent.py "tu mensaje"       # un solo mensaje
"""
import sys
import json
from datetime import datetime

from dotenv import load_dotenv
from langchain_core.messages import (
    SystemMessage, HumanMessage, AIMessage, ToolMessage,
)
from langchain_google_genai import ChatGoogleGenerativeAI

import config
from prompts import SYSTEM_PROMPT_AGENTE
from tools import HERRAMIENTAS
from rag import to_text

load_dotenv()

LOG_FILE = config.BASE_DIR / "data" / "logs" / "interacciones.jsonl"
MAX_ITERACIONES = 5  # tope de rondas de herramientas por turno (evita bucles)


def registrar_log(pregunta: str, respuesta: str, herramientas: list[str]):
    """Guarda la interacción en un log JSONL (trazabilidad / auditoría)."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    registro = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "pregunta": pregunta,
        "respuesta": respuesta,
        "herramientas_usadas": herramientas,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


class CindyAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=config.CHAT_MODEL, temperature=0.3
        ).bind_tools(HERRAMIENTAS)
        self.tool_map = {t.name: t for t in HERRAMIENTAS}

    def responder(self, mensaje: str, historial=None):
        mensajes = [SystemMessage(content=SYSTEM_PROMPT_AGENTE)]
        mensajes += historial or []
        mensajes.append(HumanMessage(content=mensaje))

        herramientas_usadas = []
        ai = self.llm.invoke(mensajes)

        for _ in range(MAX_ITERACIONES):
            if not ai.tool_calls:
                break
            mensajes.append(ai)
            for tc in ai.tool_calls:
                herramientas_usadas.append(tc["name"])
                herramienta = self.tool_map[tc["name"]]
                resultado = herramienta.invoke(tc["args"])
                mensajes.append(
                    ToolMessage(content=str(resultado), tool_call_id=tc["id"])
                )
            ai = self.llm.invoke(mensajes)

        respuesta = to_text(ai.content)
        registrar_log(mensaje, respuesta, herramientas_usadas)
        return respuesta, herramientas_usadas


def main():
    cindy = CindyAgent()

    if len(sys.argv) > 1:
        mensaje = " ".join(sys.argv[1:])
        respuesta, herramientas = cindy.responder(mensaje)
        print(f"\n🧑 {mensaje}\n\n🐘 {respuesta}\n\n🔧 Herramientas: {herramientas or 'ninguna'}")
        return

    print("🐘 Cindy — asistente de Trompitas Dental (escribe 'salir' para terminar)\n")
    historial = []
    while True:
        try:
            mensaje = input("🧑 Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not mensaje or mensaje.lower() in {"salir", "exit", "quit"}:
            break
        respuesta, herramientas = cindy.responder(mensaje, historial)
        print(f"\n🐘 Cindy: {respuesta}\n")
        historial.append(HumanMessage(content=mensaje))
        historial.append(AIMessage(content=respuesta))


if __name__ == "__main__":
    main()
