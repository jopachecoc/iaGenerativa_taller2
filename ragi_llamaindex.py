import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain_community.embeddings import JinaEmbeddings
from llama_index.vector_stores.pinecone import PineconeVectorStore
import pinecone

def construir_llamaindex():
    # Configura embeddings de Jina vía LangChain
    jina_api_key = os.getenv("JINA_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not jina_api_key or not pinecone_api_key:
        raise ValueError("Faltan variables de entorno JINA_API_KEY o PINECONE_API_KEY")

    # Inicializa Pinecone
    pinecone.init(api_key=pinecone_api_key, environment="us-east-1-aws")
    index_name = "tarea-jj-index"
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=768, metric="cosine")
    pinecone_index = pinecone.Index(index_name)

    # Embeddings de Jina vía LangChain
    langchain_embedding = LangchainEmbedding(
        JinaEmbeddings(jina_api_key=jina_api_key, model_name="jina-embeddings-v2-base-es")
    )

    # Configura el vector store de LlamaIndex para Pinecone
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    # Service context para LlamaIndex
    service_context = ServiceContext.from_defaults(embed_model=langchain_embedding)

    # Carga documentos desde una carpeta (puedes cambiar la ruta)
    docs = SimpleDirectoryReader("docs").load_data()

    # Construye el índice
    index = VectorStoreIndex.from_documents(
        docs,
        service_context=service_context,
        vector_store=vector_store
    )
    return index

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python ragi_llamaindex.py 'Tu pregunta sobre EcoMarket'")
        exit(1)
    pregunta = sys.argv[1]
    index = construir_llamaindex()
    query_engine = index.as_query_engine(similarity_top_k=3)
    respuesta = query_engine.query(pregunta)
    print("Respuesta:", respuesta.response)
    print("Fuentes:")
    for node in respuesta.source_nodes:
        print("-", node.node.get_content()[:100], "...")