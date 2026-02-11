# app/services/prompt_builder.py

from typing import List, Dict
from langchain_core.documents import Document


class PromptBuilder:

    @staticmethod
    def build_context(documents: List[Document]) -> str:
        """
        Formats retrieved documents into structured context.
        """

        context_blocks = []

        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown source")
            score = round(doc.metadata.get("score", 0), 3)

            context_blocks.append(
                f"[Documento {i} | Fuente: {source} | Score: {score}]\n"
                f"{doc.page_content}"
            )

        return "\n\n".join(context_blocks)

    @staticmethod
    def build_messages(query: str, documents: List[Document]) -> List[Dict]:

        context = PromptBuilder.build_context(documents)

        system_message = """
    Eres un asistente legal especializado en análisis documental.

    Tu tarea es responder preguntas usando EXCLUSIVAMENTE
    la información contenida en los documentos proporcionados.

    Reglas:
    - No inventes información.
    - Si la respuesta no está explícitamente en los documentos, responde:
    "No tengo suficiente información en los documentos proporcionados."
    - Responde en el mismo idioma que la pregunta.
    - Cita el número del documento cuando sea relevante.
    """

        user_message = f"""
    A continuación se presentan los documentos recuperados:

    {context}

    Usando únicamente la información anterior,
    responde la siguiente pregunta:

    {query}
    """

        return [
            {"role": "system", "content": system_message.strip()},
            {"role": "user", "content": user_message.strip()},
        ]

