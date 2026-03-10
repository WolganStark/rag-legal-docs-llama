"""
ingest.py

Pipeline de Ingesta para documentos legales.
Responsabilidades:
- Cargar PDFs desde S3 (producción) o sistema de archivos local (desarrollo)
- Extraer texto por página
- Aplicar chunking
- Enriquecer metadata
"""
import os
import tempfile
import boto3
from typing import List
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


DATA_DIR = Path("data/raw_documents")


def detect_metadata(filename: str) -> dict:
    filename_lower = filename.lower()

    if "colombia" in filename_lower:
        return {
            "jurisdiction": "Colombia",
            "document_type": "labor_law",
            "language": "es"
        }

    if "estatuto" in filename_lower:
        return {
            "jurisdiction": "Spain",
            "document_type": "labor_law",
            "language": "es"
        }

    if "gdpr" in filename_lower:
        return {
            "jurisdiction": "EU",
            "document_type": "regulation",
            "language": "en"
        }

    return {
        "jurisdiction": "Unknown",
        "document_type": "Unknown",
        "language": "Unknown"
    }


def load_pdfs_from_s3(bucket: str, prefix: str) -> List[Document]:
    """
    Descarga PDFs desde S3 a un directorio temporal y los procesa.
    boto3 usa automáticamente el IAM Role de la EC2 sin credenciales explícitas.
    """
    s3 = boto3.client("s3")
    documents = []

    # Lista todos los objetos en el bucket con el prefijo dado
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

    for page in pages:
        for obj in page.get("Contents", []):
            key = obj["Key"]

            # Solo procesa archivos PDF
            if not key.endswith(".pdf"):
                continue

            # Nombre del archivo sin la ruta del bucket
            filename = Path(key).name

            # Descarga el PDF a un archivo temporal
            # tempfile.NamedTemporaryFile crea un archivo temporal que se
            # elimina automáticamente al salir del bloque with
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                s3.download_fileobj(bucket, key, tmp)
                tmp_path = tmp.name

            try:
                loader = PyMuPDFLoader(tmp_path)
                docs = loader.load()

                semantic_metadata = detect_metadata(filename)

                for d in docs:
                    d.metadata.update({
                        "source": filename,
                        **semantic_metadata
                    })

                documents.extend(docs)

            except Exception as e:
                print(f"Error al procesar {filename}: {e}")

            finally:
                # Elimina el archivo temporal del disco
                os.unlink(tmp_path)

    return documents


def load_pdfs_from_local(data_dir: Path) -> List[Document]:
    """
    Carga PDFs recursivamente desde el sistema de archivos local.
    Se usa en desarrollo cuando S3_BUCKET no está configurado.
    """
    documents = []

    # rglob busca recursivamente en subcarpetas — reemplaza glob("*.pdf")
    for pdf_path in data_dir.rglob("*.pdf"):
        try:
            loader = PyMuPDFLoader(str(pdf_path))
            docs = loader.load()

            semantic_metadata = detect_metadata(pdf_path.name)

            for d in docs:
                d.metadata.update({
                    "source": pdf_path.name,
                    **semantic_metadata
                })

            documents.extend(docs)

        except Exception as e:
            print(f"Error al procesar {pdf_path.name}: {e}")

    return documents


def load_all_pdfs(data_dir: Path = DATA_DIR) -> List[Document]:
    """
    Punto de entrada principal. Decide automáticamente si usar S3 o local
    basándose en la variable de entorno S3_BUCKET.
    """
    s3_bucket = os.getenv("S3_BUCKET")
    s3_prefix = os.getenv("S3_PREFIX", "raw_documents/")

    if s3_bucket:
        print(f"[Ingest] Cargando PDFs desde S3: s3://{s3_bucket}/{s3_prefix}")
        documents = load_pdfs_from_s3(s3_bucket, s3_prefix)
    else:
        print(f"[Ingest] Cargando PDFs desde local: {data_dir}")
        documents = load_pdfs_from_local(data_dir)

    print(f"[Ingest] {len(documents)} páginas cargadas")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(documents)
    print(f"[Ingest] {len(chunks)} chunks generados")

    return chunks