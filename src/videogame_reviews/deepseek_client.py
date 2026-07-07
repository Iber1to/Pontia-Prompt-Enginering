"""Cliente DeepSeek compatible con OpenAI, validado e inyectable."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from .config import PipelineConfig
from .schemas import UsageMetrics

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class TransientLLMError(RuntimeError):
    """Error que puede resolverse reintentando la misma petición."""


class PermanentLLMError(RuntimeError):
    """Error de autenticación, saldo o formato que no debe reintentarse."""


class DeepSeekClient:
    def __init__(
        self,
        config: PipelineConfig,
        transport: Callable[..., tuple[str, dict[str, int]]] | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self.sleeper = sleeper
        self.transport = transport or self._openai_transport()

    def _openai_transport(self) -> Callable[..., tuple[str, dict[str, int]]]:
        from openai import OpenAI

        sdk = OpenAI(
            api_key=self.config.get_api_key(),
            base_url=self.config.base_url,
            timeout=self.config.request_timeout_seconds,
            max_retries=0,
        )

        def call(**kwargs) -> tuple[str, dict[str, int]]:
            try:
                response = sdk.chat.completions.create(**kwargs)
            except Exception as error:  # SDK expone varias subclases por versión
                status = getattr(error, "status_code", None)
                if status in {400, 401, 402, 422}:
                    raise PermanentLLMError(f"DeepSeek devolvió HTTP {status}") from error
                if status in {429, 500, 503} or isinstance(error, TimeoutError):
                    raise TransientLLMError(f"Error transitorio de DeepSeek: {status or 'timeout'}") from error
                raise TransientLLMError(f"Fallo de transporte: {type(error).__name__}") from error
            content = response.choices[0].message.content or ""
            usage = response.usage
            return content, {
                "prompt_tokens": int(getattr(usage, "prompt_tokens", 0) or 0),
                "completion_tokens": int(getattr(usage, "completion_tokens", 0) or 0),
                "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
            }

        return call

    def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int,
        schema: type[SchemaT],
    ) -> tuple[SchemaT, UsageMetrics]:
        aggregate = UsageMetrics()
        last_error: Exception | None = None
        for attempt in range(self.config.max_attempts):
            try:
                content, raw_usage = self.transport(
                    model=model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=self.config.temperature,
                    max_tokens=max_tokens,
                    stream=False,
                    extra_body={
                        "thinking": {
                            "type": "enabled" if self.config.thinking_enabled else "disabled"
                        }
                    },
                )
                aggregate.calls += 1
                aggregate.prompt_tokens += int(raw_usage.get("prompt_tokens", 0))
                aggregate.completion_tokens += int(raw_usage.get("completion_tokens", 0))
                aggregate.total_tokens += int(raw_usage.get("total_tokens", 0))
                if not content.strip():
                    raise TransientLLMError("DeepSeek devolvió contenido vacío")
                return schema.model_validate(json.loads(content)), aggregate
            except PermanentLLMError:
                raise
            except (TransientLLMError, json.JSONDecodeError, ValidationError) as error:
                last_error = error
                if not isinstance(error, TransientLLMError):
                    last_error = TransientLLMError(f"Respuesta inválida: {error}")
                if attempt == self.config.max_attempts - 1:
                    break
                aggregate.retries += 1
                delay = min(
                    self.config.initial_retry_seconds * (2**attempt),
                    self.config.max_retry_seconds,
                )
                self.sleeper(delay)
        raise TransientLLMError(
            f"No se obtuvo una respuesta válida tras {self.config.max_attempts} intentos"
        ) from last_error
