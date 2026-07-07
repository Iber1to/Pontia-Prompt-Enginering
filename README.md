# Análisis de reseñas de videojuegos con DeepSeek

Proyecto final de Prompt Engineering: pipeline reproducible de dos etapas para filtrar reseñas poco informativas y extraer información estructurada de las relevantes.

## Arquitectura

El notebook `Ejercicio 2.ipynb` explica y orquesta el trabajo. La lógica probada se encuentra en `src/videogame_reviews`:

1. carga, exploración y selección determinista de las 100 reseñas más largas;
2. filtrado con `deepseek-v4-flash`, lotes de 5;
3. extracción con `deepseek-v4-pro`, lotes de 3;
4. validación Pydantic, checkpoints y reconstrucción de duplicados;
5. exportación de resultados y métricas.

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
$env:PYTHONPATH = "src"
```

## Credencial

La API key nunca se escribe en el proyecto:

```powershell
$env:DEEPSEEK_API_KEY = Read-Host "DeepSeek API key"
```

La variable solo es necesaria al ejecutar las etapas LLM. No se imprime ni se guarda.

## Ejecución

En el notebook, cambiar `RUN_API = False` a `True` para realizar las llamadas reales. También puede ejecutarse por código:

```python
from videogame_reviews import PipelineConfig, run_pipeline

result = run_pipeline(PipelineConfig(), stage="all")
```

Etapas aceptadas: `preprocess`, `filter`, `extract` y `all`. Si una ejecución se interrumpe, repetirla reutiliza los checkpoints compatibles de `outputs/checkpoints`.

## Resultados

- `sample_top_100.csv`: muestra exigida.
- `relevance_results.csv`: decisión para las 100 filas.
- `relevant_reviews.csv`: DataFrame reducido.
- `structured_reviews.csv`: ocho atributos extraídos.
- `run_metrics.json`: cobertura, llamadas, reintentos y tokens.

Los CSV generados y checkpoints están excluidos de Git para evitar entregar resultados incompletos por accidente. Deben adjuntarse explícitamente junto al notebook cuando proceda.

## Pruebas

```powershell
python -m pytest -v
python -m pytest --cov=src/videogame_reviews --cov-report=term-missing
```

Las pruebas usan clientes simulados y nunca consumen la API.

## Trazabilidad

| Requisito | Implementación / notebook |
|---|---|
| Exploración, nulos y distribución | Secciones 3–5; `data.py` |
| Top 100 por longitud | Sección 5; `prepare_sample` |
| Filtrado LLM | Secciones 7–8; `relevance.py` |
| Extracción estructurada | Secciones 9–10; `extraction.py` |
| Tokens, lotes y límites | Secciones 6 y 11; `deepseek_client.py` |
| Recuperación y resultados | Secciones 11–12; `persistence.py` y `pipeline.py` |
| Validación cualitativa | Sección 13; `evaluation.py` |

## Limitaciones

La muestra por longitud favorece reseñas extensas y no representa necesariamente todo el dataset. No existe ground truth para relevancia o atributos, por lo que la auditoría final es cualitativa. Las reseñas están principalmente en inglés, mientras que las categorías y explicaciones se normalizan en español.
