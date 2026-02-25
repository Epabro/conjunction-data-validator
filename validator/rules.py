from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseModel, Field


class TimeRules(BaseModel):
    warn_if_lead_time_s_below: float = 60.0


class StateRules(BaseModel):
    max_position_norm_m_warn: float = 80_000_000.0
    max_speed_mps_warn: float = 15_000.0


class ConsistencyRules(BaseModel):
    miss_distance_abs_tol_m: float = 5.0
    miss_distance_rel_tol_frac: float = 0.10
    rel_speed_abs_tol_mps: float = 0.2
    rel_speed_rel_tol_frac: float = 0.10


class CovarianceRules(BaseModel):
    symmetry_tol: float = 1e-6
    psd_eig_tol: float = -1e-9
    std_warn_m: float = 100_000.0
    std_fail_m: float = 10_000_000.0


class Rules(BaseModel):
    time: TimeRules = Field(default_factory=TimeRules)
    state: StateRules = Field(default_factory=StateRules)
    consistency: ConsistencyRules = Field(default_factory=ConsistencyRules)
    covariance: CovarianceRules = Field(default_factory=CovarianceRules)


def load_rules(path: str | None) -> Rules:
    if path is None:
        return Rules()

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Rules file not found: {p}")

    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if data is None:
        data = {}

    if not isinstance(data, dict):
        raise ValueError("Rules file must be a YAML mapping/object at the top level.")

    return Rules.model_validate(data)
