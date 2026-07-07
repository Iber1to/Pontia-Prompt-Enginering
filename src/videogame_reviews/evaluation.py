"""Métricas estructurales y muestra determinista para revisión humana."""

from __future__ import annotations

import pandas as pd


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
