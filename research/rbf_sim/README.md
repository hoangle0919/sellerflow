# `rbf_sim` — reproducible simulation package

Implements **`METHODOLOGY_SPEC.md` v1.0** (frozen 2026-08-03, before any outcome run).

> ⚠️ Everything this package produces is **simulated**. No observed seller revenue,
> repayment, or default outcome exists in this study. See spec §15 for binding
> interpretation limits.

## Run

```bash
python3 -m pytest rbf_sim/tests/ -q     # 629 tests
python3 run_baseline.py                 # -> results/baseline_v2_canonical.json
```

Deterministic: identical seeds reproduce **numerically at published precision**, and byte-identically **within a fixed runtime**. ~~bit-for-bit~~ withdrawn (D-041): on macOS CPython 3.11.5, `baseline_v2` differs in 9 last-bit float values and `baseline_equalcost_v1` in 2. Verify with `research/verify_reproduction.py`.

## Modules

| Module | Spec § | Purpose |
|---|---|---|
| `generator.py` | 4, 5 | Revenue paths with **enforced accounting identities** |
| `contracts.py` | 6, 7, 8 | FIX-A, FIX-B, RBF, RBF-G. Pure arithmetic, no model calls |
| `metrics.py` | 10 | Burden, high-burden months, duration, recovery, underreporting |
| `engine.py` | 9, 10 | Paired runner — one path, four contracts |

## Why this replaces `backend/generate_data.py`

The original generator drew all ten features independently, so `revenue`,
`orders` and `AOV` are mutually inconsistent. Measured: median ratio
`revenue / (orders × AOV)` = **0.9751**, with **60.97%** of rows (n=3,000)
outside the project's own reconciliation band `[0.55, 1.75]`, and the integrity
engine flagging **62.30%** of the first 1,000 rows its credit model was trained
on. (An earlier draft said "the identity is violated in 61% of rows"; with
independent draws it is violated in essentially every row — 61% is the share
outside the tolerance band, a different statement.)

Here, exactly one of `{revenue, orders, AOV}` is derived and the rest sampled.
Identities are **computed, never sampled**, and enforced by
`tests/test_identities.py` — not by convention.

## Terminology (binding)

- **High-payment-burden month** — computed from revenue alone. The primary metric.
- **Distress month** — requires `m` and `F` assumptions. Secondary, always labelled.
- **Incomplete recovery within horizon** — **never** called a default rate.
- RBF burden is constant at `r` **by construction**. Direction is definitional;
  magnitude and the duration trade-off are measured.
