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

#from langchain_pinecone.vectorstores import Pinecone, PineconeVectorStore


# Función para leer PDF
def leer_pdf(ruta_pdf):
    with open(ruta_pdf, "rb") as file:
        reader = PdfReader(file)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text()
    return texto

# Función para leer TXT
def leer_txt(ruta_txt):
    with open(ruta_txt, "r", encoding="utf-8") as file:
        return file.read()

# Función para leer Excel
def leer_excel(ruta_excel):
    df = pd.read_excel(ruta_excel, engine='openpyxl')
    texto = ""
    for col in df.columns:
        texto += df[col].to_string(index=False) + "\n"
    return texto

# Inicializar embeddings
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

    # Crear una instancia de Pinecone usando tu API Key
    pc = Pinecone(api_key=pinecone_api_key)

    index_name = "tarea-jj-index"  # change if desired

    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    index = pc.Index(index_name)

    return index#, vector_store




# Función para insertar embeddings en Pinecone
def insertar_embeddings_en_pinecone(embeddings, chunks, index):
    # Convertir los embeddings y los textos a un formato adecuado para Pinecone
    vectors = [
        (f"doc_{i}", embeddings[i], {"text": chunk})
        for i, chunk in enumerate(chunks)
    ]
 
    # Insertar los vectores en Pinecone
    index.upsert(vectors)


# Procesar el chunking recursivo
def chunking_recursivo(texto):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return text_splitter.split_text(texto)

# Función para obtener embeddings de los chunks
def obtener_embeddings(chunks, emb):
    return emb.embed_documents(chunks)





# Función principal para procesar el documento
def procesar_documento(ruta_documento):
    # Leer el documento dependiendo de su tipo
    if ruta_documento.endswith(".pdf"):
        texto = leer_pdf(ruta_documento)
    elif ruta_documento.endswith(".txt"):
        texto = leer_txt(ruta_documento)
    elif ruta_documento.endswith(".xlsx"):
        texto = leer_excel(ruta_documento)
    else:
        raise ValueError("Formato de archivo no soportado")

    # Dividir el texto en chunks
    chunks = chunking_recursivo(texto)

    # Inicializar embeddings
    emb = inicializar_embeddings()
    embeddings = obtener_embeddings(chunks, emb)

    # Inicializar Pinecone
    index=inicializar_pinecone()
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)

    # cargar embeddings a pinecone
    # Lista de IDs (pueden ser UUIDs o cualquier string único)
    ids = [str(uuid4()) for _ in range(len(embeddings))]



##### aca 


    # Crear Document por chunk
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

    # Obtener embeddings
    embeddings = obtener_embeddings([doc.page_content for doc in documents], emb)

    # Subir con metadata
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




### hasta aca




    # Metadatos opcionales por vector
#    metadatos = [
#        {"source": "pdf1", "page": 1}
#    ]
#
#    # Construir el payload para insertar
#
#
#
#
#    items = [
#        {
#            "id": ids[i],
#            "values": embeddings[i]
#            #"metadata": metadatos[i]  # O eliminar esta línea si no tienes metadatos
#        }
#        for i in range(len(embeddings))
#    ]
#
    # Subir a Pinecone
    index.upsert(vectors=items)

    print("✅ Embeddings subidos correctamente a Pinecone.")

    #CONFIRMAR QUE SE SUBIERON BIEN
    stats = index.describe_index_stats()
    print(stats)



    
    print(f"🔹 Chunks generados para {ruta_documento}: {len(chunks)}")
    print(f"🔹 Primer chunk: {chunks[0][:200]}...")  # Mostrar solo los primeros 200 caracteres
    print(f"🔹 Embedding del primer chunk (primeros 5 valores): {embeddings[0][:5]}")
    print(f"🔹 Largo de los Embeddings : {len(embeddings[1])}")
    #print(vector_store)




# Ejecutar con un archivo específico
if __name__ == "__main__":
    ruta_documento = "D:\\DESCARGAS\\AI\\tarea2\\Politica_Devoluciones.pdf"  # Cambia esto por el archivo que quieres procesar
    procesar_documento(ruta_documento)













#api_key = os.getenv("JINA_API_KEY")
#if not api_key:
#    raise ValueError("❌ No se encontró la variable de entorno JINA_API_KEY")
#
#emb = JinaEmbeddings(
#    jina_api_key=os.getenv("JINA_API_KEY"),
#    model_name="jina-embeddings-v2-base-es"
#)
#
#
## Texto de ejemplo
#texto_largo = """
#LangChain es una poderosa biblioteca para crear aplicaciones con modelos de lenguaje.
#Permite encadenar LLMs con otras herramientas como búsquedas, bases de datos vectoriales, y más.
#"""
#
## Inicializa el splitter
#text_splitter = RecursiveCharacterTextSplitter(
#    chunk_size=500,
#    chunk_overlap=50,
#    separators=["\n\n", "\n", ".", " ", ""],
#)
#
## Divide el texto
#chunks = text_splitter.split_text(texto_largo)
#
## Obtiene los embeddings
#embeddings = emb.embed_documents(chunks)
#
#print(f"🔹 Chunks generados: {len(chunks)}")
#print(f"🔹 Embedding del primer chunk (primeros 5 valores): {embeddings[0][:5]}")
#





# Embeder una consulta de ejemplo
#emb_q = emb.embed_query("Hola, ¿cómo estás?")
#print(emb_q)

# Embeder documentos
#emb_docs = emb.embed_documents(["Doc 1", "Otro documento"])
#print(emb_docs)


#####################
#####################
#####################
#####################
#####################
#####################
# vamos hacer el chunking recursivo
#####################
#####################
#####################
#####################
#####################


#from langchain.text_splitter import RecursiveCharacterTextSplitter

#Crear el splitter recursivo
#text_splitter = RecursiveCharacterTextSplitter(
#    chunk_size=500,       # Tamaño del chunk
#    chunk_overlap=100,    # Cuánto se solapan los chunks
#)

# Supón que tienes este documento
#raw_text = """
#La inteligencia artificial está transformando la industria. Los modelos de lenguaje, como los de OpenAI o Jina, permiten nuevas formas de interacción con la información. Al vectorizar el texto, podemos realizar búsquedas semánticas eficientes.
#"""

# Generar los chunks
#documents = text_splitter.create_documents([raw_text])
#print(f"Número de chunks generados: {len(documents)}")
#for i, doc in enumerate(documents):
#    print(f"Chunk {i+1}: {doc.page_content}\n")         
