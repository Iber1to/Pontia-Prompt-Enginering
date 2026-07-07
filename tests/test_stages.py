import pandas as pd

from videogame_reviews.extraction import extract_reviews
from videogame_reviews.relevance import filter_reviews
from videogame_reviews.schemas import (
    ExtractionBatch,
    RelevanceBatch,
    UsageMetrics,
)


HASH_A = "a" * 64
HASH_B = "b" * 64


class FakeClient:
    def __init__(self):
        self.calls = []

    def complete(self, messages, model, max_tokens, schema):
        text = str(messages)
        hashes = [value for value in (HASH_A, HASH_B) if value in text]
        self.calls.append((model, tuple(hashes)))
        if schema is RelevanceBatch:
            data = {"results": [
                {"content_hash": value, "relevante": value == HASH_A,
                 "motivo": "informativa" if value == HASH_A else "spam",
                 "justificacion_breve": "decisión"}
                for value in hashes
            ]}
        else:
            data = {"results": [
                {"content_hash": value, "sentimiento_general": "positivo",
                 "aspectos_positivos": ["historia"], "aspectos_negativos": [],
                 "dificultad": "no_mencionada", "problemas_tecnicos": [],
                 "relacion_calidad_precio": "no_mencionada",
                 "recomendacion_modelo": "si", "resumen": "Buena historia."}
                for value in hashes
            ]}
        return schema.model_validate(data), UsageMetrics(calls=1, total_tokens=10)


def sample():
    return pd.DataFrame([
        {"source_row_id": 1, "Contenido": "good", "content_hash": HASH_A},
        {"source_row_id": 2, "Contenido": "good", "content_hash": HASH_A},
        {"source_row_id": 3, "Contenido": "spam", "content_hash": HASH_B},
    ])


def test_filter_calls_duplicate_once_and_reconstructs_rows(tmp_path):
    client = FakeClient()
    result, usage, errors = filter_reviews(
        sample(), client, "flash", 2, 200, tmp_path / "filter.jsonl", "v1"
    )
    assert len(client.calls) == 1
    assert len(result) == 3
    assert result["relevante"].tolist() == [True, True, False]
    assert usage.calls == 1
    assert errors == []


def test_filter_resumes_without_calling_api(tmp_path):
    client = FakeClient()
    path = tmp_path / "filter.jsonl"
    first, _, _ = filter_reviews(sample(), client, "flash", 2, 200, path, "v1")
    second_client = FakeClient()
    second, _, _ = filter_reviews(sample(), second_client, "flash", 2, 200, path, "v1")
    pd.testing.assert_frame_equal(first, second)
    assert second_client.calls == []


def test_extraction_only_accepts_relevant_rows(tmp_path):
    relevant = sample().iloc[:2].assign(relevante=True)
    client = FakeClient()
    result, _, errors = extract_reviews(
        relevant, client, "pro", 3, 400, tmp_path / "extract.jsonl", "v1"
    )
    assert len(result) == 2
    assert result["aspectos_positivos"].iloc[0] == ["historia"]
    assert errors == []


def test_extraction_rejects_non_relevant_input(tmp_path):
    bad = sample().iloc[:1].assign(relevante=False)
    try:
        extract_reviews(bad, FakeClient(), "pro", 3, 400,
                        tmp_path / "extract.jsonl", "v1")
    except ValueError as error:
        assert "relevantes" in str(error)
    else:
        raise AssertionError("Debió rechazar una fila no relevante")
