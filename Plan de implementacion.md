# Pipeline LLM para reseñas de videojuegos - Implementation Plan

**Objetivo:** construir un pipeline reproducible de dos etapas que filtre reseñas poco informativas y extraiga información estructurada mediante la API oficial de DeepSeek.

**Arquitectura:** el notebook presenta y orquesta el ejercicio, mientras que los módulos de `src/videogame_reviews` concentran la lógica reutilizable. Las respuestas se validan con Pydantic y cada lote aceptado se persiste en checkpoints para permitir reanudaciones sin repetir llamadas.

**Tech Stack:** Python 3.11+, pandas, Pydantic, OpenAI SDK, DeepSeek API, pytest, Jupyter/nbclient y Git.

---

## 1. Decisiones cerradas

- Filtrado: `deepseek-v4-flash`, lotes de 5 y máximo de 2.000 tokens de salida.
- Extracción: `deepseek-v4-pro`, lotes de 3 y máximo de 4.000 tokens de salida.
- Endpoint: `https://api.deepseek.com` mediante el SDK compatible con OpenAI.
- Credencial: exclusivamente `DEEPSEEK_API_KEY` desde el entorno.
- Formato: JSON Output, temperatura 0 y razonamiento desactivado.
- Ejecución secuencial, sin concurrencia.
- Reintentos: hasta 5 intentos con backoff de 2, 4, 8 y 16 segundos, limitado a 30.
- Muestra: las 100 reseñas con mayor longitud tras eliminar contenidos nulos.
- Duplicados: se conservan en los resultados, pero se consultan una sola vez por SHA-256.
- Tokens estimados: `ceil(caracteres_del_prompt/4)`.
- Entrega: notebook, código modular, pruebas, CSV finales, métricas y documentación.

## 2. Estructura del proyecto

```text
.
├── Ejercicio 2.ipynb
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── videogames_reviews.csv
├── analisis_videojuegos_resultados.csv
├── src/videogame_reviews/
│   ├── config.py
│   ├── schemas.py
│   ├── data.py
│   ├── prompts.py
│   ├── deepseek_client.py
│   ├── persistence.py
│   ├── stages.py
│   ├── relevance.py
│   ├── extraction.py
│   ├── evaluation.py
│   └── pipeline.py
├── tests/
└── outputs/
    ├── sample_top_100.csv
    ├── relevance_results.csv
    ├── relevant_reviews.csv
    ├── structured_reviews.csv
    └── run_metrics.json
```

## 3. Contratos de salida

### Filtrado

```json
{
  "content_hash": "sha256",
  "relevante": true,
  "motivo": "informativa",
  "justificacion_breve": "Describe jugabilidad y problemas técnicos."
}
```

`motivo` admite `informativa`, `texto_vacio`, `spam`, `incoherente` y `sin_informacion_evaluable`.

### Extracción

```json
{
  "content_hash": "sha256",
  "sentimiento_general": "positivo",
  "aspectos_positivos": ["historia"],
  "aspectos_negativos": ["bugs"],
  "dificultad": "equilibrada",
  "problemas_tecnicos": ["crashes"],
  "relacion_calidad_precio": "media",
  "recomendacion_modelo": "condicional",
  "resumen": "Buena experiencia condicionada por errores técnicos."
}
```

Las listas ausentes usan `[]`; los escalares no mencionados usan `no_mencionada` o `no_determinable`.

## 4. Work orders

### WO-01 - Repositorio y dependencias

**Archivos:** `.gitignore`, `requirements.txt`, `requirements-dev.txt`, `pytest.ini`.

- [ ] Inicializar Git y crear una rama de trabajo.
- [ ] Excluir `.env`, entornos virtuales, cachés, checkpoints y notebooks temporales.
- [ ] Declarar pandas, Pydantic y OpenAI SDK como dependencias de ejecución.
- [ ] Declarar pytest, pytest-cov, Jupyter y nbclient como dependencias de desarrollo.
- [ ] Instalar dependencias y ejecutar `python -m pytest --collect-only`.
- [ ] Crear el commit `chore: initialize project structure and dependencies`.

**Aceptación:** entorno instalable y ningún secreto versionado.

### WO-02 - Configuración y esquemas

**Archivos:** `src/videogame_reviews/config.py`, `schemas.py`, `tests/test_config.py`, `tests/test_schemas.py`.

- [ ] Escribir pruebas que rechacen una clave ausente, lotes inválidos, enums desconocidos y hashes duplicados.
- [ ] Confirmar que las pruebas fallan por ausencia de los contratos.
- [ ] Implementar `PipelineConfig` con los valores cerrados en la sección 1.
- [ ] Implementar modelos Pydantic estrictos para relevancia, extracción, uso y ejecución.
- [ ] Ejecutar las pruebas específicas y la suite completa.
- [ ] Crear el commit `feat: add configuration and validated schemas`.

**Aceptación:** ninguna respuesta incompatible puede incorporarse a los DataFrames.

### WO-03 - Carga, exploración y muestra

**Archivos:** `src/videogame_reviews/data.py`, `tests/test_data.py`.

- [ ] Probar columnas ausentes, nulos, empates de longitud, identificador ausente y duplicados.
- [ ] Cargar `videogames_reviews.csv` y renombrar `Unnamed: 0` como `source_row_id`.
- [ ] Registrar forma, tipos, nulos y distribución de `Valoración`.
- [ ] Eliminar contenidos nulos y calcular `longitud_caracteres`.
- [ ] Normalizar el contenido y calcular `content_hash` SHA-256.
- [ ] Seleccionar el top 100 con desempate determinista y añadir `sample_rank`.
- [ ] Crear una vista única para la API y exportar `sample_top_100.csv`.
- [ ] Verificar 20.000 filas, 288 nulos, 100 seleccionadas y 80 contenidos únicos.
- [ ] Crear el commit `feat: add deterministic review preprocessing`.

### WO-04 - Prompts versionados

**Archivos:** `src/videogame_reviews/prompts.py`, `tests/test_prompts.py`.

- [ ] Probar que ambos prompts contienen `json`, el esquema y los hashes.
- [ ] Diseñar el prompt de relevancia con criterios positivos y negativos.
- [ ] Diseñar el prompt de extracción limitado a evidencia explícita.
- [ ] Añadir versiones `filter-v1.0` y `extraction-v1.0`.
- [ ] Delimitar las reseñas y exigir correspondencia exacta de hashes.
- [ ] Crear el commit `feat: define versioned LLM prompts`.

### WO-05 - Cliente DeepSeek resiliente

**Archivos:** `src/videogame_reviews/deepseek_client.py`, `tests/test_deepseek_client.py`.

- [ ] Probar respuesta válida, contenido vacío, JSON inválido, 429, timeout y error 401.
- [ ] Inyectar el transporte para que las pruebas no consuman la API.
- [ ] Configurar OpenAI SDK con `base_url=https://api.deepseek.com`.
- [ ] Enviar JSON Output, temperatura 0, `stream=False` y `thinking=disabled`.
- [ ] Reintentar únicamente fallos transitorios y acumular tokens/reintentos.
- [ ] No registrar claves ni reseñas completas.
- [ ] Crear el commit `feat: add resilient DeepSeek client`.

### WO-06 - Checkpoints y motor de lotes

**Archivos:** `src/videogame_reviews/persistence.py`, `stages.py`, `tests/test_persistence.py`.

- [ ] Probar escritura atómica, reanudación, corrupción e incompatibilidad de versión/modelo.
- [ ] Crear JSONL con cabecera de metadatos y un registro por hash.
- [ ] Omitir hashes ya procesados.
- [ ] Validar que cada respuesta devuelve exactamente los hashes solicitados.
- [ ] Dividir un lote fallido hasta llegar a una fila individual.
- [ ] Conservar el resto de resultados cuando una fila sea irrecuperable.
- [ ] Crear el commit `feat: add atomic resumable checkpoints`.

### WO-07 - Filtrado semántico

**Archivos:** `src/videogame_reviews/relevance.py`, `tests/test_stages.py`.

- [ ] Probar lotes completos, duplicados, reanudación, hashes inesperados y cero relevantes.
- [ ] Procesar contenidos únicos en lotes de 5 con `deepseek-v4-flash`.
- [ ] Reconstruir las 100 filas originales tras consultar los hashes únicos.
- [ ] Exportar `relevance_results.csv` y `relevant_reviews.csv`.
- [ ] Mostrar recuentos y motivos de descarte.
- [ ] Crear el commit `feat: implement relevance filtering`.

### WO-08 - Extracción estructurada

**Archivos:** `src/videogame_reviews/extraction.py`, `tests/test_stages.py`.

- [ ] Probar listas vacías, valores no mencionados, JSON truncado y entrada no relevante.
- [ ] Procesar únicamente relevantes en lotes de 3 con `deepseek-v4-pro`.
- [ ] Validar ocho atributos estructurados.
- [ ] Reconstruir duplicados y serializar listas como JSON dentro del CSV.
- [ ] Exportar `structured_reviews.csv`.
- [ ] Crear el commit `feat: implement structured extraction`.

### WO-09 - Orquestación y métricas

**Archivos:** `src/videogame_reviews/pipeline.py`, `evaluation.py`, `tests/test_pipeline.py`, `tests/test_evaluation.py`.

- [ ] Probar `preprocess`, `filter`, `extract` y `all` con cliente simulado.
- [ ] Probar que `preprocess` nunca sobrescribe `run_metrics.json`.
- [ ] Implementar `run_pipeline()` como punto único de orquestación.
- [ ] Guardar preprocesamiento aislado en `preprocess_metrics.json`.
- [ ] Calcular llamadas y tokens estimados sobre prompts reales y hashes únicos.
- [ ] Registrar modelos, versiones, filas, llamadas, reintentos, tokens y duración.
- [ ] Generar auditoría determinista con semilla 26.
- [ ] Crear el commit `feat: orchestrate pipeline and preserve metrics`.

**Valores esperados para los datos actuales:** 43 llamadas mínimas, 280.184 tokens de entrada estimados, 99 filas relevantes y 99 filas estructuradas.

### WO-10 - Notebook entregable

**Archivo:** `Ejercicio 2.ipynb`.

- [ ] Organizar carga, EDA, preprocesamiento, filtrado, extracción, métricas y conclusiones.
- [ ] Mostrar los prompts completos y sus versiones.
- [ ] Justificar modelos, lotes, tokens, coste, pausas, reintentos y checkpoints.
- [ ] Añadir `RUN_API=False` como modo seguro que reutiliza resultados.
- [ ] Mostrar los CSV reales de ambas etapas y la auditoría cualitativa.
- [ ] Ejecutar con `jupyter nbconvert --execute` y confirmar que no cambia `run_metrics.json`.
- [ ] Crear el commit `docs: complete executable project notebook`.

### WO-11 - Documentación y seguridad

**Archivos:** `README.md`, `tests/test_security.py`.

- [ ] Documentar instalación, credencial, ejecución y reanudación.
- [ ] Explicar Flash frente a Pro, lotes 5/3 y razonamiento desactivado.
- [ ] Documentar 43 llamadas mínimas y el método de estimación de tokens.
- [ ] Explicar la fórmula de coste y exigir consultar las tarifas vigentes.
- [ ] Añadir trazabilidad entre requisitos y secciones del notebook.
- [ ] Ejecutar la prueba de secretos y `git grep`.
- [ ] Crear el commit `docs: add setup and Prompt Engineering rationale`.

### WO-12 - Verificación y publicación

- [ ] Ejecutar `python -m pytest --cov=src/videogame_reviews --cov-report=term-missing`.
- [ ] Ejecutar `python -m compileall -q src`.
- [ ] Ejecutar el notebook completo con nbconvert.
- [ ] Validar 100 filtradas, 99 relevantes, 99 estructuradas y 8 atributos.
- [ ] Confirmar que `run_metrics.json` conserva métricas y estimaciones.
- [ ] Confirmar que Git está limpio y no contiene secretos.
- [ ] Fusionar en `main`, etiquetar la entrega y publicar en GitHub.

**Aceptación final:** 32 pruebas superadas, cobertura mínima del 90 %, notebook ejecutable, resultados reales presentes y repositorio sin credenciales.

## 5. Matriz de trazabilidad

| Requisito | Work orders |
|---|---|
| Exploración y nulos | WO-03, WO-10 |
| Top 100 e identificador estable | WO-03 |
| Filtrado con primer LLM | WO-04, WO-05, WO-07 |
| Extracción con segundo LLM | WO-04, WO-05, WO-08 |
| Batching, tokens y rate limits | WO-05, WO-06, WO-09, WO-11 |
| Credenciales seguras | WO-01, WO-02, WO-11 |
| Código estructurado y PEP 8 | WO-02 a WO-09 |
| Notebook y resultados visibles | WO-10 |
| Recuperación ante interrupciones | WO-06, WO-09 |
| Entrega y verificación | WO-11, WO-12 |
