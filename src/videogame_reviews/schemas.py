"""Contratos estrictos para entradas, respuestas y métricas."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ContentHash = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RelevanceReason(str, Enum):
    INFORMATIVA = "informativa"
    TEXTO_VACIO = "texto_vacio"
    SPAM = "spam"
    INCOHERENTE = "incoherente"
    SIN_INFORMACION = "sin_informacion_evaluable"


class RelevanceResult(StrictModel):
    content_hash: ContentHash
    relevante: bool
    motivo: RelevanceReason
    justificacion_breve: Annotated[str, Field(min_length=1, max_length=300)]

    @model_validator(mode="after")
    def reason_matches_decision(self) -> "RelevanceResult":
        if self.relevante != (self.motivo == RelevanceReason.INFORMATIVA):
            raise ValueError("motivo y relevante son incoherentes")
        return self


class UniqueBatch(StrictModel):
    @model_validator(mode="after")
    def hashes_are_unique(self):
        hashes = [item.content_hash for item in self.results]
        if len(hashes) != len(set(hashes)):
            raise ValueError("El lote contiene content_hash duplicados")
        return self


class RelevanceBatch(UniqueBatch):
    results: list[RelevanceResult]


class ExtractionResult(StrictModel):
    content_hash: ContentHash
    sentimiento_general: Literal["positivo", "negativo", "neutral", "mixto"]
    aspectos_positivos: list[str]
    aspectos_negativos: list[str]
    dificultad: Literal[
        "demasiado_facil", "facil", "equilibrada", "dificil",
        "demasiado_dificil", "no_mencionada",
    ]
    problemas_tecnicos: list[str]
    relacion_calidad_precio: Literal["alta", "media", "baja", "no_mencionada"]
    recomendacion_modelo: Literal["si", "no", "condicional", "no_determinable"]
    resumen: Annotated[str, Field(min_length=1, max_length=600)]


class ExtractionBatch(UniqueBatch):
    results: list[ExtractionResult]


class UsageMetrics(StrictModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    calls: int = 0
    retries: int = 0


class RunMetrics(StrictModel):
    status: Literal["completed", "partial", "failed"] = "completed"
    filter_model: str
    extraction_model: str
    filter_prompt_version: str
    extraction_prompt_version: str
    original_rows: int = 0
    clean_rows: int = 0
    sampled_rows: int = 0
    unique_rows: int = 0
    relevant_rows: int = 0
    cached_rows: int = 0
    errors: list[str] = Field(default_factory=list)
    filter_usage: UsageMetrics = Field(default_factory=UsageMetrics)
    extraction_usage: UsageMetrics = Field(default_factory=UsageMetrics)
    duration_seconds: dict[str, float] = Field(default_factory=dict)
