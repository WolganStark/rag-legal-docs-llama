# Base image — Python slim para reducir tamaño
FROM python:3.11-slim

# Evita que Python escriba .pyc y bufferiza stdout (importante para logs en AWS)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias primero (capa cacheada — si no cambia requirements.txt, Docker no reinstala)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Puerto que expone FastAPI
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "app.api.server:app", "--host", "0.0.0.0", "--port", "8000"]