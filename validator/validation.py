from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

import numpy as np
from pydantic import BaseModel, Field

from .models import ConjunctionMessage
from .rules import Rules


Severity = Literal["PASS", "WARN", "FAIL"]


class Finding(BaseModel):
    check_id: str
    severity: Severity
    message: str
    details: Optional[Dict[str, Any]] = None


class ValidationReport(BaseModel):
    report_time_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    message_id: str
    creation_time_utc: datetime
    tca_utc: datetime

    findings: List[Finding]
    summary: Dict[str, int]
    ok: bool


def _add(findings: List[Finding], check_id: str, severity: Severity, message: str, details: Dict[str, Any] | None = None) -> None:
    findings.append(Finding(check_id=check_id, severity=severity, message=message, details=details))


def _norm3(v: List[float]) -> float:
    a = np.array(v, dtype=float)
    return float(np.linalg.norm(a))


def _cov3x3(flat9: List[float]) -> np.ndarray:
    return np.array(flat9, dtype=float).reshape((3, 3))


def validate_message(msg: ConjunctionMessage, rules: Rules | None = None) -> ValidationReport:
    rules = rules or Rules()
    findings: List[Finding] = []

    # --- Basic identity checks ---
    if msg.primary.object_id == msg.secondary.object_id:
        _add(findings, "ID_DISTINCT", "FAIL", "Primary and secondary object_id are identical.")
    else:
        _add(findings, "ID_DISTINCT", "PASS", "Primary and secondary object_id are distinct.")

    # --- Time consistency ---
    if msg.creation_time_utc >= msg.tca_utc:
        _add(
            findings,
            "TIME_ORDER",
            "FAIL",
            "creation_time_utc is not before tca_utc.",
            {"creation_time_utc": msg.creation_time_utc.isoformat(), "tca_utc": msg.tca_utc.isoformat()},
        )
    else:
        lead_s = (msg.tca_utc - msg.creation_time_utc).total_seconds()
        if lead_s < rules.time.warn_if_lead_time_s_below:
            _add(findings, "LEAD_TIME", "WARN", "Very small lead time between creation and TCA.", {"lead_time_s": lead_s})
        else:
            _add(findings, "LEAD_TIME", "PASS", "Lead time between creation and TCA is within expectations.", {"lead_time_s": lead_s})

    # --- Frame consistency ---
    if msg.primary.frame != msg.secondary.frame:
        _add(
            findings,
            "FRAME_MATCH",
            "WARN",
            "Primary and secondary frames differ (review needed).",
            {"primary_frame": msg.primary.frame, "secondary_frame": msg.secondary.frame},
        )
    else:
        _add(findings, "FRAME_MATCH", "PASS", "Primary and secondary frames match.", {"frame": msg.primary.frame})

    # --- State plausibility (very light sanity checks) ---
    p_r = _norm3(msg.primary.position_m)
    s_r = _norm3(msg.secondary.position_m)
    p_v = _norm3(msg.primary.velocity_mps)
    s_v = _norm3(msg.secondary.velocity_mps)

    if p_r > rules.state.max_position_norm_m_warn or s_r > rules.state.max_position_norm_m_warn:
        _add(findings, "POS_NORM", "WARN", "Large position norm detected (check units/reference).", {"primary_r_m": p_r, "secondary_r_m": s_r})
    else:
        _add(findings, "POS_NORM", "PASS", "Position norms look reasonable.", {"primary_r_m": p_r, "secondary_r_m": s_r})

    if p_v > rules.state.max_speed_mps_warn or s_v > rules.state.max_speed_mps_warn:
        _add(findings, "SPEED_NORM", "WARN", "Large speed detected (check units/reference).", {"primary_v_mps": p_v, "secondary_v_mps": s_v})
    else:
        _add(findings, "SPEED_NORM", "PASS", "Speed norms look reasonable.", {"primary_v_mps": p_v, "secondary_v_mps": s_v})

    # --- Consistency: miss distance & relative speed ---
    rel_pos = (np.array(msg.secondary.position_m, dtype=float) - np.array(msg.primary.position_m, dtype=float))
    rel_vel = (np.array(msg.secondary.velocity_mps, dtype=float) - np.array(msg.primary.velocity_mps, dtype=float))
    miss_est = float(np.linalg.norm(rel_pos))
    rel_speed_est = float(np.linalg.norm(rel_vel))

    if msg.miss_distance_m is not None:
        abs_err = abs(msg.miss_distance_m - miss_est)
        rel_err = abs_err / max(miss_est, 1e-9)
        tol = max(rules.consistency.miss_distance_abs_tol_m, rules.consistency.miss_distance_rel_tol_frac * miss_est)
        if abs_err > tol:
            _add(
                findings,
                "MISS_DISTANCE_CONSISTENCY",
                "FAIL",
                "miss_distance_m inconsistent with relative position norm.",
                {"miss_distance_m": msg.miss_distance_m, "estimated_m": miss_est, "abs_err_m": abs_err, "rel_err": rel_err, "tolerance_m": tol},
            )
        else:
            _add(findings, "MISS_DISTANCE_CONSISTENCY", "PASS", "miss_distance_m consistent with relative position norm.", {"abs_err_m": abs_err, "tolerance_m": tol})
    else:
        _add(findings, "MISS_DISTANCE_PRESENT", "WARN", "miss_distance_m not provided (cannot cross-check).")

    if msg.relative_speed_mps is not None:
        abs_err = abs(msg.relative_speed_mps - rel_speed_est)
        rel_err = abs_err / max(rel_speed_est, 1e-9)
        tol = max(rules.consistency.rel_speed_abs_tol_mps, rules.consistency.rel_speed_rel_tol_frac * rel_speed_est)
        if abs_err > tol:
            _add(
                findings,
                "REL_SPEED_CONSISTENCY",
                "WARN",
                "relative_speed_mps differs from norm of relative velocity (review).",
                {"relative_speed_mps": msg.relative_speed_mps, "estimated_mps": rel_speed_est, "abs_err_mps": abs_err, "rel_err": rel_err, "tolerance_mps": tol},
            )
        else:
            _add(findings, "REL_SPEED_CONSISTENCY", "PASS", "relative_speed_mps consistent with relative velocity norm.", {"abs_err_mps": abs_err, "tolerance_mps": tol})
    else:
        _add(findings, "REL_SPEED_PRESENT", "WARN", "relative_speed_mps not provided (cannot cross-check).")

    # --- Covariance sanity (optional) ---
    if msg.rel_pos_cov_m2 is None:
        _add(findings, "COV_PRESENT", "WARN", "rel_pos_cov_m2 not provided (cannot assess uncertainty validity).")
    else:
        C = _cov3x3(msg.rel_pos_cov_m2)

        # symmetry check
        sym_err = float(np.max(np.abs(C - C.T)))
        if sym_err > rules.covariance.symmetry_tol:
            _add(findings, "COV_SYMMETRY", "FAIL", "Covariance is not symmetric within tolerance.", {"max_abs_C_minus_CT": sym_err})
        else:
            _add(findings, "COV_SYMMETRY", "PASS", "Covariance symmetry OK.", {"max_abs_C_minus_CT": sym_err})

        # PSD-ish check via eigenvalues of symmetrized matrix
        Csym = 0.5 * (C + C.T)
        eigs = np.linalg.eigvalsh(Csym)
        min_eig = float(np.min(eigs))
        if min_eig < rules.covariance.psd_eig_tol:
            _add(findings, "COV_PSD", "FAIL", "Covariance not positive semi-definite (eigenvalue too negative).", {"min_eigenvalue": min_eig})
        else:
            _add(findings, "COV_PSD", "PASS", "Covariance PSD check OK.", {"min_eigenvalue": min_eig})

        # std magnitude checks
        diag = np.diag(Csym)
        if np.any(diag < 0):
            _add(findings, "COV_DIAG", "FAIL", "Covariance diagonal contains negative values.", {"diag": diag.tolist()})
        else:
            std = np.sqrt(diag)
            max_std = float(np.max(std))
            if max_std > rules.covariance.std_fail_m:
                _add(findings, "COV_STD", "FAIL", "Covariance std is extremely large (units/reference likely wrong).", {"max_std_m": max_std})
            elif max_std > rules.covariance.std_warn_m:
                _add(findings, "COV_STD", "WARN", "Covariance std is large (review).", {"max_std_m": max_std})
            else:
                _add(findings, "COV_STD", "PASS", "Covariance std magnitudes look reasonable.", {"max_std_m": max_std})

    # --- Summary ---
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for f in findings:
        counts[f.severity] += 1

    ok = counts["FAIL"] == 0

    return ValidationReport(
        message_id=msg.message_id,
        creation_time_utc=msg.creation_time_utc,
        tca_utc=msg.tca_utc,
        findings=findings,
        summary={k.lower(): v for k, v in counts.items()},
        ok=ok,
    )


def report_to_markdown(report: ValidationReport) -> str:
    lines: List[str] = []
    lines.append(f"# Conjunction Data Validation Report")
    lines.append("")
    lines.append(f"- **Report time (UTC):** {report.report_time_utc.isoformat()}")
    lines.append(f"- **Message ID:** {report.message_id}")
    lines.append(f"- **Creation time (UTC):** {report.creation_time_utc.isoformat()}")
    lines.append(f"- **TCA (UTC):** {report.tca_utc.isoformat()}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- PASS: {report.summary.get('pass', 0)}")
    lines.append(f"- WARN: {report.summary.get('warn', 0)}")
    lines.append(f"- FAIL: {report.summary.get('fail', 0)}")
    lines.append(f"- **OK:** {report.ok}")
    lines.append("")
    lines.append("## Findings")
    for f in report.findings:
        lines.append(f"### [{f.severity}] {f.check_id}")
        lines.append(f"- {f.message}")
        if f.details:
            lines.append(f"- Details: `{f.details}`")
        lines.append("")
    return "\n".join(lines)
