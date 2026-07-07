"""Prompts versionados y separados por responsabilidad."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping

FILTER_PROMPT_VERSION = "filter-v1.0"
EXTRACTION_PROMPT_VERSION = "extraction-v1.0"

FILTER_SYSTEM_PROMPT = """Eres un clasificador estricto de reseñas de videojuegos.
Decide si cada reseña aporta opiniones o información evaluable sobre el juego.
Descarta texto vacío, spam, contenido incoherente y comentarios sin información útil.
Devuelve exclusivamente un objeto json con este esquema:
{"results":[{"content_hash":"sha256", "relevante":true,
"motivo":"informativa|texto_vacio|spam|incoherente|sin_informacion_evaluable",
"justificacion_breve":"máximo 300 caracteres"}]}
Usa motivo=informativa si y solo si relevante=true. No cambies hashes ni omitas filas.
"""

EXTRACTION_SYSTEM_PROMPT = """Extrae información estructurada de reseñas relevantes.
Usa solo evidencia explícita; no inventes. Devuelve exclusivamente un objeto json:
{"results":[{"content_hash":"sha256","sentimiento_general":"positivo|negativo|neutral|mixto",
"aspectos_positivos":[],"aspectos_negativos":[],
"dificultad":"demasiado_facil|facil|equilibrada|dificil|demasiado_dificil|no_mencionada",
"problemas_tecnicos":[],"relacion_calidad_precio":"alta|media|baja|no_mencionada",
"recomendacion_modelo":"si|no|condicional|no_determinable","resumen":"máximo 600 caracteres"}]}
Cuando no haya evidencia, usa listas vacías o el valor no_mencionada/no_determinable.
No cambies hashes ni omitas filas.
"""


def _payload(reviews: Iterable[Mapping]) -> str:
    records = [
        {"content_hash": row["content_hash"], "contenido": row["Contenido"]}
        for row in reviews
    ]
    return "RESEÑAS_INICIO\n" + json.dumps(records, ensure_ascii=False) + "\nRESEÑAS_FIN"


def build_filter_messages(reviews: Iterable[Mapping]) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": FILTER_SYSTEM_PROMPT},
        {"role": "user", "content": _payload(reviews)},
    ]


def build_extraction_messages(reviews: Iterable[Mapping]) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": _payload(reviews)},
    ]
