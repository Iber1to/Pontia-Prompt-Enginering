# Análisis de reseñas de videojuegos con DeepSeek

Proyecto final de Prompt Engineering: pipeline reproducible de dos etapas para filtrar reseñas poco informativas y extraer información estructurada de las relevantes.

## Arquitectura

El notebook `Ejercicio 2.ipynb` explica y orquesta el trabajo. La lógica probada se encuentra en `src/videogame_reviews`:

1. carga, exploración y selección determinista de las 100 reseñas más largas;
2. filtrado con `deepseek-v4-flash`, lotes de 5;
3. extracción con `deepseek-v4-pro`, lotes de 3 y modo de razonamiento desactivado;
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

## Decisiones de Prompt Engineering y límites

- **Modelos:** `deepseek-v4-flash` se usa para la clasificación binaria por su menor coste y latencia. `deepseek-v4-pro` se reserva para la extracción de ocho atributos, donde prima la consistencia semántica. El modo de razonamiento se desactiva porque ambas tareas requieren JSON controlado, no razonamiento abierto.
- **Lotes:** se envían 5 reseñas al filtro y 3 a la extracción. Con 80 textos únicos en la muestra y 79 relevantes únicos, el mínimo estimado es de **16 + 27 = 43 llamadas exitosas**. Los 20 duplicados no generan llamadas adicionales.
- **Tokenización:** antes de ejecutar se estima la entrada mediante `ceil(caracteres_del_prompt/4)`. Sobre esta entrega se estiman 139.714 tokens de entrada para filtrado y 140.470 para extracción, 280.184 en total. Es una aproximación conservadora; el consumo facturado debe consultarse en la respuesta de uso de la API.
- **Salida:** `max_tokens` se limita a 2.000 en filtrado y 4.000 en extracción para evitar JSON truncado sin permitir respuestas innecesariamente extensas.
- **Ritmo y rate limits:** las llamadas son secuenciales, por lo que no se consume concurrencia. No se impone una pausa fija después de éxitos; ante 429, 500, 503, timeout, contenido vacío o JSON inválido se aplica backoff exponencial de 2, 4, 8 y 16 segundos, limitado a 30 segundos, con un máximo de 5 intentos.
- **Interrupciones:** cada lote validado se guarda inmediatamente. Si se agota el saldo o persiste un límite, la ejecución termina parcial y una nueva ejecución continúa desde el checkpoint sin volver a pagar los lotes aceptados.
- **Coste:** se calcula como tokens de entrada y salida por la tarifa vigente de cada modelo. Las tarifas no se fijan en código porque pueden cambiar; deben comprobarse en la documentación oficial de DeepSeek antes de ejecutar.

## Resultados

- `sample_top_100.csv`: muestra exigida.
- `relevance_results.csv`: decisión para las 100 filas.
- `relevant_reviews.csv`: DataFrame reducido.
- `structured_reviews.csv`: ocho atributos extraídos.
- `run_metrics.json`: cobertura, llamadas, reintentos, tokens observados en el proceso y estimación completa. `usage_scope=current_process_only` aclara que las llamadas servidas desde checkpoints no vuelven a contabilizarse.
- `preprocess_metrics.json`: métricas de una ejecución aislada de preprocesamiento; nunca sobrescribe `run_metrics.json`.

Los CSV generados y checkpoints están excluidos de Git.

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

La muestra por longitud favorece reseñas extensas y no representa necesariamente todo el dataset. No existe ground truth para relevancia o atributos, por lo que la auditoría final es cualitativa. Las reseñas están principalmente en inglés, mientras que las categorías y explicaciones se normalizan en español de España.
