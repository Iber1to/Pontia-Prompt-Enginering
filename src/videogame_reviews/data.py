"""Carga, exploración y selección determinista de reseñas."""

from __future__ import annotations

import hashlib
import unicodedata
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"Contenido", "Valoración", "Recomendado_binario"}


def load_reviews(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Faltan columnas obligatorias: {sorted(missing)}")
    if "Unnamed: 0" in frame.columns:
        frame = frame.rename(columns={"Unnamed: 0": "source_row_id"})
    elif "source_row_id" not in frame.columns:
        frame.insert(0, "source_row_id", frame.index)
    return frame


def explore_reviews(frame: pd.DataFrame) -> dict:
    return {
        "rows": int(len(frame)),
        "columns": list(frame.columns),
        "dtypes": {key: str(value) for key, value in frame.dtypes.items()},
        "nulls": {key: int(value) for key, value in frame.isna().sum().items()},
        "null_content": int(frame["Contenido"].isna().sum()),
        "ratings": {
            str(key): int(value)
            for key, value in frame["Valoración"].value_counts(dropna=False).items()
        },
    }


def normalize_content(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return " ".join(normalized.split()).strip()


def content_hash(value: str) -> str:
    return hashlib.sha256(normalize_content(value).encode("utf-8")).hexdigest()


def prepare_sample(frame: pd.DataFrame, sample_size: int = 100) -> pd.DataFrame:
    clean = frame.dropna(subset=["Contenido"]).copy()
    clean["Contenido"] = clean["Contenido"].astype(str)
    clean["longitud_caracteres"] = clean["Contenido"].str.len()
    clean["content_hash"] = clean["Contenido"].map(content_hash)
    clean["_source_sort"] = clean["source_row_id"].astype(str)
    sample = (
        clean.sort_values(
            ["longitud_caracteres", "_source_sort"],
            ascending=[False, True],
            kind="mergesort",
        )
        .head(sample_size)
        .drop(columns="_source_sort")
        .reset_index(drop=True)
    )
    sample.insert(0, "sample_rank", range(1, len(sample) + 1))
    return sample


def unique_for_api(sample: pd.DataFrame) -> pd.DataFrame:
    return sample.drop_duplicates("content_hash", keep="first").reset_index(drop=True)
