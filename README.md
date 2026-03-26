# RAG Legal Docs

Sistema de consulta inteligente sobre documentos legales basado en **RAG (Retrieval-Augmented Generation)**. Permite hacer preguntas en lenguaje natural sobre documentos legales en PDF y obtener respuestas contextualizadas respaldadas por las fuentes originales.

---

## Tecnologías principales

| Componente | Tecnología |
|---|---|
| LLM | [Groq](https://groq.com) — `llama-3.3-70b-versatile` |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Vector Store | [ChromaDB](https://www.trychroma.com) |
| Ingesta | [LangChain](https://langchain.com) + PyMuPDF |
| API | [FastAPI](https://fastapi.tiangolo.com) + Uvicorn |
| Frontend | [Streamlit](https://streamlit.io) |
| Contenedores | Docker + Docker Compose |
| Infraestructura | AWS EC2 (t3.micro) + S3 + ECR |

---

## Arquitectura del sistema

### Flujo de inferencia

```
Usuario
   │
   ▼
┌─────────────────────┐
│  Frontend Streamlit  │  puerto 8501
│  (frontend/app.py)  │
└──────────┬──────────┘
           │ POST /api/v1/ask
           ▼
┌─────────────────────┐
│    API FastAPI       │  puerto 8000
│  (app/api/server)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    RAG Pipeline      │
│                     │
│  1. Query embedding  │◄── SentenceTransformer
│  2. Retriever        │◄── ChromaDB (top_k=3)
│  3. Prompt builder   │
│  4. Generator        │◄── Groq API
└──────────┬──────────┘
           │
           ▼
       Respuesta + Sources
```

### Flujo de indexación

```
PDFs en S3
   │
   ▼
┌─────────────────────┐
│    ingest.py         │
│  - PyMuPDFLoader    │
│  - Metadata enrich  │
│  - Chunking         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  EmbeddingService   │
│  SentenceTransformer│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     ChromaDB        │
│  (vector store)     │
└─────────────────────┘
```

### Arquitectura de despliegue en AWS

```
Internet
   │
   ▼
┌──────────────────────────────────────────┐
│           EC2 t3.micro (Ubuntu 22.04)    │
│                                          │
│  ┌─────────────────┐  ┌───────────────┐  │
│  │  rag-legal-api  │  │rag-legal-front│  │
│  │   FastAPI       │  │  Streamlit    │  │
│  │   :8000         │  │  :8501        │  │
│  └────────┬────────┘  └───────────────┘  │
│           │                              │
│  ┌────────▼────────┐                     │
│  │    ChromaDB     │  (volumen Docker)   │
│  │  EBS 20GB gp2   │                     │
│  └─────────────────┘                     │
│                                          │
│  IAM Role: rag-ec2-ssm-role              │
│  Acceso: SSM Session Manager (sin SSH)   │
└──────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────┐      ┌──────────────────┐
│  Groq API   │      │    AWS S3        │
│  (LLM)      │      │  raw_documents/  │
│  Gratuito   │      │  (PDFs fuente)   │
└─────────────┘      └──────────────────┘
         │
         ▼
┌─────────────────────┐
│  AWS ECR            │
│  rag-api:latest     │
│  rag-frontend:latest│
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  AWS Parameter Store│
│  /rag-legal/groq-.. │
│  /rag-legal/hf-...  │
└─────────────────────┘
```

---

## Estructura del proyecto

```
rag-legal-docs-llama/
├── app/
│   ├── api/
│   │   ├── routes.py          # Endpoints FastAPI
│   │   └── server.py          # Configuración de la app
│   ├── config/
│   │   └── settings.py        # Variables de entorno con Pydantic
│   ├── core/
│   │   ├── container.py       # Inyección de dependencias
│   │   └── rag_pipeline.py    # Pipeline end-to-end
│   ├── ingest/
│   │   └── ingest.py          # Carga PDFs desde S3 o local
│   ├── services/
│   │   ├── embeddings.py      # SentenceTransformer
│   │   ├── generator.py       # Groq API
│   │   └── retriever.py       # Búsqueda en ChromaDB
│   └── vector_store/
│       ├── chroma_client.py   # Cliente ChromaDB
│       └── index_documents.py # Script de indexación
├── frontend/
│   ├── app.py                 # Interfaz Streamlit
│   └── requirements.txt       # Dependencias del frontend
├── data/
│   └── raw_documents/         # PDFs locales (desarrollo)
├── docs/
│   └── evaluation/            # Evaluación de calidad del sistema
├── tests/
├── Dockerfile                 # Imagen de la API
├── Dockerfile.streamlit       # Imagen del frontend
├── docker-compose.yml         # Base compartida
├── docker-compose.override.yml# Configuración local
├── docker-compose.prod.yml    # Configuración producción (AWS)
└── requirements.txt
```

---

## Instalación y ejecución local

### Requisitos previos

- Python 3.11+
- API Key de [Groq](https://console.groq.com/keys) (gratuita)
- Token de [HuggingFace](https://huggingface.co/settings/tokens) (gratuito, tipo Read)

### 1. Clonar el repositorio

```bash
git clone https://github.com/WolganStark/rag-legal-docs-llama.git
cd rag-legal-docs-llama
```

### 2. Crear y activar entorno virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```dotenv
# App
APP_NAME=rag-legal-docs
ENVIRONMENT=development
LOG_LEVEL=INFO

# LLM (Groq Cloud)
LLM_PROVIDER=groq
GROQ_API_KEY=tu_api_key_de_groq
GROQ_MODEL=llama-3.3-70b-versatile

# Embeddings
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
HF_TOKEN=tu_token_de_huggingface

# Vector DB
VECTOR_DB=chroma
VECTOR_DB_PATH=./data/processed/vector_index
CHROMA_COLLECTION=knowledge_base

# Chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=150

# Device
DEVICE=cpu

# Rebuild Index
REBUILD_INDEX=true

# Frontend
API_URL=http://localhost:8000
DOCS_PATH=./data/raw_documents
```

> ⚠️ Nunca subas el archivo `.env` al repositorio. Está incluido en `.gitignore`.

### 5. Agregar documentos PDF

Coloca tus documentos PDF en `data/raw_documents/` organizados en subcarpetas:

```
data/raw_documents/
├── gdpr/
├── legal/
└── privacy/
```

### 6. Indexar documentos

```bash
python -m app.vector_store.index_documents
```

### 7. Levantar la API

```bash
uvicorn app.api.server:app --host 127.0.0.1 --port 8000 --reload
```

La documentación Swagger estará disponible en `http://localhost:8000/docs`.

### 8. Levantar el frontend

En otra terminal (con el entorno virtual activo):

```bash
streamlit run frontend/app.py
```

El frontend estará disponible en `http://localhost:8501`.

---

## Ejecución con Docker

### Requisitos previos

- Docker Desktop instalado
- Variables de entorno configuradas en `.env`

### Levantar todos los servicios

```bash
# Construir las imágenes
docker-compose build

# Levantar los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Detener los servicios
docker-compose down
```

### Indexar documentos en Docker

```bash
docker-compose exec api python -m app.vector_store.index_documents
```

### Servicios disponibles

| Servicio | URL |
|---|---|
| API (Swagger) | `http://localhost:8000/docs` |
| Frontend | `http://localhost:8501` |

---

## Endpoints de la API

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/v1/health` | Verificar estado del servicio |
| `GET` | `/api/v1/documents` | Listar documentos disponibles |
| `POST` | `/api/v1/ask` | Hacer una consulta al sistema RAG |

### Ejemplo de consulta

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Qué dice la ley colombiana sobre el trabajo nocturno?"}'
```

### Ejemplo de respuesta

```json
{
  "answer": "Según el Código del Trabajo colombiano, el trabajo nocturno...",
  "sources": [
    {
      "source": "codigo_trabajo_colombia.pdf",
      "score": 0.72
    }
  ]
}
```

---

## Evaluación de calidad

Se realizó una evaluación manual del sistema basada en el framework **RAGAS** con 10 preguntas distribuidas en tres categorías.

| Métrica | Resultado | Estado |
|---|---|---|
| Faithfulness | 2.9 / 3.0 | ✅ Bueno |
| Answer Relevancy | 1.1 / 3.0 | ❌ Mejorar |
| Context Precision | 0.44 / 3.0 | ❌ Mejorar |
| Context Recall | 0.9 / 3.0 | ❌ Mejorar |
| **Score Global** | **46.6 / 100** | **❌ Mejorar** |

| Categoría | Score |
|---|---|
| A — Preguntas directas | 36.7 / 100 |
| B — Preguntas de razonamiento | 33.3 / 100 |
| C — Preguntas límite (fuera del dominio) | 91.7 / 100 |

**Conclusión principal:** El sistema no alucina (Faithfulness casi perfecto) y maneja correctamente preguntas fuera del dominio. El problema central está en el retriever — el componente que busca los chunks relevantes en ChromaDB. El documento completo de evaluación está disponible en [`docs/evaluation/`](./docs/evaluation/).

---

## Mejoras futuras identificadas

Las siguientes mejoras están priorizadas para próximas versiones basadas en los resultados de la evaluación:

**Retriever**
- Aumentar `top_k` de 3 a 6-8 para mejorar la cobertura de chunks relevantes
- Implementar filtrado por metadata antes del retrieval (por jurisdicción, tipo de documento)
- Evaluar modelos de embeddings más robustos para documentos legales multilingüe

**Indexación**
- Resolver el problema de *index imbalance* — el Estatuto español (611 chunks) domina el espacio vectorial frente a documentos más cortos
- Implementar estrategia de chunking adaptativa según el tipo de sección legal (SemanticChunker)

**Sistema**
- Endpoint `POST /api/v1/documents/upload` para carga de nuevos documentos desde el frontend
- Autenticación con AWS Cognito para control de acceso
- Pipeline de evaluación automática con RAGAS integrado en CI/CD
- CI/CD completo con GitHub Actions para despliegue automático en EC2

---

## Notas de seguridad

- El acceso al servidor en AWS se realiza exclusivamente via **AWS SSM Session Manager** — el puerto 22 (SSH) está cerrado
- Las credenciales sensibles se almacenan en **AWS Parameter Store** como `SecureString`
- El bucket S3 con los documentos es privado — no tiene acceso público
- Los contenedores usan el **IAM Role** de la instancia para autenticarse con AWS sin credenciales explícitas

---

## Licencia

Este proyecto es de uso personal y forma parte del portafolio profesional del autor.
