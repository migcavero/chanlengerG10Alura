"""Paso 6 — Interfaz web (Streamlit).

Chat web de Cindy, la asistente digital de Trompitas Dental. Conecta con el agente
(RAG + agenda), mantiene el historial de la conversación y muestra las herramientas/
fuentes usadas. Deja claro que es una IA.

Uso:
    cd src && streamlit run app.py
"""
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from agent import CindyAgent

st.set_page_config(page_title="Cindy · Trompitas Dental", page_icon="🐘")

# --- Encabezado ---
st.title("🐘 Cindy — Trompitas Dental")
st.caption(
    "Asistente **digital (IA)** de Trompitas Dental · Odontopediatría y odontología general. "
    "Puedo darte información y ayudarte a agendar tu cita."
)

# --- Inicialización (el agente se crea una sola vez por sesión) ---
@st.cache_resource(show_spinner="Despertando a Cindy... 🐘")
def cargar_agente():
    return CindyAgent()


cindy = cargar_agente()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []  # historial visible (dicts role/content)
    st.session_state.historial = []  # historial para el agente (LangChain messages)
    st.session_state.mensajes.append(
        {
            "role": "assistant",
            "content": (
                "¡Hola! Soy **Cindy** 🐘✨, la asistente digital de Trompitas Dental. "
                "Puedo ayudarte con información de servicios, precios y horarios, o a "
                "agendar tu cita. ¿En qué te apoyo hoy? 😊"
            ),
        }
    )

# --- Render del historial ---
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"], avatar="🐘" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

# --- Entrada del usuario ---
if pregunta := st.chat_input("Escribe tu mensaje..."):
    st.session_state.mensajes.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant", avatar="🐘"):
        with st.spinner("Cindy está pensando... 🦷"):
            respuesta, herramientas = cindy.responder(pregunta, st.session_state.historial)
        st.markdown(respuesta)
        if "agendar_cita" in herramientas:
            st.success("📅 ¡Cita registrada!")

    # Actualiza ambos historiales
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    st.session_state.historial.append(HumanMessage(content=pregunta))
    st.session_state.historial.append(AIMessage(content=respuesta))

# --- Aviso de IA en el pie ---
st.divider()
st.caption("🤖 Cindy es un asistente virtual con IA. Para urgencias, escribe al WhatsApp +52 427 335 1918.")
