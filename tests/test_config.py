import pytest

from videogame_reviews.config import PipelineConfig


def test_api_key_is_read_from_environment(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    assert PipelineConfig().get_api_key() == "test-key"


def test_missing_api_key_has_clear_error(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
        PipelineConfig().get_api_key()


def test_config_rejects_invalid_batch_size():
    with pytest.raises(ValueError):
        PipelineConfig(filter_batch_size=0)
