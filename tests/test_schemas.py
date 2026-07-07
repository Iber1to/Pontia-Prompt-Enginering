import pytest
from pydantic import ValidationError

from videogame_reviews.schemas import (
    ExtractionBatch,
    RelevanceBatch,
)


HASH_A = "a" * 64
HASH_B = "b" * 64


def test_relevance_batch_accepts_valid_json():
    batch = RelevanceBatch.model_validate(
        {"results": [{"content_hash": HASH_A, "relevante": True,
                      "motivo": "informativa", "justificacion_breve": "Útil"}]}
    )
    assert batch.results[0].relevante is True


@pytest.mark.parametrize("field,value", [
    ("motivo", "otro"),
    ("content_hash", "short"),
])
def test_relevance_batch_rejects_invalid_values(field, value):
    item = {"content_hash": HASH_A, "relevante": True,
            "motivo": "informativa", "justificacion_breve": "Útil"}
    item[field] = value
    with pytest.raises(ValidationError):
        RelevanceBatch.model_validate({"results": [item]})


def test_batch_rejects_duplicate_hashes():
    item = {"content_hash": HASH_A, "relevante": True,
            "motivo": "informativa", "justificacion_breve": "Útil"}
    with pytest.raises(ValidationError, match="duplicados"):
        RelevanceBatch.model_validate({"results": [item, item]})


def test_extraction_rejects_unknown_enum_and_extra_field():
    item = {
        "content_hash": HASH_B,
        "sentimiento_general": "excelente",
        "aspectos_positivos": [],
        "aspectos_negativos": [],
        "dificultad": "no_mencionada",
        "problemas_tecnicos": [],
        "relacion_calidad_precio": "no_mencionada",
        "recomendacion_modelo": "no_determinable",
        "resumen": "Sin datos.",
        "inventado": 1,
    }
    with pytest.raises(ValidationError):
        ExtractionBatch.model_validate({"results": [item]})
