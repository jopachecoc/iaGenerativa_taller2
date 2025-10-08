


from main2 import *

#cargar los documentos 
#procesar_documento("D:\\DESCARGAS\\AI\\tarea2\\Politica_Devoluciones.pdf")
#procesar_documento("D:\\DESCARGAS\\AI\\tarea2\\Inventario_Productos.xlsx")

#hacer la consulta para que arroje similitud



def procesar_consulta(ruta_documento):
    # Leer el documento dependiendo de su tipo

    texto = ruta_documento

    # Dividir el texto en chunks
    chunks = chunking_recursivo(texto)

    # Inicializar embeddings
    emb = inicializar_embeddings()
    embeddings = obtener_embeddings(chunks, emb)

    # Inicializar Pinecone
    index=inicializar_pinecone()
#    vector_store = PineconeVectorStore(index=index, embedding=embeddings)

    # Paso 5: Realiza la búsqueda en Pinecone
    resultados = index.query(
    vector=embeddings,
    top_k=3,
    include_metadata=True
    )

    # Obtener los textos relevantes
#    textos_recuperados = [
#        match["metadata"].get("page_content", "")
#        for match in resultados["matches"]
#        if "page_content" in match["metadata"]
#    ]

    textos_recuperados = [
        match["metadata"].get("page_content", "") or match["metadata"].get("text", "")
        for match in resultados["matches"]
        if "metadata" in match and (
            "page_content" in match["metadata"] or "text" in match["metadata"]
        )
    ]

#3    # 👇 Mostrar qué trajo
#    print("\n🔍 Textos recuperados:")
#    for i, texto in enumerate(textos_recuperados, 1):
#        print(f"\n--- Chunk #{i} ---")
#        print(texto[:500])  # Muestra los primeros 500 caracteres de cada chunk


    # Concatenar todos en un solo contexto
    contexto = "\n\n".join(textos_recuperados)


    prompt_final = f"""
    Contexto recuperado de documentos:
    {contexto}

    Pregunta del usuario:
    {texto}

    Respuesta basada en el contexto:
    """


    # Paso 6: Mostrar resultados
#    for i, match in enumerate(resultados["matches"], 1):
#        print(f"\n🔹 Resultado #{i}")
#        print(f"Score: {match['score']:.4f}")
#        print(f"ID: {match['id']}")
#        print("🧾 Metadata completa:")
#        print(match.get("metadata", {}))

#    for i, match in enumerate(resultados["matches"], 1):
#        metadata = match.get("metadata", {})
#        texto = metadata.get("page_content") or metadata.get("text", "[Texto no encontrado]")
#    
#        print(f"\n🔹 Resultado #{i}")
#        print(f"Score: {match['score']:.4f}")
#        print(f"Texto:\n{texto[:500]}...")



#    for i, match in enumerate(resultados["matches"], 1):
#        print(f"\n📌 Resultado #{i}")
#        print(f"🔹 ID: {match['id']}")
#        print(f"🔹 Score: {match['score']:.4f}")
#        print(f"🔹 Metadata: {match.get('metadata')}")



    #CONFIRMAR QUE SE SUBIERON BIEN
#    stats = index.describe_index_stats()
#    print(stats)



    ## hasta acá
    ###
    ##
    #
   
    print(f"🔹 Chunks generados para {ruta_documento}: {len(chunks)}")
    print(f"🔹 Primer chunk: {chunks[0][:200]}...")  # Mostrar solo los primeros 200 caracteres
    print(f"🔹 Embedding del primer chunk (primeros 5 valores): {embeddings[0][:5]}")
    print(f"🔹 Largo de los Embeddings : {len(embeddings[0])}")
    print(contexto[0:102])
    #print(f"🔹 Largo de los Embeddings : {len(resultados[0])}")
    #print(vector_store)

if __name__ == "__main__":
    cosulta = "¿Cuál es la política de devoluciones?"  # Cambia esto por el archivo que quieres procesar
    procesar_consulta(cosulta)


