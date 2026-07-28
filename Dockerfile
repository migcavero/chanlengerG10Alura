# Imagen para desplegar el agente Cindy (Trompitas Dental) en OCI.
FROM python:3.12-slim

WORKDIR /app

# Dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código y base de conocimiento
COPY . .

# La app escucha en el 8000
EXPOSE 8000

# Al arrancar: si no existe la base vectorial, se construye (necesita GOOGLE_API_KEY);
# luego se levanta el servidor web.
CMD ["sh", "start.sh"]
