import os
import requests
import streamlit as st

st.set_page_config(
    page_title="RAG Legal Docs",
    page_icon="⚖️",
    layout="centered",
)

st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Georgia', serif;
        }
        .stApp {
            background-color: #F9F7F4;
        }
        .answer-box {
            background-color: #FFFFFF;
            border-left: 4px solid #2C3E50;
            padding: 1.2rem 1.5rem;
            border-radius: 4px;
            margin-top: 1rem;
            color: #1A1A1A;
            line-height: 1.7;
        }
        .source-chip {
            display: inline-block;
            background-color: #EAE6DF;
            color: #2C3E50;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.78rem;
            margin: 0.2rem;
        }
        h1 {
            color: #2C3E50 !important;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .subtitle {
            color: #7F8C8D;
            font-size: 0.95rem;
            margin-top: -0.8rem;
            margin-bottom: 2rem;
        }
        .loading-overlay {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem 0;
            gap: 1rem;
        }
        .spinner {
            width: 48px;
            height: 48px;
            border: 4px solid #EAE6DF;
            border-top: 4px solid #2C3E50;
            border-radius: 50%;
            animation: spin 0.9s linear infinite;
        }
        @keyframes spin {
            0%   { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .loading-text {
            color: #7F8C8D;
            font-size: 0.9rem;
            font-family: 'Georgia', serif;
        }
    </style>
""", unsafe_allow_html=True)

API_URL = os.getenv("API_URL", "http://localhost:8000")


def ask_api(query: str) -> dict:
    response = requests.post(
        f"{API_URL}/api/v1/ask",
        json={"query": query},
        timeout=180
    )
    response.raise_for_status()
    return response.json()


def get_available_documents() -> dict[str, list[str]]:
    """
    Llama al endpoint GET /api/v1/documents de FastAPI.
    Retorna un dict agrupado por carpeta: {"gdpr": ["archivo1"], "legal": [...]}
    """
    try:
        response = requests.get(f"{API_URL}/api/v1/documents", timeout=10)
        response.raise_for_status()
        return response.json().get("documents", {})
    except Exception:
        # Si la API no está disponible, retorna vacío sin crashear
        return {}


# ── Encabezado ─────────────────────────────────────────────────────────────────
st.title("⚖️ RAG Legal Docs")
st.markdown('<p class="subtitle">Consulta inteligente sobre documentos legales</p>',
            unsafe_allow_html=True)
st.divider()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Documentos disponibles")

    docs = get_available_documents()

    if docs:
        for folder, files in docs.items():
            if folder:
                st.markdown(f"**📂 {folder.upper()}**")
            for file_name in files:
                st.markdown(f"&nbsp;&nbsp;&nbsp;• {file_name}")
    else:
        st.info("No se encontraron documentos o la API no está disponible.")

    st.divider()
    st.caption(f"🔗 API: `{API_URL}`")
    st.caption("🤖 Modelo: llama-3.3-70b-versatile")
    st.caption("📦 Embeddings: paraphrase-multilingual-MiniLM-L12-v2")

# ── Consulta ───────────────────────────────────────────────────────────────────
query = st.text_area(
    label="Escribe tu consulta legal",
    placeholder="Ej: ¿Qué dice la ley colombiana sobre el trabajo nocturno?",
    height=100,
)

submitted = st.button("🔍 Consultar", use_container_width=True)

if submitted:
    if not query or len(query.strip()) < 3:
        st.warning("Por favor escribe una consulta de al menos 3 caracteres.")
    else:
        loading_placeholder = st.empty()
        loading_placeholder.markdown("""
            <div class="loading-overlay">
                <div class="spinner"></div>
                <p class="loading-text">Consultando documentos legales...</p>
            </div>
        """, unsafe_allow_html=True)

        try:
            result = ask_api(query.strip())
            loading_placeholder.empty()

            st.subheader("📋 Respuesta")
            st.markdown(
                f'<div class="answer-box">{result["answer"]}</div>',
                unsafe_allow_html=True
            )

            sources = result.get("sources", [])
            if sources:
                st.subheader("📎 Fuentes consultadas")
                chips_html = ""
                for source in sources:
                    source_name = source.get("source", "Desconocido")
                    file_name = os.path.basename(source_name)
                    score = source.get("score")
                    score_text = f" ({score:.2f})" if score is not None else ""
                    chips_html += f'<span class="source-chip">📄 {file_name}{score_text}</span>'
                st.markdown(chips_html, unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            loading_placeholder.empty()
            st.error(f"❌ No se pudo conectar con la API en `{API_URL}`.")

        except requests.exceptions.Timeout:
            loading_placeholder.empty()
            st.error("⏱️ La consulta tardó demasiado. Intenta con una pregunta más corta.")

        except requests.exceptions.HTTPError as e:
            loading_placeholder.empty()
            st.error(f"❌ Error de la API: {e.response.status_code} - "
                     f"{e.response.json().get('detail', 'Error desconocido')}")

        except Exception as e:
            loading_placeholder.empty()
            st.error(f"❌ Error inesperado: {str(e)}")