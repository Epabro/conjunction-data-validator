![CI](https://github.com/Epabro/conjunction-data-validator/actions/workflows/ci.yml/badge.svg)

# Conjunction Data Validator (MVP)

Autonomous, config-driven validation of conjunction / collision-avoidance data products (simplified CDM-like messages).  
Produces machine-readable JSON reports and operator-friendly Markdown summaries, and returns non-zero exit codes on validation failures (suitable for automation pipelines).

## Features
- Schema validation (required fields, types, forbidden extras)
- Time consistency checks (creation time vs TCA, lead-time warning)
- State plausibility checks (position/speed norms)
- Internal consistency checks (miss distance and relative speed)
- Covariance sanity checks (symmetry, PSD, magnitude thresholds)
- Outputs: `*_report.json`, `*_report.md`

## Quickstart

### Install (venv)
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`


### Validate a sample message
- `python -m validator.cli validate samples/good.json`
- `python -m validator.cli validate samples/bad_time.json ; echo $?`


Reports are written to `out/` by default:
- `out/good_report.json`
- `out/good_report.md`

### Configure thresholds
- Edit `rules.yaml` to adjust validation thresholds (tolerances, covariance limits, plausibility bounds).

## Project structure
- `validator/` core library + CLI
- `samples/` example inputs (good and intentionally bad)
- `tests/` pytest tests
- `.github/workflows/ci.yml` GitHub Actions CI
- `rules.yaml` validation thresholds

## Notes / limitations
- Message format is a simplified CDM-inspired schema for demonstration/testing.
- The MVP does not perform orbit propagation (can be extended with SGP4-based screening).

