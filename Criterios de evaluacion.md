# Criterios de evaluación

## Diseño del pipeline LLM y gestión de limitaciones — 55 %

Se evaluará:

- la implementación efectiva de las dos etapas;
- la claridad y calidad de los prompts;
- la separación de responsabilidades entre filtrado y extracción;
- la elección y justificación del proveedor y del modelo;
- la calidad y visibilidad de los resultados;
- la gestión explícita de tokens, rate limits, tiempo, RAM, lotes, pausas y reintentos;
- la justificación del número de filas por lote y del número de llamadas.

## Preprocesamiento y exploración de datos — 20 %

Se evaluará:

- la carga correcta de `videogames_reviews.csv`;
- el análisis de la forma del dataset y de la distribución de valoraciones;
- la identificación y el tratamiento de valores nulos;
- la selección y justificación de una muestra representativa, en particular las 100 reseñas con mayor longitud de contenido.

## Calidad del código y organización — 25 %

Se evaluará:

- el cumplimiento razonable de PEP 8;
- la estructura y legibilidad del código;
- la organización lógica de las celdas;
- los comentarios y explicaciones necesarias;
- la justificación escrita de modelos, prompts y parámetros.
