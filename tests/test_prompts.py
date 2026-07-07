from videogame_reviews.prompts import (
    EXTRACTION_PROMPT_VERSION,
    FILTER_PROMPT_VERSION,
    build_extraction_messages,
    build_filter_messages,
)


REVIEWS = [{"content_hash": "a" * 64, "Contenido": "Great game"}]


def test_filter_prompt_contains_json_schema_and_hash():
    text = str(build_filter_messages(REVIEWS)).lower()
    assert "json" in text
    assert "content_hash" in text
    assert "a" * 64 in text
    assert FILTER_PROMPT_VERSION


def test_extraction_prompt_is_separate_and_complete():
    text = str(build_extraction_messages(REVIEWS)).lower()
    for field in ("sentimiento_general", "aspectos_positivos", "dificultad",
                  "recomendacion_modelo"):
        assert field in text
    assert "json" in text
    assert EXTRACTION_PROMPT_VERSION != FILTER_PROMPT_VERSION
