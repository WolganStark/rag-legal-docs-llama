"""
Frontend Streamlit para RAG Legal Docs
--------------------------------------
Interfaz minimalista para consultar documentos legales
mediante la API de FastAPI.
"""

# ── Importaciones ──────────────────────────────────────────────────────────────
import os           # Para leer variables de entorno del sistema operativo
import requests     # Para hacer llamadas HTTP a la API de FastAPI
import streamlit as st  # El framework principal del frontend

# ── Configuración general de la página ────────────────────────────────────────
# Esta función DEBE ser la primera llamada a Streamlit en el script.
# Define el título de la pestaña del navegador, el ícono y el layout.
st.set_page_config(
    page_title="RAG Legal Docs",
    page_icon="⚖️",
    layout="centered",   # "centered" centra el contenido | "wide" usa todo el ancho
)

# ── Estilos CSS personalizados ─────────────────────────────────────────────────
# st.markdown con unsafe_allow_html=True permite inyectar HTML/CSS directamente.
# Aquí definimos la paleta de colores y ajustamos componentes de Streamlit.
st.markdown("""
    <style>
        /* Fuente principal del cuerpo */
        html, body, [class*="css"] {
            font-family: 'Georgia', serif;
        }

        /* Color de fondo de la app */
        .stApp {
            background-color: #F9F7F4;
        }

        /* Estilo del cuadro de respuesta */
        .answer-box {
            background-color: #FFFFFF;
            border-left: 4px solid #2C3E50;
            padding: 1.2rem 1.5rem;
            border-radius: 4px;
            margin-top: 1rem;
            color: #1A1A1A;
            line-height: 1.7;
        }

        /* Estilo de cada fuente recuperada */
        .source-chip {
            display: inline-block;
            background-color: #EAE6DF;
            color: #2C3E50;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.78rem;
            margin: 0.2rem;
        }

        /* Estilo del título principal */
        h1 {
            color: #2C3E50 !important;
            font-weight: 700;
            letter-spacing: -0.5px;
        }

        /* Subtítulo */
        .subtitle {
            color: #7F8C8D;
            font-size: 0.95rem;
            margin-top: -0.8rem;
            margin-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# ── URL base de la API ─────────────────────────────────────────────────────────
# Lee la variable de entorno API_URL. Si no existe, usa localhost como fallback.
# En Docker, este valor vendrá del docker-compose (http://api:8000).
# En local, apunta a tu Uvicorn corriendo en el puerto 8000.
API_URL = os.getenv("API_URL", "http://localhost:8000")

# ── Función para consultar la API ──────────────────────────────────────────────
def ask_api(query: str) -> dict:
    """
    Envía una pregunta al endpoint POST /api/v1/ask de FastAPI.
    Retorna el JSON de respuesta con 'answer' y 'sources'.
    Lanza una excepción si la llamada falla.
    """
    response = requests.post(
        f"{API_URL}/api/v1/ask",
        json={"query": query},  # El body que espera AskRequest en routes.py
        timeout=60              # Espera máximo 60 segundos (el LLM puede tardar)
    )
    response.raise_for_status()  # Lanza HTTPError si el status code es 4xx o 5xx
    return response.json()       # Retorna el dict con 'answer' y 'sources'


# ── Función para obtener documentos disponibles ────────────────────────────────
def get_available_documents() -> list[str]:
    """
    Recorre recursivamente la carpeta de documentos y sus subcarpetas
    para encontrar todos los PDFs disponibles.
    """
    docs_path = os.getenv("DOCS_PATH", "./data/raw_documents")
    try:
        pdf_files = []
        # os.walk recorre el árbol de directorios:
        # - root: carpeta actual en cada iteración
        # - dirs: subcarpetas dentro de root (no se usa aquí)
        # - files: archivos dentro de root
        for root, dirs, files in os.walk(docs_path):
            for file in files:
                if file.endswith(".pdf"):
                    # Construye la ruta relativa desde docs_path
                    # Ej: "gdpr/reglamento_gdpr.pdf" en lugar de la ruta absoluta
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, docs_path)
                    pdf_files.append(relative_path)

        return sorted(pdf_files)
    except FileNotFoundError:
        return []


# ── Encabezado principal ───────────────────────────────────────────────────────
# st.title renderiza un <h1> en la página
st.title("⚖️ RAG Legal Docs")

# st.markdown renderiza HTML/Markdown directamente
st.markdown('<p class="subtitle">Consulta inteligente sobre documentos legales</p>',
            unsafe_allow_html=True)

# st.divider dibuja una línea horizontal separadora
st.divider()

# ── Sidebar: documentos disponibles ───────────────────────────────────────────
# st.sidebar es un panel lateral izquierdo, ideal para info de contexto
with st.sidebar:
    st.header("📁 Documentos disponibles")

    # Llama a la función para obtener los PDFs
    docs = get_available_documents()

    if docs:
        # Agrupa por subcarpeta para mostrar organizadamente
        current_folder = None
        for doc in docs:
            # os.path.dirname extrae la carpeta padre del archivo
            # Ej: de "gdpr/archivo.pdf" extrae "gdpr"
            folder = os.path.dirname(doc)
            file_name = os.path.basename(doc).replace(".pdf", "")

        # Si cambia de carpeta, muestra el nombre como encabezado
            if folder != current_folder:
                current_folder = folder
                if folder:  # Solo muestra encabezado si hay subcarpeta
                    st.markdown(f"**📂 {folder.upper()}**")

            st.markdown(f"&nbsp;&nbsp;&nbsp;• {file_name}")
    else:
        st.info("No se encontraron documentos en la ruta configurada.")

        st.divider()

        # Información del sistema en el sidebar
        st.caption(f"🔗 API: `{API_URL}`")
        st.caption("🤖 Modelo: llama-3.3-70b-versatile")
        st.caption("📦 Embeddings: paraphrase-multilingual-MiniLM-L12-v2")

# ── Cuerpo principal: formulario de consulta ───────────────────────────────────
# st.text_area crea una caja de texto multilinea
# - label: texto visible encima del input
# - placeholder: texto gris dentro del input cuando está vacío
# - height: altura en píxeles
query = st.text_area(
    label="Escribe tu consulta legal",
    placeholder="Ej: ¿Qué dice la ley colombiana sobre el trabajo nocturno?",
    height=100,
)

# st.button crea un botón que retorna True cuando el usuario hace clic
# use_container_width=True hace que el botón ocupe todo el ancho disponible
submitted = st.button("🔍 Consultar", use_container_width=True)

# ── Lógica de consulta ─────────────────────────────────────────────────────────
# Solo ejecuta si el usuario hizo clic en el botón
if submitted:

    # Validación básica: no enviar si el campo está vacío o tiene menos de 3 chars
    if not query or len(query.strip()) < 3:
        # st.warning muestra un mensaje amarillo de advertencia
        st.warning("Por favor escribe una consulta de al menos 3 caracteres.")
    else:
        # st.spinner muestra un indicador de carga mientras ejecuta el bloque
        # El texto dentro aparece junto al spinner
        with st.spinner("Consultando documentos legales..."):
            try:
                # Llama a la API con la pregunta del usuario
                result = ask_api(query.strip())

                # ── Mostrar respuesta ──────────────────────────────────────────
                st.subheader("📋 Respuesta")

                # Inyecta la respuesta dentro del div estilizado con CSS
                st.markdown(
                    f'<div class="answer-box">{result["answer"]}</div>',
                    unsafe_allow_html=True
                )

                # ── Mostrar fuentes ────────────────────────────────────────────
                sources = result.get("sources", [])  # Lista de SourceItem

                if sources:
                    st.subheader("📎 Fuentes consultadas")

                    # Construye los chips de fuentes como HTML
                    chips_html = ""
                    for source in sources:
                        # Extrae solo el nombre del archivo, no la ruta completa
                        source_name = source.get("source", "Desconocido")
                        file_name = os.path.basename(source_name)  # Ej: ley_laboral.pdf
                        score = source.get("score")

                        # Si hay score de similitud, lo muestra con 2 decimales
                        score_text = f" ({score:.2f})" if score is not None else ""
                        chips_html += f'<span class="source-chip">📄 {file_name}{score_text}</span>'

                    st.markdown(chips_html, unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                # Error específico cuando la API no está corriendo
                st.error("❌ No se pudo conectar con la API. ¿Está corriendo el servidor en "
                         f"`{API_URL}`?")

            except requests.exceptions.Timeout:
                # Error cuando el servidor tarda más de 60 segundos
                st.error("⏱️ La consulta tardó demasiado. Intenta con una pregunta más corta.")

            except requests.exceptions.HTTPError as e:
                # Error cuando la API retorna un status 4xx o 5xx
                st.error(f"❌ Error de la API: {e.response.status_code} - "
                         f"{e.response.json().get('detail', 'Error desconocido')}")

            except Exception as e:
                # Captura cualquier otro error inesperado
                st.error(f"❌ Error inesperado: {str(e)}")