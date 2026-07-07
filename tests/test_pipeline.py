import json
from pathlib import Path

import pandas as pd

from videogame_reviews.config import PipelineConfig
from videogame_reviews.pipeline import run_pipeline
from videogame_reviews.schemas import ExtractionBatch, RelevanceBatch, UsageMetrics


class AllRelevantClient:
    def complete(self, messages, model, max_tokens, schema):
        import re
        hashes = list(dict.fromkeys(re.findall(r"[0-9a-f]{64}", str(messages))))
        if schema is RelevanceBatch:
            results = [{"content_hash": h, "relevante": True, "motivo": "informativa",
                        "justificacion_breve": "Aporta opinión"} for h in hashes]
        else:
            results = [{"content_hash": h, "sentimiento_general": "positivo",
                        "aspectos_positivos": ["jugabilidad"], "aspectos_negativos": [],
                        "dificultad": "no_mencionada", "problemas_tecnicos": [],
                        "relacion_calidad_precio": "no_mencionada",
                        "recomendacion_modelo": "si", "resumen": "Opinión positiva."}
                       for h in hashes]
        return schema.model_validate({"results": results}), UsageMetrics(calls=1, total_tokens=5)


def test_full_pipeline_with_fake_client(tmp_path):
    source = Path(__file__).parent / "fixtures" / "reviews.csv"
    config = PipelineConfig(input_path=source, output_dir=tmp_path,
                            sample_size=4, filter_batch_size=2,
                            extraction_batch_size=2)
    result = run_pipeline(config, stage="all", client=AllRelevantClient())
    assert result["metrics"].status == "completed"
    assert len(result["structured"]) == 4
    for name in ("sample_top_100.csv", "relevance_results.csv",
                 "relevant_reviews.csv", "structured_reviews.csv", "run_metrics.json"):
        assert (tmp_path / name).exists()
    metrics = json.loads((tmp_path / "run_metrics.json").read_text(encoding="utf-8"))
    assert metrics["sampled_rows"] == 4
    assert metrics["execution_estimate"]["estimated_total_calls"] == 4
    assert metrics["usage_scope"] == "current_process_only"


def test_preprocess_does_not_overwrite_completed_run_metrics(tmp_path):
    source = Path(__file__).parent / "fixtures" / "reviews.csv"
    metrics_path = tmp_path / "run_metrics.json"
    original = {"status": "completed", "relevant_rows": 3, "marker": "real-run"}
    metrics_path.write_text(json.dumps(original), encoding="utf-8")
    config = PipelineConfig(input_path=source, output_dir=tmp_path, sample_size=4)

    run_pipeline(config, stage="preprocess")

    assert json.loads(metrics_path.read_text(encoding="utf-8")) == original
    assert (tmp_path / "preprocess_metrics.json").exists()
