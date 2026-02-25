from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import ValidationError

from .models import ConjunctionMessage


def load_message(path: str) -> ConjunctionMessage:
    p = Path(path)

    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {p}")

    if p.suffix.lower() in [".yaml", ".yml"]:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    elif p.suffix.lower() == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"Unsupported file type: {p.suffix}. Use .json or .yaml")

    if not isinstance(data, dict):
        raise ValueError("Top-level input must be an object/dict.")

    try:
        return ConjunctionMessage.model_validate(data)
    except ValidationError as e:
        # Re-raise with a cleaner message
        raise ValueError(f"Schema validation failed:\n{e}") from e
