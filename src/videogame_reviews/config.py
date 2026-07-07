"""Configuración central del pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    """Parámetros configurables con valores seguros y reproducibles."""

    api_key_env: str = "DEEPSEEK_API_KEY"
    base_url: str = "https://api.deepseek.com"
    filter_model: str = "deepseek-v4-flash"
    extraction_model: str = "deepseek-v4-pro"
    filter_batch_size: int = 5
    extraction_batch_size: int = 3
    filter_max_tokens: int = 2000
    extraction_max_tokens: int = 4000
    temperature: float = 0.0
    thinking_enabled: bool = False
    request_timeout_seconds: float = 120.0
    max_attempts: int = 5
    initial_retry_seconds: float = 2.0
    max_retry_seconds: float = 30.0
    sample_size: int = 100
    input_path: Path = Path("videogames_reviews.csv")
    output_dir: Path = Path("outputs")

    def __post_init__(self) -> None:
        positive = {
            "filter_batch_size": self.filter_batch_size,
            "extraction_batch_size": self.extraction_batch_size,
            "filter_max_tokens": self.filter_max_tokens,
            "extraction_max_tokens": self.extraction_max_tokens,
            "request_timeout_seconds": self.request_timeout_seconds,
            "max_attempts": self.max_attempts,
            "sample_size": self.sample_size,
        }
        invalid = [name for name, value in positive.items() if value <= 0]
        if invalid:
            raise ValueError(f"Deben ser positivos: {', '.join(invalid)}")
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature debe estar entre 0 y 2")

    def get_api_key(self) -> str:
        """Obtiene la credencial sin almacenarla ni mostrarla."""
        value = os.environ.get(self.api_key_env, "").strip()
        if not value:
            raise RuntimeError(
                f"Falta la variable de entorno {self.api_key_env}. "
                "Configúrala antes de ejecutar llamadas a DeepSeek."
            )
        return value
