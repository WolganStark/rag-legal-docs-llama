# RAG Legal Docs (Llama + Groq + Chroma + FastAPI + Streamlit)

Este repositorio implementa una base de **RAG (Retrieval-Augmented Generation)** para consultar documentos legales en PDF (laborales, privacidad, GDPR, etc.) usando:

- **Ingesta y chunking** con LangChain.
- **Embeddings** con Sentence Transformers.
- **Vector store** local con ChromaDB.
- **Generación** con **Groq** usando el modelo **`llama-3.3-70b-versatile`**.
- **Orquestación** con un pipeline sencillo (`RAGPipeline`).
- **Frontend** construido con **Streamlit**.

---

## 1) Revisión rápida del código base

### Arquitectura actual

- `app/ingest/ingest.py`
  - Carga PDFs con `PyMuPDFLoader`.
  - Enriquecimiento de metadata (`jurisdiction`, `document_type`, `language`, `source`).
  - Chunking con `RecursiveCharacterTextSplitter`.

- `app/vector_store/index_documents.py`
  - Ejecuta la indexación de chunks:
    1. Carga documentos.
    2. Calcula embeddings.
    3. Guarda en Chroma.

- `app/services/embeddings.py`
  - Capa de embeddings (`SentenceTransformer`) para documentos y consultas.

- `app/services/retriever.py`
  - Consulta Chroma con embeddings de query y retorna `top_k` documentos con score.

- `app/services/generator.py`
  - Llama a Groq y devuelve la respuesta final usando `llama-3.3-70b-versatile`.

- `app/core/rag_pipeline.py`
  - Flujo end-to-end: retrieve -> prompt -> generate.

- `app/core/container.py`
  - Ensambla e inyecta dependencias (estilo singleton simple).

- `app/main.py`
  - Punto de ejecución local por script (sin API web).

---

## 2) Siguiente paso: crear API con FastAPI (local)

A continuación te lo explico en el formato que pediste: **conceptual -> técnico -> código**.

### 2.1 Conceptual

El siguiente paso es encapsular tu pipeline RAG detrás de una interfaz HTTP para poder:

1. Probar el sistema desde cualquier cliente (`curl`, Postman, frontend).
2. Separar responsabilidades:
   - El motor RAG responde preguntas.
   - FastAPI expone endpoints y contratos de entrada/salida.
3. Preparar terreno para producción (autenticación, rate limit, observabilidad), empezando con pruebas locales.

En términos simples:

- Antes: ejecutas `python app/main.py` y una query fija.
- Después: levantas servidor (`uvicorn`) y haces `POST /api/v1/ask` con cualquier pregunta.

### 2.2 Técnico

Para pruebas locales, el mínimo viable es:

1. **App FastAPI** con metadata básica (`title`, `version`).
2. **Router versionado** (`/api/v1`) con:
   - `GET /health` para verificar que el servicio está arriba.
   - `POST /ask` para enviar la pregunta.
3. **Esquemas Pydantic** para request/response.
4. **Integración con `Container.get_rag()`** para reutilizar tu pipeline actual sin reescribir lógica.
5. **Ejecución local con Uvicorn** y pruebas con `curl`.

### 2.3 Código propuesto (ya agregado al repo)

Se agregaron estos archivos:

- `app/api/server.py`: crea y expone la app de FastAPI.
- `app/api/routes.py`: define endpoints y modelos Pydantic.

#### Levantar API local

```bash
uvicorn app.api.server:app --host 0.0.0.0 --port 8000 --reload
```

#### Probar healthcheck

```bash
curl http://localhost:8000/api/v1/health
```

#### Probar consulta RAG

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Qué dice la ley Colombiana sobre el trabajo nocturno?"}'
```

---

## 3) Instalación y ejecución del proyecto

## Requisitos

- Python 3.11+
- API Key de Groq
- Dependencias del proyecto

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Variables de entorno (`.env`)

Crea un archivo `.env` en la raíz con al menos:

```env
# App
APP_NAME=RAG Legal API
ENVIRONMENT=local
LOG_LEVEL=INFO

# LLM (Groq)
LLM_PROVIDER=groq
GROQ_API_KEY=tu_api_key_de_groq
GROQ_MODEL=llama-3.3-70b-versatile

# Embeddings
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector DB
VECTOR_DB=chroma
VECTOR_DB_PATH=./data/chroma
CHROMA_COLLECTION=legal_docs

# Chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=150

# Device
DEVICE=cpu

# Index
REBUILD_INDEX=false
```

### Indexar documentos

```bash
python -m app.vector_store.index_documents
```

### Ejecutar consulta por script

```bash
python app/main.py
```

### Ejecutar API local

```bash
uvicorn app.api.server:app --host 0.0.0.0 --port 8000 --reload
```

Docs automáticas:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Ejecutar frontend Streamlit

```bash
streamlit run app/frontend/streamlit_app.py
```

---

## 4) Próximos pasos recomendados

1. Mover modelos Pydantic a `app/api/schemas.py` si crece la API.
2. Agregar endpoint de `POST /reindex` para disparar indexación controlada.
3. Añadir tests API (pytest + TestClient).
4. Incorporar validaciones de negocio (límite de longitud de query, idioma, etc.).
5. Estandarizar errores con un formato común (`code`, `message`, `details`).

---

## 5) Estado actual

- ✅ Pipeline RAG funcional en modo script.
- ✅ API FastAPI mínima para pruebas locales.
- ✅ Frontend en Streamlit para interacción del usuario.
- 🔜 Falta robustecer tests, manejo de errores y estrategia de despliegue.
