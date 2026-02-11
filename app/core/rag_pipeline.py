# app/core/rag_pipeline.py

from app.services.prompt_builder import PromptBuilder

class RAGPipeline:

    def __init__(self, retriever, generator):
        self.retriever = retriever
        self.generator = generator

    def ask(self, query: str):

        documents = self.retriever.retrieve(query)

        messages = PromptBuilder.build_messages(query, documents)

        answer = self.generator.generate(messages)

        return {
            "answer": answer,
            "sources": [
                {
                    "source": doc.metadata.get("source"),
                    "score": doc.metadata.get("score"),
                }
                for doc in documents
            ]
        }
