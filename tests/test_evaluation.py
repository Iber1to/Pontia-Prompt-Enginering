import pandas as pd

from videogame_reviews.evaluation import (
    build_audit_sample,
    estimate_execution_plan,
    quality_metrics,
)


def frame():
    return pd.DataFrame([
        {"content_hash": f"{i:064x}", "Contenido": f"review {i}",
         "Valoración": "Recomendado", "relevante": i < 6,
         "motivo": "informativa" if i < 6 else "spam",
         "justificacion_breve": "x"}
        for i in range(12)
    ])


def test_audit_sample_is_deterministic_and_balanced():
    first = build_audit_sample(frame())
    second = build_audit_sample(frame())
    pd.testing.assert_frame_equal(first, second)
    assert first["relevante"].value_counts().to_dict() == {True: 5, False: 5}


def test_quality_metrics_reports_coverage_and_duplicates():
    sample = pd.concat([frame(), frame().iloc[:1]], ignore_index=True)
    structured = frame().iloc[:6]
    metrics = quality_metrics(sample, frame(), structured)
    assert metrics["duplicates_avoided"] == 1
    assert metrics["filter_coverage_pct"] == 100.0
    assert metrics["structured_coverage_pct"] == 100.0


def test_execution_plan_estimates_unique_calls_and_prompt_tokens():
    sample = frame()
    relevant = sample[sample["relevante"]].copy()

    estimate = estimate_execution_plan(
        sample,
        relevant,
        filter_batch_size=5,
        extraction_batch_size=3,
    )

    assert estimate["filter_unique_reviews"] == 12
    assert estimate["extraction_unique_reviews"] == 6
    assert estimate["estimated_filter_calls"] == 3
    assert estimate["estimated_extraction_calls"] == 2
    assert estimate["estimated_total_calls"] == 5
    assert estimate["estimated_filter_input_tokens"] > 0
    assert estimate["estimated_extraction_input_tokens"] > 0
    assert estimate["token_estimation_method"] == "ceil(caracteres_prompt/4)"
