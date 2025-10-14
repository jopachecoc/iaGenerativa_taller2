---
# 🧠 Segundo Taller de IA Generativa
 - jonathan Pacheco
 - Julio Morales
---

## 🚀 Fase 1: Selección de Componentes Clave del Sistema RAG

Antes de codificar, debemos tomar decisiones de **arquitectura**.  
En esta fase, los estudiantes seleccionarán los componentes principales del sistema **RAG (Retrieval-Augmented Generation)**.

---

### 🔹 **1. Modelo de Embeddings**

**Pregunta:**  
¿Qué modelo utilizarían para convertir los documentos de la empresa en vectores numéricos?  
Justifiquen su elección basándose en la precisión, el costo y la capacidad de manejar el idioma español.  
¿Sería un modelo de código abierto como los de Hugging Face o uno propietario?

#### 💬 **Respuesta**

El modelo de embeddings define cinco aspectos fundamentales para este caso de uso:

- 📘 **Capacidad de manejo de texto en español**
- 💰 **Costo de generación de embeddings**
- 🧩 **Calidad semántica (qué tan bien captura el significado)**
- ⚡ **Latencia**
- 🔍 **Velocidad de búsqueda**

**Comparativa de opciones:**

- **Open Source:** LaBSE, Jina Embeddings V2 Base ES, SBERT-Spanish, Smaller LaBSE.
- **Propietarios:** text-embedding-ada-002, embed-v4.0, gemini-embedding-001.

De todos, **Jina Embeddings V2 Base ES** destaca por su balance entre precisión, eficiencia y capacidad en español.  
Basado en una arquitectura **BERT (JinaBERT)**, soporta hasta **8192 tokens**, maneja contextos complejos y ofrece resultados semánticamente precisos en español e inglés.

Además:

- Es **open source**, con bajo costo operativo si se ejecuta localmente.
- Su **latencia** es baja y permite búsquedas rápidas con vectores densos (768 dimensiones).
- Se integra fácilmente con bases vectoriales optimizadas y sistemas SQL.

#### ✅ **Conclusión**

> Se recomienda que **EcoMarket** utilice el modelo **open source `jina-embeddings-v2-base-es`**, ya que ofrece un equilibrio ideal entre precisión, bajo costo y soporte multilingüe (español e inglés).  
> Esto asegura escalabilidad, control local y flexibilidad frente a modelos propietarios.

---

### 🔹 **2. Base de Datos Vectorial**

**Pregunta:**  
¿Dónde almacenarán los vectores para que la búsqueda por similitud sea eficiente?  
Exploren opciones como **Pinecone**, **ChromaDB** o **Weaviate**.  
¿Qué ventajas y desventajas tiene cada una para EcoMarket (escalabilidad, costo, facilidad de uso)?

#### 💬 **Respuesta**

En la arquitectura de **EcoMarket**, la base de datos vectorial almacenará embeddings de productos, políticas, FAQs y pedidos.  
A continuación, un resumen de las opciones:

| Tecnología   | Escalabilidad       | Costo         | Facilidad de uso      | Ideal para           |
| ------------ | ------------------- | ------------- | --------------------- | -------------------- |
| **Pinecone** | ⭐⭐⭐⭐⭐ Muy alta | 💲💲💲💲 Alto | ⭐⭐⭐⭐ Fácil (SaaS) | Escalado masivo      |
| **ChromaDB** | ⭐⭐ Limitada       | 💲 Gratis     | ⭐⭐⭐⭐⭐ Muy fácil  | MVP / validación     |
| **Weaviate** | ⭐⭐⭐⭐ Alta       | 💲💲 Medio    | ⭐⭐⭐ Media          | Escenario productivo |

#### 🔸 Pinecone

- **Ventajas:** Escalabilidad muy alta, baja latencia, integraciones nativas con OpenAI/LangChain.
- **Desventajas:** Alto costo, dependencia del proveedor, sin control interno.

#### 🔸 ChromaDB

- **Ventajas:** Open source, ligero, gratuito y de fácil integración.
- **Desventajas:** Escalabilidad limitada y requiere gestión manual si se instala localmente.

#### 🔸 Weaviate

- **Ventajas:** Open Source + SaaS, escalable, búsqueda híbrida, integración con GraphQL.
- **Desventajas:** Curva de aprendizaje más alta, costos medios, mayor configuración.

#### ✅ **Conclusión**

> Para **MVPs o validaciones**, ChromaDB es la opción más práctica.  
> Sin embargo, para **EcoMarket**, que busca un equilibrio entre **escalabilidad y control**, **Weaviate** representa la mejor alternativa.

---

## 📂 Fase 2: Creación de la Base de Conocimiento de Documentos

### 1️⃣ Identificación de Documentos Clave

Para un sistema de atención al cliente en un e-commerce sostenible, se deben incluir:

#### 📄 Políticas y Términos

- Política de Devoluciones (PDF/DOCX)
- Términos y Condiciones de Compra
- Política de Envíos y Entregas
- Garantías y Reclamos
- Normativas internas

#### 🛒 Comercial y Marketing

- Promociones vigentes (CSV/CRM)
- Política de Cupones
- Boletines y newsletters

#### 🧾 Inventario de Productos (Excel/CSV)

- Nombre, descripción, stock, categorías, precios y SKU.

#### 💬 FAQs (JSON/Markdown/HTML)

- Preguntas frecuentes sobre envíos, pagos, garantías, promociones, etc.

#### 📘 Manuales y Soporte

- Manuales de producto, comparativos, información de contacto y horarios de atención.

---

### 2️⃣ Segmentación (Chunking) de Documentos

Antes de generar los **chunks**, es vital validar la **calidad de los documentos**:

#### ⚠️ Problemas comunes:

- Errores de OCR, texto confuso o redundante.
- Logos o pies de página repetidos.
- Tablas mal estructuradas o lenguaje inconsistente.

#### 📚 Buenas prácticas:

- Mantener estructura coherente.
- Fragmentar por secciones semánticas claras.
- Evitar ruido visual o texto irrelevante.

#### 🔧 Estrategias de Chunking

- **Por tamaño fijo (500 tokens):** simple, pero puede cortar ideas.
- **Por secciones naturales:** mantiene coherencia.
- **Recursiva:** mezcla ambas; recomendada para EcoMarket.

**Ejemplo:**

```text
¿Puedo devolver un jabón líquido?
No, los productos de higiene no son elegibles por razones sanitarias.
```

---

### 3️⃣ Indexación en la Base de Datos Vectorial 🧩

Este proceso convierte los fragmentos (chunks) en **vectores** y los carga en la **base de datos vectorial**.  
La calidad de los documentos y la forma de dividirlos tienen un impacto directo en el rendimiento del sistema RAG.

#### 🔄 Proceso general:

1. **Normalización del texto**

   - Limpieza de HTML, acentos, y stopwords mínimas.
   - Conversión a minúsculas si no afecta la semántica.

2. **Generación de embeddings**

   - Usar `text-embedding-3-small` (rápido y económico).
   - O `text-embedding-3-large` si se requiere mayor precisión semántica.

3. **Estructura de almacenamiento (con metadata):**

   ```json
   {
     "id": "faq_001_chunk1",
     "vector": [0.123, 0.456, ...],
     "metadata": {
       "tipo_documento": "FAQ",
       "categoría": "Devoluciones",
       "fuente": "docs/ecomarket",
       "fecha_actualización": "2025-10-10"
     }
   }
   ```

4. **Carga en la Vector DB (ChromaDB / Pinecone / Weaviate):**
   - Permiten enviar embeddings + metadata.
   - Soportan consultas por similitud y filtros semánticos.

---

## ⚙️ Instalación y Configuración

### 1. Clona el repositorio y entra al directorio del proyecto

```bash
git clone <URL_DEL_REPO>
cd iaGenerativa_taller2
```

### 2. Crea y activa un entorno virtual
```bash
python -m venv .venv
source .venv/Scripts/activate # En Git Bash o WSL
```
# En PowerShell: [Activate.ps1]

### 3. Instala las dependencias
```bash
python -m pip install --upgrade pip
python -m pip install -r [requirements.txt]
```
### 4. Configura las variables de entorno

Debes tener las siguientes variables de entorno configuradas antes de ejecutar los scripts en el archivo .env en la raíz del proyecto:

JINA_API_KEY (obtén tu API key en https://jina.ai/api-dashboard/embedding)
PINECONE_API_KEY (obtén tu API key en https://www.pinecone.io/)

🚦 Ejecución

- A. Procesar e indexar documentos (main2.py)
- B. Consultar el sistema RAG con LangChain (Taller1_Fase3_EcoMarket/rag_ejemplo.py)
- C. Consultar el sistema RAG con LlamaIndex (ragi_llamaindex.py)

 ##### - Coloca los documentos a indexar en una carpeta llamada docs en la raíz del proyecto.
 ##### - Ejecuta:
   
```bash
python [ragi_llamaindex.py] "¿Puedo devolver un cepillo de dientes?"
```
