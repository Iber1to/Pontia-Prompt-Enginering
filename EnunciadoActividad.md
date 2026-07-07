Análisis de reseñas de videojuegos
Pasos
Requisitos
Evaluación
Recursos descargables
Necesitas descargar los siguientes recursos para realizar el ejercicio:

¿Qué hay que hacer?
Diseña un pipeline de dos pasos con LLMs para analizar reseñas de videojuegos: un primer modelo que filtre las reseñas con contenido poco informativo y un segundo modelo que extraiga información estructurada de las ya filtradas. Puedes usar un proveedor comercial por API (Gemini, OpenAI, Groq...) o un modelo local vía HuggingFace, justificando la elección y cómo gestionas sus limitaciones (tokens por llamada, rate limits, tamaño de los lotes).

Pasos a seguir
En este ejercicio trabajarás con un dataframe que contiene información sobre reseñas de videojuegos. Cada fila del dataframe contiene la información de una reseña.

Columnas del dataset:

Contenido: texto de la reseña
Valoración: Recomendado o No recomendado
Recomendado_binario: 1 si la valoración es Recomendado, 0 si es No recomendado
Objetivo: aplicar técnicas de Prompt Engineering para extraer información estructurada de las reseñas mediante un pipeline de dos pasos con LLMs, en vez de un único análisis directo — dividir tareas complejas en subtareas simples y controlables es justo lo que se evalúa en este ejercicio.

Tareas a realizar:

Carga y exploración de datos:
Cargar el archivo videogames_reviews.csv.
Realizar un análisis exploratorio básico: forma del dataframe, valores nulos y cómo se gestionan, distribución de la columna Valoración.
Preprocesamiento:
Limpiar los datos eliminando filas con contenido nulo.
Seleccionar una muestra representativa de comentarios para el análisis (por ejemplo, los 100 comentarios con más texto).
Paso 1 del pipeline — filtrado con un primer LLM:
Diseñar un prompt que clasifique cada reseña como relevante o no relevante (descartando spam, texto vacío o sin contenido evaluable).
Justificar el proveedor/modelo elegido —API comercial (Gemini, OpenAI, Groq...) o modelo local vía Hugging Face—, el tamaño de los lotes (nº de reseñas por llamada) y cómo se respetan sus límites (rate limits si es API, tiempo/RAM si es local).
El resultado debe ser un dataframe reducido, sin las reseñas irrelevantes.
Paso 2 del pipeline — extracción estructurada con un segundo LLM:
Sobre el dataframe ya filtrado, extraer al menos 3 campos estructurados por reseña (por ejemplo: sentimiento general, aspectos positivos, aspectos negativos, dificultad, recomendación, valor por dinero...). El esquema exacto es libre.
Justificar de nuevo el modelo elegido (el mismo del paso 1 u otro distinto) y la estrategia de llamadas: tamaño de batch, tiempo entre llamadas (time.sleep() u otro mecanismo) y qué ocurre si se alcanza un límite de uso antes de terminar.
Entregables:

Notebook con el código implementado, bien organizado en celdas (carga, exploración, preprocesado, paso 1, paso 2).
Análisis exploratorio básico de los datos.
Pipeline de dos pasos con LLMs: filtrado de reseñas irrelevantes y extracción de información estructurada, con la justificación escrita de los modelos, prompts y parámetros elegidos.
Requisitos
Diseñar un pipeline de dos pasos con LLMs: un primer modelo que filtre las reseñas irrelevantes y un segundo modelo (puede ser el mismo, justificando por qué) que extraiga información estructurada.
Conectar con el proveedor de tu elección —API comercial (Google Gemini, OpenAI, Groq...) o modelo local vía Hugging Face— utilizando variables de entorno para la API key (si aplica).
Cargar el archivo videogames_reviews.csv que contiene reseñas de videojuegos con las siguientes columnas:
Contenido: texto de la reseña
Valoración: Recomendado o No recomendado
Recomendado_binario: 1 si la valoración es Recomendado, 0 si la valoración es No recomendado
Realizar un análisis exploratorio básico del dataset.
Preprocesar los datos eliminando filas con contenido nulo y seleccionar una muestra representativa para el análisis (por ejemplo, los comentarios más largos).
Filtrar las reseñas irrelevantes con un primer LLM, justificando el modelo, el tamaño de los lotes y cómo se gestionan los límites del proveedor o el hardware (rate limits, tokens por llamada, tiempo/RAM).
Extraer información estructurada (al menos 3 campos) de las reseñas ya filtradas con un segundo LLM, justificando de nuevo el modelo y la estrategia de llamadas.
Organizar el notebook con celdas ordenadas y código bien estructurado.
Cómo se evalúa
Tu solución se calificará según estos criterios:

Diseño del pipeline LLM y gestión de limitaciones
55%
Debe implementarse un pipeline de dos pasos con LLMs: un primer modelo que filtre las reseñas irrelevantes y un segundo modelo (puede ser el mismo, justificando por qué) que extraiga información estructurada de las reseñas ya filtradas. El proveedor es libre - API comercial (Google Gemini, OpenAI, Groq...) o modelo local vía Hugging Face- siempre justificando la elección. Debe demostrarse el análisis con resultados visibles y gestionarse explícitamente las limitaciones del proveedor o hardware elegido: tokens máximos por llamada, rate limits (o tiempo/RAM si es local) y tamaño de los lotes de reseñas por llamada.

Preprocesamiento y exploración de datos
20%
Debe cargarse correctamente el archivo videogames_reviews.csv. Debe realizarse un análisis exploratorio básico que muestre información sobre el dataset (forma, distribución de valoraciones). Los datos deben preprocesarse adecuadamente: identificación y tratamiento de valores nulos, y selección de una muestra representativa para el análisis (por ejemplo, las reseñas con más texto).

Calidad del código y organización
25%
El código debe cumplir con PEP 8 y estar bien estructurado. El notebook debe estar organizado con celdas ordenadas que separen claramente la carga de datos, el análisis exploratorio, el preprocesamiento y los dos pasos del pipeline con LLMs (filtrado y extracción). Debe incluir comentarios explicativos donde sea necesario y una justificación escrita de los modelos, prompts y parámetros elegidos (tamaño de batch, tiempo entre llamadas, etc.).

Tecnologías a utilizar
Python
Python