"""Métricas estructurales y muestra determinista para revisión humana."""

from __future__ import annotations

import json
import math

import pandas as pd

from .prompts import build_extraction_messages, build_filter_messages


def estimate_execution_plan(
    sample: pd.DataFrame,
    relevant: pd.DataFrame,
    filter_batch_size: int,
    extraction_batch_size: int,
) -> dict:
    """Estima llamadas y tokens de entrada con cuatro caracteres por token."""

    def stage_estimate(frame, batch_size, message_builder):
        unique = frame.drop_duplicates("content_hash", keep="first")
        rows = unique[["content_hash", "Contenido"]].to_dict(orient="records")
        characters = 0
        for start in range(0, len(rows), batch_size):
            messages = message_builder(rows[start : start + batch_size])
            characters += len(json.dumps(messages, ensure_ascii=False))
        return len(rows), math.ceil(characters / 4)

    filter_unique, filter_tokens = stage_estimate(
        sample, filter_batch_size, build_filter_messages
    )
    extraction_unique, extraction_tokens = stage_estimate(
        relevant, extraction_batch_size, build_extraction_messages
    )
    filter_calls = math.ceil(filter_unique / filter_batch_size)
    extraction_calls = math.ceil(extraction_unique / extraction_batch_size)
    return {
        "filter_unique_reviews": filter_unique,
        "extraction_unique_reviews": extraction_unique,
        "estimated_filter_calls": filter_calls,
        "estimated_extraction_calls": extraction_calls,
        "estimated_total_calls": filter_calls + extraction_calls,
        "estimated_filter_input_tokens": filter_tokens,
        "estimated_extraction_input_tokens": extraction_tokens,
        "estimated_total_input_tokens": filter_tokens + extraction_tokens,
        "token_estimation_method": "ceil(caracteres_prompt/4)",
    }


def build_audit_sample(filtered: pd.DataFrame, seed: int = 26) -> pd.DataFrame:
    unique = filtered.drop_duplicates("content_hash", keep="first")
    relevant = unique[unique["relevante"] == True].sample(  # noqa: E712
        n=min(5, int((unique["relevante"] == True).sum())),  # noqa: E712
        random_state=seed,
    )
    discarded = unique[unique["relevante"] == False].sample(  # noqa: E712
        n=min(5, int((unique["relevante"] == False).sum())),  # noqa: E712
        random_state=seed,
    )
    audit = pd.concat([relevant, discarded], ignore_index=True)
    audit["contenido_abreviado"] = audit["Contenido"].str.slice(0, 240)
    columns = [
        "content_hash", "contenido_abreviado", "Valoración",
        "relevante", "motivo", "justificacion_breve",
    ]
    return audit[[column for column in columns if column in audit]]


def quality_metrics(
    sample: pd.DataFrame,
    filtered: pd.DataFrame,
    structured: pd.DataFrame,
) -> dict[str, float | int]:
    accepted = filtered[filtered["relevante"] == True]  # noqa: E712
    unique_sample = sample["content_hash"].nunique()
    unique_structured = structured["content_hash"].nunique() if not structured.empty else 0
    return {
        "sample_rows": int(len(sample)),
        "unique_sample_rows": int(unique_sample),
        "duplicates_avoided": int(len(sample) - unique_sample),
        "filter_coverage_pct": round(filtered["relevante"].notna().mean() * 100, 2),
        "relevant_rows": int(len(accepted)),
        "structured_unique_rows": int(unique_structured),
        "structured_coverage_pct": round(
            (unique_structured / accepted["content_hash"].nunique() * 100)
            if not accepted.empty else 100.0,
            2,
        ),
    }
