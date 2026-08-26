# `rbf_sim` — reproducible simulation package

Implements **`METHODOLOGY_SPEC.md` v1.0 + amendments A-1…A-9** (v1.0 frozen 2026-08-03, before any outcome run).

**A-9 is the one amendment that changed a computed value.** The effective-rate
calculation now takes the complete monthly payment vector including internal
zero months, solves over `i > −1` so a loss is a negative rate rather than
"undefined", and reports its denominator: `apr_mean` is conditioned on IRR
existence, `duration_mean` on completion. Those are different sets.

> ⚠️ Everything this package produces is **simulated**. No observed seller revenue,
> repayment, or default outcome exists in this study. See spec §15 for binding
> interpretation limits.

## Run

```bash
python3 -m pytest rbf_sim/tests/ -q     # 643 tests
python3 run_baseline.py                 # -> results/baseline_v3_canonical.json
```

Deterministic: identical seeds reproduce **numerically at published precision**, and byte-identically **within a fixed runtime**. ~~bit-for-bit~~ withdrawn (D-041): the superseded `baseline_v2` / `baseline_equalcost_v1` generation was measured on macOS CPython 3.11.5 and differed in a few last-bit float values. The current generation has **not** been re-measured there, so no count is quoted for it. Verify with `research/verify_reproduction.py`, which runs the full validation battery as well as the baselines.

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
- RBF **contractual** burden is constant at `r` **by construction**, on the
  contractual base (net sales). The burden this package *reports* uses GMV as
  its denominator, so it equals `r·(1 − return rate)` and moves when returns
  move — constant only where the net-sales/GMV ratio is fixed, and before the
  final clipped payment. Direction is definitional; magnitude and the duration
  trade-off are measured.
- Provider recovery ordering is **not** definitional: under P4 it may lead or
  lag the cost-matched fixed arm depending on the realised path. Report it per
  scenario, never as a property of the structure.
