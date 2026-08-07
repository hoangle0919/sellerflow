# `rbf_sim` — reproducible simulation package

Implements **`METHODOLOGY_SPEC.md` v1.0** (frozen 2026-08-03, before any outcome run).

> ⚠️ Everything this package produces is **simulated**. No observed seller revenue,
> repayment, or default outcome exists in this study. See spec §15 for binding
> interpretation limits.

## Run

```bash
python3 -m pytest rbf_sim/tests/ -q     # 146 tests
python3 run_baseline.py                 # -> results/baseline_v1.json
```

Deterministic: identical seeds reproduce bit-for-bit.

## Modules

| Module | Spec § | Purpose |
|---|---|---|
| `generator.py` | 4, 5 | Revenue paths with **enforced accounting identities** |
| `contracts.py` | 6, 7, 8 | FIX-A, FIX-B, RBF, RBF-G. Pure arithmetic, no model calls |
| `metrics.py` | 10 | Burden, high-burden months, duration, recovery, underreporting |
| `engine.py` | 9, 10 | Paired runner — one path, four contracts |

## Why this replaces `backend/generate_data.py`

The original generator drew all ten features independently, violating
`revenue = orders × AOV` in **61%** of rows, and causing the project's own
integrity engine to flag **62.3%** of the data its credit model was trained on.

Here, exactly one of `{revenue, orders, AOV}` is derived and the rest sampled.
Identities are **computed, never sampled**, and enforced by
`tests/test_identities.py` — not by convention.

## Terminology (binding)

- **High-payment-burden month** — computed from revenue alone. The primary metric.
- **Distress month** — requires `m` and `F` assumptions. Secondary, always labelled.
- **Incomplete recovery within horizon** — **never** called a default rate.
- RBF burden is constant at `r` **by construction**. Direction is definitional;
  magnitude and the duration trade-off are measured.
