import pandas as pd

from videogame_reviews.evaluation import build_audit_sample, quality_metrics


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
