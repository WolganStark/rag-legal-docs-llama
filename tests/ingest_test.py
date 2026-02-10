from app.rag.ingest import load_all_pdfs

docs = load_all_pdfs()

print(f"Total chunks: {len(docs)}")
print(docs[0])