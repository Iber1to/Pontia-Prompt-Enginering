"""Orquestador público del pipeline."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Literal

import pandas as pd

from .config import PipelineConfig
from .data import explore_reviews, load_reviews, prepare_sample
from .deepseek_client import DeepSeekClient
from .extraction import extract_reviews, serialize_list_columns
from .persistence import atomic_write_json
from .prompts import EXTRACTION_PROMPT_VERSION, FILTER_PROMPT_VERSION
from .relevance import filter_reviews
from .schemas import RunMetrics

Stage = Literal["preprocess", "filter", "extract", "all"]


def _read_required(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe el artefacto requerido: {path}")
    return pd.read_csv(path)


def run_pipeline(
    config: PipelineConfig | None = None,
    stage: Stage = "all",
    client=None,
) -> dict:
    config = config or PipelineConfig()
    if stage not in {"preprocess", "filter", "extract", "all"}:
        raise ValueError(f"Etapa desconocida: {stage}")
    output = Path(config.output_dir)
    checkpoints = output / "checkpoints"
    output.mkdir(parents=True, exist_ok=True)
    checkpoints.mkdir(parents=True, exist_ok=True)
    metrics = RunMetrics(
        filter_model=config.filter_model,
        extraction_model=config.extraction_model,
        filter_prompt_version=FILTER_PROMPT_VERSION,
        extraction_prompt_version=EXTRACTION_PROMPT_VERSION,
    )
    result: dict = {"metrics": metrics}
    all_errors: list[str] = []

    if stage in {"preprocess", "filter", "all"}:
        started = time.perf_counter()
        frame = load_reviews(config.input_path)
        report = explore_reviews(frame)
        sample = prepare_sample(frame, config.sample_size)
        sample.to_csv(output / "sample_top_100.csv", index=False)
        metrics.original_rows = report["rows"]
        metrics.clean_rows = report["rows"] - report["null_content"]
        metrics.sampled_rows = len(sample)
        metrics.unique_rows = sample["content_hash"].nunique()
        metrics.cached_rows = len(sample) - metrics.unique_rows
        metrics.duration_seconds["preprocess"] = round(time.perf_counter() - started, 3)
        result.update({"exploration": report, "sample": sample})
    else:
        sample = _read_required(output / "sample_top_100.csv")

    if stage in {"filter", "all"}:
        started = time.perf_counter()
        active_client = client or DeepSeekClient(config)
        filtered, usage, errors = filter_reviews(
            sample, active_client, config.filter_model, config.filter_batch_size,
            config.filter_max_tokens, checkpoints / "relevance.jsonl",
            FILTER_PROMPT_VERSION,
        )
        filtered.to_csv(output / "relevance_results.csv", index=False)
        relevant = filtered[filtered["relevante"] == True].copy()  # noqa: E712
        relevant.to_csv(output / "relevant_reviews.csv", index=False)
        metrics.filter_usage = usage
        metrics.relevant_rows = len(relevant)
        metrics.duration_seconds["filter"] = round(time.perf_counter() - started, 3)
        all_errors.extend(errors)
        result.update({"filtered": filtered, "relevant": relevant})
    elif stage == "extract":
        relevant = _read_required(output / "relevant_reviews.csv")

    if stage in {"extract", "all"}:
        started = time.perf_counter()
        active_client = client or DeepSeekClient(config)
        structured, usage, errors = extract_reviews(
            relevant, active_client, config.extraction_model,
            config.extraction_batch_size, config.extraction_max_tokens,
            checkpoints / "extraction.jsonl", EXTRACTION_PROMPT_VERSION,
        )
        serialize_list_columns(structured).to_csv(
            output / "structured_reviews.csv", index=False
        )
        metrics.extraction_usage = usage
        metrics.duration_seconds["extract"] = round(time.perf_counter() - started, 3)
        all_errors.extend(errors)
        result["structured"] = structured

    metrics.errors = all_errors
    metrics.status = "partial" if all_errors else "completed"
    atomic_write_json(output / "run_metrics.json", metrics.model_dump(mode="json"))
    return result
