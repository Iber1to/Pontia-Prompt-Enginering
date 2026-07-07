"""Etapa 2: extracción estructurada sobre reseñas relevantes."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .persistence import CheckpointStore
from .prompts import build_extraction_messages
from .schemas import ExtractionBatch, UsageMetrics
from .stages import process_batches

LIST_COLUMNS = ["aspectos_positivos", "aspectos_negativos", "problemas_tecnicos"]


def extract_reviews(
    relevant: pd.DataFrame,
    client,
    model: str,
    batch_size: int,
    max_tokens: int,
    checkpoint_path: str | Path,
    prompt_version: str,
) -> tuple[pd.DataFrame, UsageMetrics, list[str]]:
    if "relevante" in relevant and not relevant["relevante"].fillna(False).all():
        raise ValueError("La extracción solo acepta reseñas relevantes")
    unique = relevant.drop_duplicates("content_hash", keep="first")
    rows = unique[["content_hash", "Contenido"]].to_dict(orient="records")
    store = CheckpointStore(
        checkpoint_path, {"model": model, "prompt_version": prompt_version}
    )

    def request(group):
        return client.complete(
            build_extraction_messages(group), model, max_tokens, ExtractionBatch
        )

    records, usage, errors = process_batches(rows, batch_size, store, request)
    extracted = pd.DataFrame(records.values())
    if extracted.empty:
        return relevant.iloc[0:0].copy(), usage, errors
    result = relevant.merge(extracted, on="content_hash", how="inner", validate="many_to_one")
    return result, usage, errors


def serialize_list_columns(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    for column in LIST_COLUMNS:
        if column in output:
            output[column] = output[column].map(
                lambda value: json.dumps(value, ensure_ascii=False)
            )
    return output
