from app.core.container import Container

if __name__ == "__main__":

    rag = Container.get_rag()

    query = "¿Qué dice la ley Colombiana sobre el trabajo nocturno?"

    result = rag.ask(query)

    print(result["answer"])