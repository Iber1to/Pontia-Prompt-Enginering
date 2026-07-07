from pathlib import Path

import pandas as pd
import pytest

from videogame_reviews.data import (
    explore_reviews,
    load_reviews,
    prepare_sample,
    unique_for_api,
)


FIXTURE = Path(__file__).parent / "fixtures" / "reviews.csv"


def test_load_and_explore_fixture():
    frame = load_reviews(FIXTURE)
    report = explore_reviews(frame)
    assert frame.columns[0] == "source_row_id"
    assert report["rows"] == 5
    assert report["null_content"] == 1


def test_prepare_sample_is_deterministic_and_preserves_duplicates():
    frame = load_reviews(FIXTURE)
    first = prepare_sample(frame, sample_size=4)
    second = prepare_sample(frame, sample_size=4)
    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 4
    assert first["sample_rank"].tolist() == [1, 2, 3, 4]
    assert first["content_hash"].nunique() == 3
    assert len(unique_for_api(first)) == 3


def test_missing_required_column_is_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"Contenido": ["x"]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="columnas obligatorias"):
        load_reviews(path)


def test_source_id_falls_back_to_original_index(tmp_path):
    path = tmp_path / "reviews.csv"
    pd.DataFrame({"Contenido": ["a"], "Valoración": ["Recomendado"],
                  "Recomendado_binario": [1]}).to_csv(path, index=False)
    assert load_reviews(path)["source_row_id"].tolist() == [0]
