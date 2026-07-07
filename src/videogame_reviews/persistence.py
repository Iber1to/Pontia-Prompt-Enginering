"""Persistencia reanudable y escrituras atómicas."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def atomic_write_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.replace(temporary, target)


class CheckpointStore:
    """JSONL con cabecera de compatibilidad y reemplazo atómico."""

    def __init__(self, path: str | Path, metadata: dict[str, str]) -> None:
        self.path = Path(path)
        self.metadata = metadata

    def _read_lines(self) -> list[dict]:
        if not self.path.exists():
            return []
        records = []
        try:
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    records.append(json.loads(line))
        except (json.JSONDecodeError, OSError) as error:
            raise ValueError(f"Checkpoint corrupto: {self.path}") from error
        return records

    def load_records(self) -> dict[str, dict]:
        lines = self._read_lines()
        if not lines:
            return {}
        header = lines[0].get("_metadata")
        if header != self.metadata:
            raise ValueError(
                f"Checkpoint incompatible: esperado {self.metadata}, encontrado {header}"
            )
        result: dict[str, dict] = {}
        for record in lines[1:]:
            key = record.get("content_hash")
            if not key:
                raise ValueError(f"Checkpoint corrupto: registro sin content_hash en {self.path}")
            result[key] = record
        return result

    def append(self, record: dict) -> None:
        records = self.load_records()
        records[record["content_hash"]] = record
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        lines = [json.dumps({"_metadata": self.metadata}, ensure_ascii=False)]
        lines.extend(json.dumps(value, ensure_ascii=False) for value in records.values())
        temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.replace(temporary, self.path)
