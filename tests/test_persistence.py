import json

import pytest

from videogame_reviews.persistence import CheckpointStore, atomic_write_json


def test_checkpoint_roundtrip_and_resume(tmp_path):
    path = tmp_path / "checkpoint.jsonl"
    store = CheckpointStore(path, {"model": "m", "prompt_version": "v1"})
    store.append({"content_hash": "a" * 64, "value": 1})
    store.append({"content_hash": "b" * 64, "value": 2})
    assert set(store.load_records()) == {"a" * 64, "b" * 64}


def test_checkpoint_rejects_incompatible_metadata(tmp_path):
    path = tmp_path / "checkpoint.jsonl"
    CheckpointStore(path, {"model": "m", "prompt_version": "v1"}).append(
        {"content_hash": "a" * 64}
    )
    with pytest.raises(ValueError, match="incompatible"):
        CheckpointStore(path, {"model": "other", "prompt_version": "v1"}).load_records()


def test_corrupt_checkpoint_is_rejected(tmp_path):
    path = tmp_path / "checkpoint.jsonl"
    path.write_text("not-json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="corrupto"):
        CheckpointStore(path, {}).load_records()


def test_atomic_json_write(tmp_path):
    path = tmp_path / "nested" / "metrics.json"
    atomic_write_json(path, {"status": "completed"})
    assert json.loads(path.read_text(encoding="utf-8"))["status"] == "completed"
    assert not path.with_suffix(path.suffix + ".tmp").exists()
