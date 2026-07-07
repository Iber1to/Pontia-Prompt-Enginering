"""Etapa 1: filtrado semántico de relevancia."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .persistence import CheckpointStore
from .prompts import build_filter_messages
from .schemas import RelevanceBatch, UsageMetrics
from .stages import process_batches


def filter_reviews(
    sample: pd.DataFrame,
    client,
    model: str,
    batch_size: int,
    max_tokens: int,
    checkpoint_path: str | Path,
    prompt_version: str,
) -> tuple[pd.DataFrame, UsageMetrics, list[str]]:
    unique = sample.drop_duplicates("content_hash", keep="first")
    rows = unique[["content_hash", "Contenido"]].to_dict(orient="records")
    store = CheckpointStore(
        checkpoint_path, {"model": model, "prompt_version": prompt_version}
    )

    def request(group):
        return client.complete(build_filter_messages(group), model, max_tokens, RelevanceBatch)

    records, usage, errors = process_batches(rows, batch_size, store, request)
    decisions = pd.DataFrame(records.values())
    if decisions.empty:
        result = sample.copy()
        result["relevante"] = pd.NA
        result["motivo"] = "error"
        result["justificacion_breve"] = "Sin respuesta válida"
    else:
        result = sample.merge(decisions, on="content_hash", how="left", validate="many_to_one")
        result["motivo"] = result["motivo"].fillna("error")
        result["justificacion_breve"] = result["justificacion_breve"].fillna(
            "Sin respuesta válida"
        )
    return result, usage, errors
