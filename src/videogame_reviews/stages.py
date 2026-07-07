"""Motor común de lotes con reanudación y degradación a filas individuales."""

from __future__ import annotations

from collections.abc import Callable

from pydantic import BaseModel

from .persistence import CheckpointStore
from .schemas import UsageMetrics


def add_usage(total: UsageMetrics, current: UsageMetrics) -> None:
    for name in ("prompt_tokens", "completion_tokens", "total_tokens", "calls", "retries"):
        setattr(total, name, getattr(total, name) + getattr(current, name))


def process_batches(
    rows: list[dict],
    batch_size: int,
    store: CheckpointStore,
    request: Callable[[list[dict]], tuple[BaseModel, UsageMetrics]],
) -> tuple[dict[str, dict], UsageMetrics, list[str]]:
    cached = store.load_records()
    pending = [row for row in rows if row["content_hash"] not in cached]
    usage = UsageMetrics()
    errors: list[str] = []

    def process(group: list[dict]) -> None:
        if not group:
            return
        expected = {row["content_hash"] for row in group}
        try:
            response, current_usage = request(group)
            add_usage(usage, current_usage)
            received = {item.content_hash for item in response.results}
            if received != expected:
                raise ValueError(
                    f"Hashes de respuesta no coinciden: esperados={expected}, recibidos={received}"
                )
            for item in response.results:
                record = item.model_dump(mode="json")
                store.append(record)
                cached[item.content_hash] = record
        except Exception as error:
            if len(group) > 1:
                middle = len(group) // 2
                process(group[:middle])
                process(group[middle:])
            else:
                errors.append(f"{group[0]['content_hash']}: {type(error).__name__}: {error}")

    for start in range(0, len(pending), batch_size):
        process(pending[start : start + batch_size])
    return cached, usage, errors
