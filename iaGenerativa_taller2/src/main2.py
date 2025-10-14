# filepath: iaGenerativa_taller2/src/main2.py

import os
import pandas as pd
import PyPDF2
import pinecone

from langchain_community.embeddings import JinaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from uuid import uuid4
from langchain_core.documents import Document

def leer_pdf(ruta_pdf):
    with open(ruta_pdf, "rb") as file:
        reader = PdfReader(file)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text()
    return texto

def leer_txt(ruta_txt):
    with open(ruta_txt, "r", encoding="utf-8") as file:
        return file.read()

def leer_excel(ruta_excel):
    df = pd.read_excel(ruta_excel, engine='openpyxl')
    texto = ""
    for col in df.columns:
        texto += df[col].to_string(index=False) + "\n"
    return texto

def inicializar_embeddings():
    api_key = os.getenv("JINA_API_KEY")
    if not api_key:
        raise ValueError("❌ No se encontró la variable de entorno JINA_API_KEY")
    
    return JinaEmbeddings(
        jina_api_key=api_key,
        model_name="jina-embeddings-v2-base-es"
    )

def inicializar_pinecone():
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        raise ValueError("❌ No se encontró la variable de entorno PINECONE_API_KEY")

    pc = Pinecone(api_key=pinecone_api_key)

    index_name = "tarea-jj-index"

    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    index = pc.Index(index_name)

    return index

def insertar_embeddings_en_pinecone(embeddings, chunks, index):
    vectors = [
        (f"doc_{i}", embeddings[i], {"text": chunk})
        for i, chunk in enumerate(chunks)
    ]
    index.upsert(vectors)

def chunking_recursivo(texto):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return text_splitter.split_text(texto)

def obtener_embeddings(chunks, emb):
    return emb.embed_documents(chunks)

def procesar_documento(ruta_documento):
    if ruta_documento.endswith(".pdf"):
        texto = leer_pdf(ruta_documento)
    elif ruta_documento.endswith(".txt"):
        texto = leer_txt(ruta_documento)
    elif ruta_documento.endswith(".xlsx"):
        texto = leer_excel(ruta_documento)
    else:
        raise ValueError("Formato de archivo no soportado")

    chunks = chunking_recursivo(texto)

    emb = inicializar_embeddings()
    embeddings = obtener_embeddings(chunks, emb)

    index = inicializar_pinecone()
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)

    ids = [str(uuid4()) for _ in range(len(embeddings))]

    documents = [
        Document(
            page_content=chunk,
            metadata={
                "source": os.path.basename(ruta_documento),
                "chunk_index": i
            }
        )
        for i, chunk in enumerate(chunks)
    ]

    embeddings = obtener_embeddings([doc.page_content for doc in documents], emb)

    items = [
        {
            "id": str(uuid4()),
            "values": embeddings[i],
            "metadata": {
                **documents[i].metadata,
                "page_content": documents[i].page_content
            }
        }
        for i in range(len(documents))
    ]

    index.upsert(vectors=items)

    print("✅ Embeddings subidos correctamente a Pinecone.")

    stats = index.describe_index_stats()
    print(stats)

    print(f"🔹 Chunks generados para {ruta_documento}: {len(chunks)}")
    print(f"🔹 Primer chunk: {chunks[0][:200]}...")
    print(f"🔹 Embedding del primer chunk (primeros 5 valores): {embeddings[0][:5]}")
    print(f"🔹 Largo de los Embeddings : {len(embeddings[1])}")

if __name__ == "__main__":
    ruta_documento = "D:\\DESCARGAS\\AI\\tarea2\\Politica_Devoluciones.pdf"
    procesar_documento(ruta_documento)