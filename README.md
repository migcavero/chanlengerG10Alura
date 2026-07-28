# 🐘 LuiM — Asistente IA de Comercial

Chatbot corporativo con **RAG** (Retrieval-Augmented Generation) y **agente con herramientas** para la asesoria comercial en las especificaciones de equipos **Comercial ** (Lima, Lima).
LuiM responde dudas de pacientes usando **únicamente** la información oficial de la comercial(sin alucinar, citando la fuente) y **información de cotizaciones y citas para capacitaciones** dentro del propio chat.

🔗 **App en vivo:** https://LuiM-comerce.onrender.com

---

## 🎓 Sobre el Challenge

Este proyecto forma parte del **Challenge AlurAgente**, del programa **Oracle Next Education (ONE)** de **Alura Latam** — formación en **Orquestación de Agentes IA**.
El objetivo del challenge es construir un agente corporativo con RAG, desplegado en **Oracle Cloud Infrastructure (OCI)** y accesible mediante una URL pública.

---

## ✨ Características

- 💬 **Responde con IA** sobre servicios, precios, horarios, ubicación, políticas y urgencias.
- 📚 **RAG con citación de fuentes**: solo responde con la base de conocimiento oficial.
- 🚫 **Anti-alucinación**: si el dato no está, lo dice y ofrece contacto humano (WhatsApp).
- 📅 **Agenda citas** (herramienta del agente) con persistencia.
- 🐘 **Personalidad propia** (LuiM) y se identifica siempre como asistente digital (IA).
- 📝 **Trazabilidad**: registra cada interacción (pregunta, respuesta, herramienta) para auditoría.
- 🎨 **Interfaz web propia** (no genérica), cálida y responsiva.

---

## 🧠 Arquitectura

```mermaid
flowchart TD
    U["👨‍👩‍👧 Usuario (web)"] --> API["FastAPI /chat"]
    API --> AG["Agente LuiM<br/>(LangChain + Gemini)"]
    AG -->|"pregunta"| T1["🔎 buscar_informacion<br/>(RAG)"]
    AG -->|"agendar"| T2["📅 agendar_cita"]
    T1 --> VS["🧠 Base vectorial<br/>Chroma (embeddings)"]
    VS --> KB["📄 Base de conocimiento<br/>(9 documentos .txt)"]
    T2 --> J["🗂️ data/citas.json"]
    AG --> LOG["📝 Logs de trazabilidad<br/>data/logs/interacciones.jsonl"]
    AG --> API --> U
```

**Flujo:** el usuario escribe → el agente decide si **responder** (busca en la base vectorial con RAG y redacta con Gemini, citando la fuente) o **agendar** (herramienta que registra la cita). Cada interacción se guarda en el log.

---

## 🛠️ Tecnologías

| Componente              | Tecnología                                 |
| ----------------------- | ------------------------------------------ |
| Lenguaje                | Python 3.12                                |
| Orquestación de agentes | LangChain                                  |
| LLM                     | Google Gemini (`gemini-flash-latest`)      |
| Embeddings              | Google Gemini (`gemini-embedding-001`)     |
| Base vectorial          | ChromaDB (persistente)                     |
| Backend web             | FastAPI + Uvicorn                          |
| Frontend                | HTML + CSS + JavaScript (sin frameworks)   |
| Contenedor / Deploy     | Docker · Oracle Cloud Infrastructure (OCI) |

---

## 📁 Estructura del proyecto

```
Trompitas Agent/
├── base_conocimiento/     # 9 documentos .txt (info oficial de la clínica) + índice
├── src/
│   ├── config.py          # modelos, rutas y parámetros
│   ├── ingest.py          # Paso 3: chunking + embeddings → Chroma
│   ├── rag.py             # Paso 4: cadena RAG (retriever + Gemini)
│   ├── prompts.py         # personalidad y reglas de LuiM
│   ├── tools.py           # herramientas: buscar_informacion, agendar_cita
│   ├── agent.py           # Paso 5: agente + trazabilidad (logs)
│   └── api.py             # Paso 6: backend FastAPI (sirve la web + /chat)
├── web/
│   └── index.html         # interfaz web de LuiM
├── data/                  # base vectorial, citas y logs (generados)
├── requirements.txt
├── Dockerfile · start.sh · .env.example
```

---

## 🚀 Instalación y uso (local)

**Requisitos:** Python 3.11 y una API key de Google AI Studio (Gemini).

```bash
# 1. Entorno e instalación
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configura tu clave (copia .env.example a .env y pon tu clave)
#    GOOGLE_API_KEY=tu_clave

# 3. Construye la base vectorial (indexación)
cd src && python ingest.py

# 4. Levanta la interfaz web
../.venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000
```

Abre **http://localhost:8000** 🐘

> También puedes probar en terminal: `python agent.py "¿cuánto cuesta la consulta?"`

### Configuración (`.env`)

```env
GOOGLE_API_KEY=tu_clave_de_google_ai_studio
```

---

## 💬 Ejemplos de preguntas y respuestas

**P: ¿Cuánto cuesta un equipo como el iR-ADV DX C5870i?**

> La inversión final depende del modelo y los accesorios que elijas (unidades de papel, finalizadores, software). Para darte una cifra exacta, te recomiendo una **asesoría personalizada sin costo**, donde analizamos tu flujo de trabajo y te entregamos una cotización formal a través de nuestro distribuidor autorizado. Lo que sí puedo adelantarte es que este equipo ofrece **70 ppm en A4 y 36 ppm en A3**, con un consumo típico muy eficiente. _Fuente: Ficha técnica serie C5800._

**P: ¿Qué velocidades manejan para impresión a color en formatos grandes?**

> Para color y alta productividad, la serie C5800 alcanza hasta **70 ppm en A4** (C5870i) y **36 ppm en A3**. Para volúmenes más moderados, la serie C3900 ofrece desde 22 hasta 35 ppm en A4. Si necesitas tamaños SRA3 o papel de hasta 300 g/m², todos los modelos lo soportan en la bandeja multipropósito. _Fuente: Especificaciones de impresión (fichas C3900 y C5800)._

**P: ¿Tienen disponibilidad inmediata del modelo 6860i?** _(dato que NO está en la base)_

> Eso no lo tengo con certeza en mi base de conocimiento, ya que la disponibilidad varía por región y distribuidor. Permíteme conectarte con un ejecutivo comercial humano para que te confirme inventario y tiempos de entrega. Escríbenos al correo {correo_comercial} o déjame tu número y te contactan. _(No inventa el dato; escala a humano.)_

**P: ¿Qué opciones de acabado puedo añadir a mi equipo?**

> Dependiendo del modelo, puedes integrar finalizadores que permiten **grapado** (hasta 50 hojas en A4), **perforado** (2 o 4 agujeros), **encuadernación en cuadernillo** y **plegado en V, C o zigzag** (disponible en serie 6800). También hay bandejas de salida adicionales para aumentar la capacidad hasta 3450 hojas. Te recomiendo definir estos detalles en la asesoría para que la cotización sea precisa. _Fuente: Opciones de acabado (fichas técnicas)._

**P: ¿Cuál es el horario para agendar una demostración del equipo?**

> Las asesorías y demostraciones se coordinan de **lunes a viernes de 9:00 a 18:00 hrs**. Fuera de ese horario, el asistente LuiM queda activo para recibir tu solicitud y te contactaremos al inicio del siguiente día hábil. Para temas de soporte técnico post-venta, contamos con canales específicos (consultar con tu distribuidor). _Fuente: Horario de atención comercial (guion LuiM)._

**Ejemplo de agendamiento:**

> _Usuario:_ "Quiero agendar una demo del C5860i para mi oficina, el martes a las 3pm. Mi empresa imprime unas 25,000 hojas al mes en color. Teléfono 55-1234-5678."
> _LuiM:_ "¡Perfecto, {nombre}! ✅ Quedó agendada tu demostración del equipo C5860i:
> 🗓️ martes
> 🕒 3:00 pm
> 📋 Tema: Evaluación del equipo para volumen de 25,000 hojas/mes en color.
> 📞 Confirmamos tu contacto: 51-1234-5678.
> Si necesitas reagendar, avísanos con al menos 4 horas de anticipación. ¡Prepara tus muestras de papel y te ayudamos a elegir la mejor solución! 🖨️"
> _(LuiM registra la cita y confirma.)_

---

## **Nota importante:** Todas las respuestas técnicas están respaldadas por las fichas oficiales de Canon. Si el usuario pregunta por datos no disponibles (precios exactos, stock, plazos de entrega), LuiM **no inventa** y ofrece el escalamiento a un ejecutivo comercial humano (C18).

## 📝 Trazabilidad (auditoría)

Cada interacción se guarda en `data/logs/interacciones.jsonl`:

```json
{
  "timestamp": "2026-07-26T03:41:03",
  "pregunta": "¿cuánto cuesta la consulta?",
  "respuesta": "...",
  "herramientas_usadas": ["buscar_informacion"]
}
```

---

## ☁️ Despliegue en la nube

La aplicación está desplegada como **contenedor Docker** y accesible públicamente:

**🔗 https://LuiM-comercial.onrender.com**

El despliegue usa el `Dockerfile` del proyecto: al arrancar, construye la base vectorial
(si no existe) y levanta el servidor web (`start.sh`). La única variable requerida es
`GOOGLE_API_KEY`, configurada como variable de entorno en la plataforma.

```bash
# Reproducible en cualquier host con Docker:
docker build -t LuiM-comercial .
docker run -d -p 8000:8000 -e GOOGLE_API_KEY="tu_clave" LuiM-comercial
```

---

## 📸 Evidencias

Aplicación **en vivo** y funcionando en la URL pública, con la interfaz de LuiM:

![Interfaz de LuiM en la URL pública](evidencias/evidencia-11.png)

El usuario pregunta en lenguaje natural sobre las consultas para niños:

![Pregunta sobre servicios para niños](evidencias/evidencia-12.png)

LuiM responde con precios y servicios reales, **citando la fuente** (base de conocimiento de la clínica):

![Respuesta con precios y fuente citada](evidencias/evidencia-13.png)

Otra consulta ("¿atienden bebés?"), con el indicador de "escribiendo":

![Consulta sobre atención a bebés](evidencias/evidencia-14.png)

Respuesta sobre equipos (Srta. Micaela Torres), nuevamente con la fuente citada:

![Respuesta sobre odontopediatría](evidencias/evidencia-15.png)

Flujo de **agendamiento** dentro del chat: LuiM solicita los datos para registrar la cita:

![Flujo de agendamiento de cita](evidencias/evidencia-16.png)

Recordatorios, políticas y LuiM **identificándose como asistente digital (IA)**:

![Recordatorios y disclaimer de IA](evidencias/evidencia-17.png)

---

## 🔜 Próximas iteraciones

- 📆 Integración real con **Google Calendar** (disponibilidad y creación de eventos).
- 💬 Conversación por **WhatsApp** (WhatsApp Business API).

---

## 👤 Autor

**Luis Miguel Cavero** — Challenge AlurAgente (Orquestación de Agentes IA).
