import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "knowledge_base")