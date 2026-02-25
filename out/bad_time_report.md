# Conjunction Data Validation Report

- **Report time (UTC):** 2026-02-25T12:09:59.868736+00:00
- **Message ID:** demo-bad-time
- **Creation time (UTC):** 2026-02-22T10:00:00+00:00
- **TCA (UTC):** 2026-02-21T10:05:00+00:00

## Summary
- PASS: 9
- WARN: 0
- FAIL: 1
- **OK:** False

## Findings
### [PASS] ID_DISTINCT
- Primary and secondary object_id are distinct.

### [FAIL] TIME_ORDER
- creation_time_utc is not before tca_utc.
- Details: `{'creation_time_utc': '2026-02-22T10:00:00+00:00', 'tca_utc': '2026-02-21T10:05:00+00:00'}`

### [PASS] FRAME_MATCH
- Primary and secondary frames match.
- Details: `{'frame': 'TEME'}`

### [PASS] POS_NORM
- Position norms look reasonable.
- Details: `{'primary_r_m': 7000000.0, 'secondary_r_m': 7000100.0}`

### [PASS] SPEED_NORM
- Speed norms look reasonable.
- Details: `{'primary_v_mps': 7500.0, 'secondary_v_mps': 7490.0}`

### [PASS] MISS_DISTANCE_CONSISTENCY
- miss_distance_m consistent with relative position norm.
- Details: `{'abs_err_m': 0.0, 'tolerance_m': 10.0}`

### [PASS] REL_SPEED_CONSISTENCY
- relative_speed_mps consistent with relative velocity norm.
- Details: `{'abs_err_mps': 0.0, 'tolerance_mps': 1.0}`

### [PASS] COV_SYMMETRY
- Covariance symmetry OK.
- Details: `{'max_abs_C_minus_CT': 0.0}`

### [PASS] COV_PSD
- Covariance PSD check OK.
- Details: `{'min_eigenvalue': 25.0}`

### [PASS] COV_STD
- Covariance std magnitudes look reasonable.
- Details: `{'max_std_m': 5.0}`
