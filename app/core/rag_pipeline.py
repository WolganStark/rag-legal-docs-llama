# app/core/rag_pipeline.py
import time
from app.core.logger import setup_logger
from app.services.prompt_builder import PromptBuilder

logger = setup_logger()

class RAGPipeline:

    def __init__(self, retriever, generator):
        self.retriever = retriever
        self.generator = generator

    def ask(self, query: str):

        logger.info(f"Received query: {query}")

        start_time = time.time()

        documents = self.retriever.retrieve(query)

        logger.info(f"Retrieved {len(documents)} documents")

        messages = PromptBuilder.build_messages(query, documents)

        answer = self.generator.generate(messages)

        elapsed = round(time.time() - start_time, 2)

        logger.info(f"Generated answer in {elapsed}s")

        return {
            "answer": answer,
            "sources": [
                {
                    "source": doc.metadata.get("source"),
                    "score": doc.metadata.get("score")
                }
                for doc in documents
            ]

        }

        
        
