import json

import pytest

from videogame_reviews.config import PipelineConfig
from videogame_reviews.deepseek_client import (
    DeepSeekClient,
    PermanentLLMError,
    TransientLLMError,
)
from videogame_reviews.schemas import RelevanceBatch


HASH = "a" * 64
VALID = {"results": [{"content_hash": HASH, "relevante": True,
                      "motivo": "informativa", "justificacion_breve": "Útil"}]}


class SequenceTransport:
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.calls = 0

    def __call__(self, **kwargs):
        self.calls += 1
        outcome = next(self.outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def config(**changes):
    values = {"max_attempts": 3, "initial_retry_seconds": 0.001,
              "max_retry_seconds": 0.001}
    values.update(changes)
    return PipelineConfig(**values)


def test_client_parses_valid_response_and_usage():
    transport = SequenceTransport([(json.dumps(VALID), {"prompt_tokens": 10,
                                                         "completion_tokens": 4,
                                                         "total_tokens": 14})])
    client = DeepSeekClient(config(), transport=transport, sleeper=lambda _: None)
    batch, usage = client.complete([], "model", 100, RelevanceBatch)
    assert batch.results[0].content_hash == HASH
    assert usage.total_tokens == 14
    assert usage.calls == 1


def test_empty_content_and_transient_errors_are_retried():
    transport = SequenceTransport([
        ("", {}),
        TransientLLMError("429"),
        (json.dumps(VALID), {}),
    ])
    client = DeepSeekClient(config(), transport=transport, sleeper=lambda _: None)
    _, usage = client.complete([], "model", 100, RelevanceBatch)
    assert transport.calls == 3
    assert usage.retries == 2


def test_permanent_error_is_not_retried():
    transport = SequenceTransport([PermanentLLMError("401")])
    client = DeepSeekClient(config(), transport=transport, sleeper=lambda _: None)
    with pytest.raises(PermanentLLMError):
        client.complete([], "model", 100, RelevanceBatch)
    assert transport.calls == 1


def test_invalid_json_exhausts_retries():
    transport = SequenceTransport([("not json", {})] * 3)
    client = DeepSeekClient(config(), transport=transport, sleeper=lambda _: None)
    with pytest.raises(TransientLLMError, match="respuesta válida"):
        client.complete([], "model", 100, RelevanceBatch)
    assert transport.calls == 3
