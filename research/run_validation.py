"""Validation battery. Run one section at a time:

    python3 run_validation.py 1   # Monte Carlo convergence
    python3 run_validation.py 2   # pricing sensitivity + equal-effective-cost cap
    python3 run_validation.py 4   # incomplete-recovery boundary search
    python3 run_validation.py 5   # RBF-G guardrail breakpoint
    python3 run_validation.py 6   # revenue-definition sensitivity

Results accumulate in results/validation_v1.json.
ALL OUTPUT IS SIMULATED under METHODOLOGY_SPEC.md v1.0 + amendments A-1..A-3.
"""
import json, os, sys
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rbf_sim.contracts import ContractTerms, rbf_payments, fix_b_payments, solve_apr
from rbf_sim.engine import run_scenario, paired_delta, bootstrap_ci
from rbf_sim.generator import PathParams, generate_cohort, reference_base_path

R0 = 185_000_000.0
BASE = dict(A=185_000_000.0, r=0.10, f=1.20, j=0.18, N_B=12)
W = 78
FP = "results/validation_v1.json"


def hdr(t):
    print("\n" + "=" * W); print(f"  {t}"); print("=" * W)


def save(key, val):
    os.makedirs("results", exist_ok=True)
    d = json.load(open(FP)) if os.path.exists(FP) else {}
    d[key] = val
    d["_meta"] = {"date": str(date.today()), "provenance": "SIMULATED - no observed data",
                  "spec": "METHODOLOGY_SPEC.md v1.0 + amendments A-1..A-3",
                  "base_terms": BASE, "R0": R0}
    json.dump(d, open(FP, "w"), indent=2, default=str)
    print(f"\n  [saved '{key}' -> {FP}]")


def sec1():
    hdr("1. MONTE CARLO CONVERGENCE  (500 / 2,000 / 5,000 / 10,000 paths)")
    print("  Scenario: sustained decline -40%. Effects must stabilise as N grows.\n")
    print(f"  {'N':>7}{'d n_HPB(0.15)':>16}{'MC interval':>24}{'d RR(12) pp':>14}{'MC interval':>22}")
    print("  " + "-" * (W - 4))
    conv = {}
    p = PathParams(R0=R0, T=24, shock="decline_sustained", shock_depth=0.40,
                   seasonality="moderate", label="sustained_decline")
    for n in (500, 2000, 5000, 10000):
        res = run_scenario(n, p, ContractTerms(**BASE))
        b = bootstrap_ci(paired_delta(res, "n_high_burden", threshold=0.15), n_boot=2000)
        r = bootstrap_ci(paired_delta(res, "recovery_ratio", k=12), n_boot=2000)
        conv[str(n)] = {"d_n_hpb": b, "d_rr12": r}
        print(f"  {n:>7}{b['mean']:>16.4f}   [{b['lo']:>7.4f},{b['hi']:>7.4f}]"
              f"{r['mean']*100:>12.3f}pp   [{r['lo']*100:>6.3f},{r['hi']*100:>6.3f}]")
    db = abs(conv["10000"]["d_n_hpb"]["mean"] - conv["5000"]["d_n_hpb"]["mean"])
    dr = abs(conv["10000"]["d_rr12"]["mean"] - conv["5000"]["d_rr12"]["mean"]) * 100
    ok = db < 0.05 and dr < 0.2
    print(f"\n  |change| 5,000 -> 10,000 : {db:.4f} months, {dr:.4f} pp")
    print(f"  => {'CONVERGED' if ok else 'NOT CONVERGED'} at 2 d.p. reporting precision.")
    print("\n  These are MONTE CARLO INTERVALS over simulated paths. They measure")
    print("  the stability of the mean given the chosen generative parameters.")
    print("  They are NOT population confidence intervals about real sellers.")
    conv["converged"] = ok
    save("convergence", conv)


def sec2():
    hdr("2. PRICING SENSITIVITY - CAP FACTOR f  +  EQUAL-EFFECTIVE-COST CAP")
    print("  Structure (fixed vs revenue-contingent) held constant; only PRICE moves.\n")
    ref = reference_base_path(PathParams(R0=R0), ContractTerms(**BASE))
    bpay = [x for x in fix_b_payments(ContractTerms(**BASE), 24) if x > 0]
    target = solve_apr(BASE["A"], bpay)
    print(f"  Benchmark B: j=18% nominal, N_B=12 -> effective APR {target:.4%}, "
          f"total repaid {sum(bpay):,.0f}")
    print(f"\n  {'f':>6}{'cap':>16}{'duration':>10}{'total repaid':>16}{'implied APR':>14}")
    print("  " + "-" * (W - 4))
    pricing = {}
    for f in (1.05, 1.08, 1.10, 1.12, 1.15, 1.20, 1.25, 1.30):
        t = ContractTerms(**{**BASE, "f": f})
        pay = [x for x in rbf_payments(ref, t) if x > 0]
        apr = solve_apr(t.A, pay)
        pricing[str(f)] = {"cap": t.cap, "duration": len(pay), "total": sum(pay), "apr": apr}
        mark = "  <- illustrative default" if abs(f - 1.20) < 1e-9 else ""
        print(f"  {f:>6.2f}{t.cap:>16,.0f}{len(pay):>10}{sum(pay):>16,.0f}{apr:>13.2%}{mark}")

    grid = [1.0 + i * 0.0005 for i in range(1, 801)]
    def gap(f):
        a = solve_apr(BASE["A"], [x for x in rbf_payments(ref, ContractTerms(**{**BASE, "f": f})) if x > 0])
        return abs((a if a is not None else 9.0) - target)
    best = min(grid, key=gap)
    tb = ContractTerms(**{**BASE, "f": best})
    pay = [x for x in rbf_payments(ref, tb) if x > 0]
    apr = solve_apr(tb.A, pay)
    print(f"\n  --- EQUAL-EFFECTIVE-COST CAP ---")
    print(f"  target effective APR (Benchmark B) : {target:.4%}")
    print(f"  equal-cost cap factor f*           : {best:.4f}")
    print(f"  cap / duration / total             : {tb.cap:,.0f} / {len(pay)} mo / {sum(pay):,.0f}")
    print(f"  achieved effective APR             : {apr:.4%}   (residual {abs(apr-target):.4%})")
    print(f"\n  Duration is an integer, so cost moves in steps; an exact match is")
    print(f"  not always attainable.")
    print(f"\n  READING: at f = {best:.3f} the simulated RBF contract costs about the")
    print(f"  same as the 18% amortizing loan while still remitting a share of")
    print(f"  revenue. PRICE and STRUCTURE are separable. The 41.30% figure is a")
    print(f"  property of the illustrative f = 1.20, not of revenue-based repayment.")
    save("pricing", {"benchmark_b_apr": target, "sweep": pricing,
                     "equal_cost": {"f_star": best, "cap": tb.cap, "duration": len(pay),
                                    "total": sum(pay), "apr": apr}})


def sec4():
    hdr("4. INCOMPLETE-RECOVERY BOUNDARY SEARCH")
    print("  Baseline v1 found 0.0% everywhere. Search harder: closure, zero-revenue")
    print("  months, longer downturns, larger advances, shorter horizons, write-off.\n")
    print(f"  {'probe':<32}{'T':>4}{'T_max':>7}{'A/R0':>6}{'incompl':>10}{'RR(24)':>9}{'dur':>7}")
    print("  " + "-" * (W - 4))
    probes = [
        ("closure @ m7", dict(shock="closure", shock_onset=7), 24, 0, 1.0),
        ("closure @ m13", dict(shock="closure", shock_onset=13), 24, 0, 1.0),
        ("temp closure 3m + -50%", dict(shock="temporary_closure", shock_depth=0.50, shock_onset=7), 24, 0, 1.0),
        ("extended downturn -60%", dict(shock="extended_downturn", shock_depth=0.60, shock_onset=7), 24, 0, 1.0),
        ("extended downturn -80%", dict(shock="extended_downturn", shock_depth=0.80, shock_onset=7), 24, 0, 1.0),
        ("sustained -40%, T=18", dict(shock="decline_sustained", shock_depth=0.40), 18, 0, 1.0),
        ("sustained -60%, T=18", dict(shock="decline_sustained", shock_depth=0.60), 18, 0, 1.0),
        ("advance 3xR0, sust -40%", dict(shock="decline_sustained", shock_depth=0.40), 24, 0, 3.0),
        ("advance 3xR0, sust -60%", dict(shock="decline_sustained", shock_depth=0.60), 24, 0, 3.0),
        ("write-off @ 18m, sust -40%", dict(shock="decline_sustained", shock_depth=0.40), 24, 18, 1.0),
        ("write-off @ 12m, sust -40%", dict(shock="decline_sustained", shock_depth=0.40), 24, 12, 1.0),
        ("write-off @ 12m, A=2xR0", dict(shock="decline_sustained", shock_depth=0.40), 24, 12, 2.0),
    ]
    res_all = {}
    for label, over, T, tmax, amult in probes:
        pp = PathParams(R0=R0, T=T, seasonality="moderate", label=label, **over)
        tt = ContractTerms(**{**BASE, "A": R0 * amult, "terminal_maturity": tmax})
        try:
            r = run_scenario(600, pp, tt)
        except ValueError as e:
            print(f"  {label:<32}{T:>4}{(tmax or '-'):>7}{amult:>6.1f}   cap unreachable on reference")
            continue
        a = r["arms"]["RBF"]
        res_all[label] = {"T": T, "terminal": tmax, "A_mult": amult,
                          "incomplete": a["incomplete_recovery_rate"],
                          "rr24": a["recovery_ratio"][24], "dur": a["duration_mean"]}
        dur = a["duration_mean"]
        print(f"  {label:<32}{T:>4}{(tmax or '-'):>7}{amult:>6.1f}"
              f"{a['incomplete_recovery_rate']*100:>9.1f}%{a['recovery_ratio'][24]*100:>8.1f}%"
              f"{(f'{dur:.1f}' if dur else 'n/a'):>7}")
    save("recovery_boundary", res_all)


def sec5():
    hdr("5. RBF-G GUARDRAIL BREAKPOINT ANALYSIS")
    t = ContractTerms(**BASE)
    print(f"  ANALYTIC RESULT (not a simulation artifact):")
    print(f"    floor BINDS when   r*obs < p_min = {t.p_min_mult}*r*R0  ->  obs < {t.p_min_mult:.2f}*R0")
    print(f"    floor APPLIES when obs >= hardship*R0                  ->  obs >= {t.hardship:.2f}*R0")
    print(f"    {t.p_min_mult:.2f} < {t.hardship:.2f}  =>  conditions are MUTUALLY EXCLUSIVE.")
    print(f"    The floor can never activate. It is dead code, provably, for any")
    print(f"    revenue path whatsoever. This explains the null result in baseline v1.")
    print(f"\n  Ceiling binds when obs > {t.p_max_mult:.2f}*R0.\n")
    print(f"  {'p_min_mult':>11}{'hardship':>10}{'floor':>12}{'floor mo':>10}{'ceil mo':>9}{'of':>10}")
    print("  " + "-" * (W - 4))
    pg = PathParams(R0=R0, T=24, seasonality="strong", growth=0.03)
    cohort = generate_cohort(1500, pg)
    bp = {}
    for pmin, hard in ((0.25, 0.50), (0.25, 0.20), (0.60, 0.50), (0.80, 0.50), (1.00, 0.50)):
        tg = ContractTerms(**{**BASE, "p_min_mult": pmin, "hardship": hard})
        series = [x for p in cohort for x in p.remittance_base(tg.remittance_basis)]
        n_floor = sum(1 for x in series if hard * R0 <= x < pmin * R0)
        n_ceil = sum(1 for x in series if x > tg.p_max_mult * R0)
        reachable = pmin > hard
        bp[f"pmin{pmin}_hard{hard}"] = {"reachable": reachable, "floor_months": n_floor,
                                        "ceiling_months": n_ceil, "total": len(series)}
        print(f"  {pmin:>11.2f}{hard:>10.2f}{('reachable' if reachable else 'DEAD'):>12}"
              f"{n_floor:>10}{n_ceil:>9}{len(series):>10}")
    print(f"\n  Scanned under STRONG seasonality + 3%/mo growth - the most favourable")
    print(f"  case for either guardrail to bind.")
    save("rbf_g_breakpoint", bp)


def sec6():
    hdr("6. REVENUE-DEFINITION SENSITIVITY  (remittance basis)")
    print("  gmv = orders x AOV is the ONLY exact identity. net_sales and")
    print("  cash_receipts are deductions from it, not parts of it (amendment A-1).\n")
    print(f"  {'basis':<16}{'fee':>6}{'duration':>10}{'total repaid':>16}{'RR(12)':>9}")
    print("  " + "-" * (W - 4))
    rd = {}
    for basis, fee in (("gmv", 0.0), ("net_sales", 0.0), ("cash_receipts", 0.0),
                       ("cash_receipts", 0.10)):
        pp = PathParams(R0=R0, T=24, seasonality="moderate", platform_fee_rate=fee)
        tt = ContractTerms(**{**BASE, "remittance_basis": basis})
        r = run_scenario(400, pp, tt)
        a = r["arms"]["RBF"]
        rd[f"{basis}_fee{fee}"] = {"duration": a["duration_mean"],
                                   "total": a["total_repaid_mean"],
                                   "rr12": a["recovery_ratio"][12]}
        print(f"  {basis:<16}{fee:>6.0%}{a['duration_mean']:>10.2f}"
              f"{a['total_repaid_mean']:>16,.0f}{a['recovery_ratio'][12]*100:>8.1f}%")
    print("\n  DECISION: remittance basis = net_sales (GMV net of returns).")
    print("  Platforms settle after returns, so remitting on GMV would charge the")
    print("  seller a share of money never received. Swept as S-16.")
    save("revenue_definition", rd)


if __name__ == "__main__":
    {"1": sec1, "2": sec2, "4": sec4, "5": sec5, "6": sec6}[sys.argv[1]]()
