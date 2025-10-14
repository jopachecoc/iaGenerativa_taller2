# primero ejecutar: desde la terminal 
# uv init creacr el archivo .toml
# uv venv # crea el entorno virtual #python3.11.13
# uv pip install --requirements requirements.txt # dependencias
# uv venv install # instala dependencias del lockfile
# uv pip install -r requirements.txt

# is a la pagina de https://jina.ai/api-dashboard/embedding para generar si api kei.
# export JINA_API_KEY="jina_772f..." #esto colocarlo en el bash


# uv pip install requests # con este se instala requests en el entorno virtual
# uv pip install rich fastapi # guarda en el lockfile
# uv run script.py # ejecuta scrip dentro del entorno
# uv pip install #esto carga todas las dependencias del lockfile



#export JINA_API_KEY="" #esto colocarlo en el bash
#export PINECONE_API_KEY=""
# rm uv.lock para limpiar todo lockfile


import os
import sys
import argparse
from uuid import uuid4
from typing import List

import pandas as pd
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_community.embeddings import JinaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# NOTE: uso la API similar a la que tenías en el archivo original
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

#from langchain_pinecone.vectorstores import Pinecone, PineconeVectorStore


# Función para leer PDF
def leer_pdf(ruta_pdf: str) -> str:
    """Leer todo el texto de un PDF y devolverlo como string."""
    texto = ""
    with open(ruta_pdf, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                texto += page_text + "\n"
    return texto


def leer_txt(ruta_txt: str) -> str:
    """Leer un .txt y devolver su contenido."""
    with open(ruta_txt, "r", encoding="utf-8") as f:
        return f.read()


def leer_excel(ruta_excel: str) -> str:
    """Leer un Excel y concatenar filas en texto (usa pandas + openpyxl)."""
    df = pd.read_excel(ruta_excel, engine="openpyxl")
    # Convertir cada fila en una línea de texto
    filas = df.astype(str).apply(lambda r: " ".join(r.values), axis=1)
    return "\n".join(filas.tolist())


def inicializar_embeddings() -> JinaEmbeddings:
    """Inicializa JinaEmbeddings usando la variable de entorno JINA_API_KEY."""
    api_key = os.getenv("JINA_API_KEY")
    if not api_key:
        raise ValueError("❌ No se encontró la variable de entorno JINA_API_KEY")
    return JinaEmbeddings(jina_api_key=api_key, model_name="jina-embeddings-v2-base-es")


def inicializar_pinecone(index_name: str = "tarea-jj-index"):
    """Inicializa/abre un índice en Pinecone y devuelve el objeto Index."""
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        raise ValueError("❌ No se encontró la variable de entorno PINECONE_API_KEY")

    pc = Pinecone(api_key=pinecone_api_key)

    # Si el índice no existe, crearlo (dimension debe coincidir con embeddings)
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    index = pc.Index(index_name)
    return index


def insertar_embeddings_en_pinecone(embeddings: List[List[float]], chunks: List[str], index):
    """
    Inserta vectores en Pinecone.
    Intenta el formato clásico (tupla) y, si falla, usa dicts.
    """
    vectors_for_upsert = []
    for i, vec in enumerate(embeddings):
        vid = f"doc_{i}_{uuid4().hex[:8]}"
        metadata = {"text": chunks[i]}
        # Preparar en forma que suelen aceptar clients nuevos/clásicos
        vectors_for_upsert.append({"id": vid, "values": list(vec), "metadata": metadata})

    # Muchos clientes Pinecone aceptan index.upsert(vectors=...)
    try:
        index.upsert(vectors=vectors_for_upsert)
    except TypeError:
        # alternativa: algunos clientes aceptan lista de tuplas (id, values, metadata)
        try:
            tuples = [(v["id"], v["values"], v["metadata"]) for v in vectors_for_upsert]
            index.upsert(tuples)
        except Exception as e:
            raise RuntimeError("Upsert a Pinecone falló: " + str(e))


def chunking_recursivo(texto: str) -> List[str]:
    """Divide el texto en chunks manejables usando RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    return splitter.split_text(texto)


def obtener_embeddings(chunks: List[str], emb_client: JinaEmbeddings) -> List[List[float]]:
    """Obtiene embeddings para una lista de chunks con el cliente JinaEmbeddings."""
    # embed_documents devuelve una lista de vectores
    return emb_client.embed_documents(chunks)


def procesar_documento(ruta_documento: str):
    """Flujo principal: leer documento, chunkear, embedir y subir a Pinecone."""
    ext = os.path.splitext(ruta_documento)[1].lower()
    if ext == ".pdf":
        texto = leer_pdf(ruta_documento)
    elif ext == ".txt":
        texto = leer_txt(ruta_documento)
    elif ext in (".xls", ".xlsx"):
        texto = leer_excel(ruta_documento)
    else:
        raise ValueError(f"Extensión no soportada: {ext}")

    if not texto.strip():
        raise ValueError("El documento está vacío o no se pudo extraer texto.")

    chunks = chunking_recursivo(texto)
    emb_client = inicializar_embeddings()
    embeddings = obtener_embeddings(chunks, emb_client)
    index = inicializar_pinecone()
    insertar_embeddings_en_pinecone(embeddings, chunks, index)

    print(f"✅ Proceso completado. Chunks: {len(chunks)}. Vectores subidos: {len(embeddings)}")


if __name__ == "__main__":
    # cargar .env (para JINA_API_KEY / PINECONE_API_KEY)
    load_dotenv()

    parser = argparse.ArgumentParser(description="Procesar documento y subir embeddings a Pinecone")
    parser.add_argument("ruta", help="Ruta al archivo (.pdf, .txt, .xls, .xlsx)")
    args = parser.parse_args()

    try:
        procesar_documento(args.ruta)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)
