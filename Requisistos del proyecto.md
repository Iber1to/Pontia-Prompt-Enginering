# Proyecto final: análisis de reseñas de videojuegos con LLMs

## 1. Contexto y peso en la evaluación

Este proyecto corresponde al **Ejercicio 2, entregable final del módulo de Prompt Engineering**. Su entrega es obligatoria y representa el **70 % de la nota final del módulo**. El cuestionario final, también obligatorio, representa el 30 % restante.

El foco del proyecto no está únicamente en el resultado obtenido, sino especialmente en el razonamiento, el diseño de prompts y las decisiones técnicas que permiten construir un proceso reproducible y controlable.

## 2. Objetivo

Diseñar e implementar un **pipeline de dos pasos con Large Language Models (LLMs)** para transformar reseñas de videojuegos en información estructurada:

1. **Filtrado de relevancia:** clasificar las reseñas y eliminar aquellas con contenido poco informativo o no evaluable.
2. **Extracción estructurada:** analizar las reseñas relevantes y extraer de cada una al menos tres entidades o atributos útiles.

La división en dos etapas es un requisito central del ejercicio. Se busca demostrar que una tarea compleja puede separarse en subtareas más simples, observables y controlables.

## 3. Datos y recursos disponibles

### 3.1. Dataset principal

Se utilizará el archivo `videogames_reviews.csv`. Cada fila representa una reseña de un videojuego y contiene estas columnas:

- `Contenido`: texto libre de la reseña.
- `Valoración`: `Recomendado` o `No recomendado`.
- `Recomendado_binario`: 1 si la valoración es `Recomendado` y 0 si es `No recomendado`.

El dataset es deliberadamente crudo, por lo que requiere exploración, limpieza y selección previa de datos.

### 3.2. Recurso de referencia

El archivo `analisis_videojuegos_resultados.csv` muestra un posible resultado final. Puede utilizarse como inspiración, pero su esquema no es obligatorio: se permite elegir otras entidades y otro formato siempre que se cumplan los requisitos de estructura y justificación.

## 4. Desarrollo del proyecto

### 4.1. Carga y exploración inicial

1. Cargar `videogames_reviews.csv` en un DataFrame.
2. Realizar un análisis exploratorio básico que incluya, como mínimo:
   - forma y dimensiones del DataFrame;
   - identificación de valores nulos;
   - explicación de cómo se gestionan los valores nulos;
   - distribución de la columna `Valoración`.

### 4.2. Preprocesamiento y selección de la muestra

1. Eliminar las filas cuyo campo `Contenido` sea nulo.
2. Calcular o considerar la longitud del texto de cada reseña.
3. Seleccionar como muestra inicial **las 100 reseñas con mayor longitud de contenido**. Si el notebook proporcionado ya contiene esta selección, deberá revisarse, explicarse y utilizarse como punto de partida.
4. Conservar un identificador estable para poder relacionar cada resultado con su reseña original.

La selección por longitud garantiza suficiente información potencial, pero **no sustituye** el filtrado semántico del primer LLM.

### 4.3. Paso 1 del pipeline: filtrado de contenido relevante

Diseñar un prompt para que un primer LLM clasifique cada reseña como **relevante** o **no relevante**.

Una reseña será relevante cuando aporte información evaluable y permita obtener opiniones, aspectos positivos o negativos u otros insights útiles. Se deberán descartar, entre otros casos:

- texto vacío o sin contenido semántico;
- spam;
- contenido incoherente;
- comentarios que no aporten información suficiente sobre el videojuego.

El resultado será un **nuevo DataFrame reducido** que contenga únicamente las reseñas relevantes. La clasificación producida por el modelo debe tener un formato consistente y procesable automáticamente.

Para esta etapa se deberá documentar y justificar:

- el proveedor y modelo elegidos;
- el prompt completo y sus decisiones de diseño;
- el número de reseñas enviado por lote;
- la estrategia de batching y tokenización;
- los tokens máximos estimados o permitidos por llamada;
- los límites de uso y su tratamiento: rate limits para una API o tiempo y memoria RAM para un modelo local;
- el mecanismo de espera, reintentos y recuperación ante errores;
- qué sucede si se alcanza un límite de uso antes de completar el proceso;
- el número total o estimado de llamadas.

### 4.4. Paso 2 del pipeline: extracción de información estructurada

Aplicar un segundo rol o paso LLM exclusivamente sobre el DataFrame filtrado. Su objetivo será extraer información estructurada de cada reseña.

El esquema es libre, pero debe incluir **al menos tres entidades o atributos relevantes**. Por ejemplo:

- sentimiento general;
- aspectos positivos;
- aspectos negativos;
- dificultad;
- recomendación;
- relación calidad-precio.

Un posible esquema orientativo es:

```json
{
  "Id": "<identificador de la reseña>",
  "SentimientoGeneral": "Positivo | Negativo | Neutral",
  "AspectosPositivos": ["aspecto 1", "aspecto 2"],
  "AspectosNegativos": ["aspecto 1", "aspecto 2"],
  "Dificultad": "Demasiado fácil | Fácil | Equilibrado | Difícil | Demasiado difícil | No mencionado",
  "Recomendado": "<valor correspondiente>"
}
```

La salida debe ser válida, consistente, procesable y convertible a un DataFrame. No deben inventarse atributos que no aparezcan en la reseña; cuando un dato no esté presente, deberá utilizarse un valor explícito y uniforme, como `No mencionado`, `null` o una lista vacía.

Para esta segunda etapa también se deberán justificar el modelo, el prompt, el tamaño de lote, los tokens por llamada, las pausas entre llamadas, los reintentos, los límites del proveedor o del hardware y el número de llamadas.

Los dos pasos deben desempeñar **funciones claramente separadas**. Puede utilizarse el mismo modelo subyacente en ambas etapas si se justifica la decisión; en tal caso, deberán mantenerse prompts, entradas, salidas y responsabilidades diferenciados.

## 5. Elección tecnológica y gestión de credenciales

El proyecto se desarrollará en **Python**. Puede utilizarse:

- una API comercial, como Google Gemini, OpenAI o Groq; o
- un modelo local mediante Hugging Face.

La elección del proveedor y del modelo debe justificarse en función de la tarea, la calidad esperada, el contexto disponible, el coste y las limitaciones operativas.

Si se utiliza una API, la clave deberá cargarse mediante una **variable de entorno**. No se incluirán claves, tokens ni otros secretos directamente en el notebook, en los archivos de salida ni en un repositorio.

## 6. Requisitos de implementación y calidad

- El notebook debe ser completo y ejecutable de principio a fin.
- El código debe cumplir razonablemente con PEP 8 y estar bien estructurado.
- Las celdas deben separar con claridad:
  1. configuración e importaciones;
  2. carga de datos;
  3. exploración;
  4. preprocesamiento y selección de muestra;
  5. paso 1: filtrado;
  6. paso 2: extracción;
  7. validación, presentación y exportación de resultados.
- Deben incluirse comentarios cuando aporten contexto y explicaciones escritas de las decisiones importantes.
- Los prompts, modelos y parámetros utilizados deben quedar visibles y justificados.
- Deben mostrarse resultados reales de ambas etapas del pipeline.
- El proceso debe contemplar respuestas inválidas, errores de conexión y ejecuciones incompletas, evitando perder resultados ya procesados.

## 7. Entregables

La entrega deberá incluir:

1. Un notebook completo, ordenado y ejecutable.
2. El análisis exploratorio básico del dataset.
3. El pipeline de dos pasos implementado:
   - DataFrame reducido tras el filtrado de relevancia;
   - resultado final con la información estructurada.
4. Explicaciones claras de cada fase.
5. Justificación de los prompts, modelos, tamaños de lote, parámetros y mecanismos de gestión de límites.
6. El resultado final estructurado, mostrado en el notebook y, opcionalmente, exportado a CSV.

La entrega puede realizarse mediante los archivos solicitados o mediante un repositorio de GitHub al que se conceda acceso al docente, según el canal indicado para el módulo. En caso de usar un repositorio, no deberá contener credenciales ni secretos.
