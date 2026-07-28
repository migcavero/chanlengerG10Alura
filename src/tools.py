"""Paso 5 — Herramientas del agente Cindy.

Define las "manos" del agente:
- buscar_informacion: consulta la base de conocimiento (RAG).
- agendar_cita: registra una solicitud de cita (versión ligera que persiste en
  data/citas.json; diseñada para sustituirse por Google Calendar más adelante).
"""
import json
from datetime import datetime

from langchain_core.tools import tool

import config
from rag import get_retriever, format_context

CITAS_FILE = config.BASE_DIR / "data" / "citas.json"

# El retriever se crea una sola vez (es costoso inicializarlo).
_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = get_retriever()
    return _retriever


@tool
def buscar_informacion(pregunta: str) -> str:
    """Busca información de los equipos de venta (servicios, precios, horarios,
    ubicación, políticas, promociones, urgencias) en la base de conocimiento oficial.
    Úsala para responder cualquier duda del usuario sobre la empresa."""
    docs = _get_retriever().invoke(pregunta)
    if not docs:
        return "Sin resultados en la base de conocimiento."
    return format_context(docs)


@tool
def agendar_cita(nombre_cliente: str, fecha: str, hora: str, servicio: str, telefono: str) -> str:
    """Registra una solicitud de cotización en la empresa. Úsala SOLO cuando tengas TODOS los datos:
    nombre del paciente, fecha, hora, servicio/motivo y teléfono de contacto. Si falta alguno,
    pídeselo al usuario antes de llamar a esta herramienta."""
    cita = {
        "nombre_cliente": nombre_cliente,
        "fecha": fecha,
        "hora": hora,
        "servicio": servicio,
        "telefono": telefono,
        "registrada_en": datetime.now().isoformat(timespec="seconds"),
    }

    CITAS_FILE.parent.mkdir(parents=True, exist_ok=True)
    citas = []
    if CITAS_FILE.exists():
        try:
            citas = json.loads(CITAS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            citas = []
    citas.append(cita)
    CITAS_FILE.write_text(json.dumps(citas, ensure_ascii=False, indent=2), encoding="utf-8")

    return (
        f"Cita registrada correctamente para {nombre_cliente} el {fecha} a las {hora} "
        f"({servicio}). Se confirmará al teléfono {telefono}."
    )

# Lista de herramientas que se le entregan al agente
HERRAMIENTAS = [buscar_informacion, agendar_cita]