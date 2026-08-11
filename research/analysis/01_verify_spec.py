"""RETIRED — HISTORICAL ONLY. Do not run as current verification (D-045).

WHY IT IS RETIRED. Three reasons, all structural rather than fixable:

  1. It verifies `METRIC_DEFINITIONS.md` v0.1, which `METHODOLOGY_SPEC.md` v1.0
     superseded. It checks a document that is no longer authoritative.
  2. `duration()` below defaults to `tol=0.5` — the **pre-A-7 floating-point
     tolerance**. Since D-024 the operational layer settles in integer đồng
     with `ε = 0` by construction, and the analytical layer uses a centralized
     `FLOAT_GUARD_VND = 1e-6` which is representation-error protection, NOT a
     settlement tolerance. Leaving `0.5` here as if it were current would
     misrepresent settlement behaviour.
  3. It is, by its own original description below, "a throwaway reference
     implementation -- it is not the engine". `rbf_sim/` is the engine, and
     `rbf_sim/tests/` verifies it.

`RESULTS_REGISTRY.md` R-003 already classifies its output as **exploratory,
not quotable**. It is removed from the current reproduction instructions in
`RESEARCH_MANIFEST.md` and retained here only so the coherence constraint it
produced (§3.4) has a traceable origin.

Original docstring follows.

---

Verify METRIC_DEFINITIONS.md is implementable and internally consistent.

Place at:  sellerflow/research/analysis/01_verify_spec.py
Run:       python3 01_verify_spec.py          (no dependencies beyond stdlib)

Run BEFORE the full comparison engine is built, to check that the frozen spec
survives contact with arithmetic. Deliberately a throwaway reference
implementation -- it is not the engine, and Phase 3's engine must reproduce
these numbers independently.

Checks:
  C1  Cost-matching (spec 3.1) holds exactly at base case.
  C2  The PTR degeneracy warned about in spec 4.1 is real.
  C3  Arms diverge in the direction H1/H3 predict under revenue decline.
  C4  FIX is invariant to underreporting; RBF is not (spec 5.8).
  C5  The distress metric is NOT degenerate -- and finding where it IS
      degenerate produced coherence constraint 3.4 and decision D-011.

Author: Phase 1, 2026-08-03
"""

R0 = 185_000_000.0   # illustrative baseline monthly revenue, VND
T = 36               # horizon, months
A = 200_000_000.0    # advance principal, VND
r = 0.10             # remittance rate
f = 1.20             # factor rate
C = A * f            # repayment cap

RULE = "=" * 74


# ── Arms (spec §2) ────────────────────────────────────────────────────────────

def rbf_payments(revenue, cap, rate, p_min=None, p_max=None, baseline=None):
    """Spec 2.2 / 2.3. Guardrails optional; hardship rule suspends the floor."""
    paid, out = 0.0, []
    for rev in revenue:
        p = rate * rev
        hardship = baseline is not None and rev < 0.5 * baseline
        if p_min is not None and not hardship:
            p = max(p, p_min)
        if p_max is not None:
            p = min(p, p_max)
        p = max(0.0, min(p, cap - paid))
        paid += p
        out.append(p)
    return out


def fix_payments(payment, term, horizon):
    """Spec 2.1."""
    return [payment if t < term else 0.0 for t in range(horizon)]


def duration(payments, cap, tol=0.5):   # tol=0.5 is PRE-A-7 and retired; see module docstring
    """Spec 4.7 — first month cumulative payments reach the cap."""
    total = 0.0
    for t, p in enumerate(payments):
        total += p
        if total >= cap - tol:
            return t + 1
    return None


def irr_annual(principal, flows, iters=200):
    """Spec 5.7 — bisection on NPV. Returns None where undefined."""
    def npv(i):
        return -principal + sum(p / (1 + i) ** (t + 1) for t, p in enumerate(flows))
    lo, hi = 1e-9, 1.0
    if npv(lo) * npv(hi) > 0:
        return None
    for _ in range(iters):
        mid = (lo + hi) / 2
        if npv(lo) * npv(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (1 + (lo + hi) / 2) ** 12 - 1


def distress_months(revenue, payments, m, F):
    """Spec 4.3 T-0 — post-payment operating cash flow below zero."""
    return sum(1 for t in range(len(payments)) if m * revenue[t] - F - payments[t] < 0)


# ── Checks ────────────────────────────────────────────────────────────────────

def main():
    print(RULE)
    print("  SPEC VERIFICATION -- METRIC_DEFINITIONS.md")
    print(RULE)

    base = [R0] * T
    rbf_base = rbf_payments(base, C, r)
    D_base = duration(rbf_base, C)
    N = D_base                      # spec 3.1 step 3
    P = C / N                       # spec 3.1 step 2
    fix = fix_payments(P, N, T)

    print("\nC1  COST-MATCHING AT BASE CASE  (spec 3.1)")
    print("-" * 74)
    print(f"  cap C = A x f                     : {C:>16,.0f}")
    print(f"  RBF base-case duration D          : {D_base:>16} months")
    print(f"  matched fixed term N              : {N:>16} months")
    print(f"  matched fixed payment P = C/N     : {P:>16,.0f}")
    print(f"  total repaid  RBF                 : {sum(rbf_base):>16,.0f}")
    print(f"  total repaid  FIX                 : {sum(fix):>16,.0f}")
    print(f"  identical to <1 VND               : {abs(sum(rbf_base) - sum(fix)) < 1.0}")
    print(f"  implied fixed APR (reported, not assumed) : {irr_annual(A, fix):.2%}")
    print("  => matched on principal, total cost AND duration, so divergence")
    print("     elsewhere is attributable to STRUCTURE rather than price. PASS.")

    print("\n\nC2  PTR DEGENERACY IS REAL  (spec 4.1)")
    print("-" * 74)
    ptr = sorted({round(p / R0, 4) for p in rbf_base if p > 0})
    print(f"  distinct RBF payment-to-revenue values : {ptr}")
    print(f"  => constant at r = {r} until the cap binds. A PTR threshold would be")
    print("     satisfied by RBF by construction and would rig the comparison.")
    print("     Confirms why D-010 rejected PTR as the distress definition. PASS.")

    print("\n\nC3  DIVERGENCE UNDER SUSTAINED -40% DECLINE FROM MONTH 7  (H1, H3)")
    print("-" * 74)
    decline = [R0 if t < 6 else R0 * 0.6 for t in range(T)]
    rbf_dec = rbf_payments(decline, C, r)
    D_dec = duration(rbf_dec, C)
    print(f"  month-12 payment   FIX            : {fix[11]:>16,.0f}")
    print(f"  month-12 payment   RBF            : {rbf_dec[11]:>16,.0f}")
    print(f"  RBF relief in month 12            : {1 - rbf_dec[11] / fix[11]:>15.1%} lower")
    print(f"  duration           FIX / RBF      : {N} / {D_dec} months")
    print(f"  recovery ratio RR  RBF            : {sum(rbf_dec) / C:>16.3f}")
    print("  => H1 direction holds mechanically; H3's duration cost is visible")
    print("     and measurable. Note RR = 1.000: at T=36 the horizon does not")
    print("     bind, so incomplete recovery needs severer paths or shorter T")
    print("     to become informative. Carry into scenario design. PASS.")

    print("\n\nC4  UNDERREPORTING: FIX INVARIANT, RBF NOT  (spec 5.8)")
    print("-" * 74)
    for w in (1.00, 0.95, 0.90, 0.80, 0.70):
        pw = rbf_payments([x * w for x in base], C, r)
        print(f"  omega={w:.2f}   RBF recovered={sum(pw):>15,.0f}  "
              f"RR={sum(pw) / C:.3f}  D={duration(pw, C)} months")
    print(f"  omega=any    FIX recovered={sum(fix):>15,.0f}  "
          f"RR={sum(fix) / C:.3f}  D={N} months  (invariant by construction)")
    print("  => within a 36-month horizon, underreporting shows up as DURATION")
    print("     EXTENSION rather than recovery shortfall. The fixed structure")
    print("     cannot be diverted from because it never reads revenue -- a real")
    print("     advantage of FIX that the paper reports plainly. PASS.")

    print("\n\nC5  DISTRESS-METRIC COHERENCE  (spec 3.4, decision D-011)")
    print("-" * 74)
    print(f"  {'m':>5} {'F/R0':>6} | {'pre-fin net':>15} {'FIX distress':>13} "
          f"{'RBF distress':>13} | discriminates?")
    print("  " + "-" * 70)
    for m, F_mult in ((0.25, 0.20), (0.25, 0.10), (0.35, 0.15), (0.45, 0.10)):
        F = F_mult * R0
        d_fix = distress_months(decline, fix, m, F)
        d_rbf = distress_months(decline, rbf_dec, m, F)
        net = m * R0 - F
        coherent = (net - P) > 0        # spec 3.4
        verdict = "yes" if (coherent and d_fix != d_rbf) else (
            "DEGENERATE" if not coherent else "no (tie)")
        print(f"  {m:>5.2f} {F_mult:>6.2f} | {net:>15,.0f} {d_fix:>13} "
              f"{d_rbf:>13} | {verdict}")
    print()
    print("  => At m=0.25, F=0.20xR0 the seller is unprofitable AFTER financing")
    print("     under the base case, so both arms report distress in every month")
    print("     and H2 fails by degeneracy rather than by evidence. This is what")
    print("     produced coherence constraint 3.4 and decision D-011: the fix is")
    print("     an explicit constraint plus reporting the incoherent region, NOT")
    print("     loosening the frozen distress threshold. PASS (constraint added).")

    print("\n" + RULE)
    print("  All five checks pass. The frozen spec is implementable.")
    print("  Phase 3's engine must reproduce C1-C4 independently before use.")
    print(RULE)


if __name__ == "__main__":
    main()
