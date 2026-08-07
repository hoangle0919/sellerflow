# Phase 0 — Project Audit

**Project:** Revenue-Based Financing (RBF) research + product
**Repository:** `github.com/hoangle0919/sellerflow` @ `bff1477` (2026-07-23)
**Live:** `https://sellerflow-production.up.railway.app`
**Audit date:** 2026-08-03
**Auditor:** Claude (research lead / QA)
**Method:** Full clone, static read of all 4,095 LOC, dependency install, model retrain, full test run, live-site fetch, and three purpose-written reproducibility probes (`backend/audit_evidence.py`).

---

## 0. One-paragraph verdict

The engineering is genuinely good and the *self-documentation is unusually honest* — the README already refuses several claims most student projects would make. The problem is not dishonesty; it is that **the honesty is aimed at the wrong target.** The README carefully disclaims that 0.92 AUC is "synthetic." The deeper issue, which nothing in the repo discloses, is that the synthetic benchmark is **mathematically circular** and the synthetic population is **internally impossible**. Separately, **the live site is not the code in the repo** — it serves the superseded "SellerFlow" credit-limit product, so the deployed artifact contradicts the README, the repo, and the intended RBF narrative. Both are fixable in August. Neither is fixable by writing better prose.

---

## 1. What actually exists

### 1.1 Verified stack

| Layer | Reality |
|---|---|
| Backend | Python 3.10, FastAPI 0.111, SQLite, 1,617 LOC across 9 modules |
| Risk model | scikit-learn RF (300 trees, depth 8) + LogisticRegression, blended 0.65/0.35 |
| Financing engine | `financing_engine.py`, 279 LOC, pure arithmetic, zero model calls |
| Integrity engine | `integrity_engine.py`, 189 LOC, 5 deterministic rules |
| Frontend | Single-file `index.html`, 1,583 LOC, vanilla JS, no build step |
| Tests | 47 passing (`pytest tests/ -q` → `47 passed in 5.46s`) |
| Deploy | Railway/Nixpacks, healthcheck `/api/health`, models trained at boot |

### 1.2 Verified working (I ran these)

```
$ python3 train_model.py
RF AUC: 0.9001 · LR AUC: 0.9237 · Ensemble AUC: 0.9182     ← reproduces the README's "0.92"

$ python3 -m pytest tests/ -q
47 passed, 1 warning in 5.46s                               ← README says 29; doc drift
```

The financing engine's math is correct, well-commented, and unit-tested against hand-computed values. The provenance tagging (`user_entered_fact` / `system_derived_metric` / `assumption`) is a real design achievement and should be preserved and promoted — it is the single most publishable thing in the codebase.

---

## 2. What can be preserved

Ranked by value to the final project.

| Asset | Verdict | Why |
|---|---|---|
| `financing_engine.py` | **Keep, extend** | Correct RBF mechanics, pure, tested. It becomes the RBF arm of the experiment. |
| Provenance tagging system | **Keep, feature it** | Directly satisfies the brief's "separate user values / assumptions / outputs." Rare and defensible. |
| `revenue_metrics()` history path | **Keep, activate** | Volatility/CV/drawdown code already exists but is dead — the form never supplies history. Wiring this up is the highest-leverage single change. |
| Refusal to fabricate (`null` + `missing_data_note`) | **Keep** | Already correct behavior. Cite it in the paper. |
| `validate_on_real_data.py` | **Keep, reframe** | Honest, reproducible, real data. But see §4.3 — it validates the wrong thing for this project. |
| 47-test suite | **Keep, extend** | Real assertions with hand-computed expectations, not smoke tests. |
| Frontend design system | **Keep** | Polished, responsive, self-hosted fonts incl. Vietnamese subset. Do not rewrite. |
| `integrity_engine.py` | **Keep, requalify** | Good rules; currently mis-scoped (see §4.4). Becomes the "revenue diversion / misreporting" research strand (SQ4/H5). |
| RBF rename work | **Keep, finish** | Repo is renamed; the deployment is not. |
| Stripe / API keys / quotas / leads | **Freeze** | Monetization scaffolding is orthogonal to a research portfolio project and dilutes the narrative. |

---

## 3. The most important gaps

### GAP-1 — There is no research layer at all. *(Critical)*
No research question, hypotheses, protocol, literature matrix, metric definitions, analysis plan, data dictionary, provenance record, results registry, paper, poster, or deck. **Zero of the ~20 required research deliverables exist.** The `docs/` directory is `.gitignore`d as "Internal / competition materials — never publish," so no research artifact is under version control. This is the whole project, and it is at 0%.

### GAP-2 — The deployed app is not the project. *(Critical)*
Live site title: `SellerFlow — Credit decisions for digital merchants`. It presents **credit limit, interest rate (12.5% p.a.), and PD** — the superseded fixed-rate-lending framing. There is no remittance percentage, no repayment cap, no scenario analysis, no integrity screen anywhere on the deployed page. The last six commits — including the entire RBF rename, the integrity engine, and the real-data validation — **are not deployed.**

Consequence: the README's headline link sends a reviewer to an artifact that contradicts the README's first paragraph. Today, a recruiter clicking that link sees a different product than the one you would describe.

### GAP-3 — There is no fixed-vs-RBF comparison. *(Critical)*
This is the project's central research question, and **no code computes a fixed-payment counterfactual.** `financing_engine.py` models only the RBF arm. H1, H2, and H3 are currently untestable. The single most important thing to build in August is the paired comparison engine.

### GAP-4 — The product cannot ingest a revenue time series. *(High)*
`MerchantSubmission` accepts one `monthly_revenue` scalar and one `revenue_growth` scalar. Volatility, seasonality, and drawdown — **the exact constructs the research question is about** — are structurally uncollectable. `revenue_metrics()` already handles history and is never called with it. Without this, "revenue volatility" research has no product surface.

### GAP-5 — No labeled outcomes, and the roadmap depends on them. *(High, unfixable by August — plan around it)*
`real_world_validation` is `null` and will remain `null`. **Accept this permanently and pivot the research away from default prediction toward repayment mechanics and cash-flow resilience**, exactly as your brief anticipates. This is a scoping decision, not a failure.

### GAP-6 — Documentation drift. *(Medium)*
README says 29 tests; there are 47. README says the local password is `demo2025` and this is committed in plaintext in `start.sh`, `start-dev.sh`, and `main.py`. Live privacy page directs deletion requests to `hello@sellerflow.io` — an address the README implies is not monitored.

---

## 4. Research-integrity risks

These are ranked by how badly each would damage you in a hostile Q&A. **RI-1 is the one that would end a defense.**

### RI-1 — The 0.92 AUC is circular. *(Critical — must be disclosed or removed)*

`generate_data.py` creates the label by writing a weighted formula over the same ten features the model later sees, adding `N(0, 0.08)` noise, and thresholding at 0.475:

```python
risk_score = 0.28*return_rate_norm + 0.22*rating_inv + 0.18*late_ship_norm
           + 0.15*growth_inv + 0.10*tenure_inv + 0.07*turnover_inv
df['defaulted'] = ((risk_score + noise) > 0.475).astype(int)
```

The model's task is to rediscover a formula written 60 lines away in the same repository.

**Measured** (`backend/audit_evidence.py`, reproducible):

```
AUC of the hand-written generating function against its own label : 0.9098
Reported ensemble AUC (train_model.py)                            : 0.9182
```

The generating function is (up to sampling noise) the Bayes-optimal ranker for this data, and it scores essentially what the model scores. **The 0.92 is a measurement of the author's choice of `sigma=0.08`.** Set `sigma=0.02` and it approaches 1.0; set `sigma=0.5` and it collapses toward 0.5. It carries no information about e-commerce sellers, credit risk, or the model's quality.

The README's disclaimer — *"describes how well it separates synthetic-good from synthetic-bad"* — is technically true and insufficient. It implies a *hard* separation task was performed well. The honest statement is: **no separation task was performed at all.** A reviewer who opens `generate_data.py` will see this in thirty seconds, and the gap between "disclosed as synthetic" and "disclosed as circular" is exactly where credibility is lost.

**Required action:** retire 0.92 from every public surface (README, `/api/model/status`, UI, resume, deck). Replace with an explicit statement that the synthetic ensemble is a **structural placeholder with no measured predictive validity**, and that the project's quantitative claims rest on repayment mechanics rather than on default prediction.

### RI-2 — The synthetic population is internally impossible. *(Critical)*

All ten features are drawn as **mutually independent** random variables.

```
max |pairwise correlation| among the 10 features : 0.0448
median  monthly_revenue / (order_volume × AOV)   : 0.98
share of rows outside a [0.55, 1.75] band        : 61.0%
```

Revenue, order volume, and average order value are related by the accounting identity `revenue = orders × AOV`. In the synthetic data this identity is violated in **61% of rows**. No real seller can exist in this distribution. Consequently `feature_importance` (revenue_growth 23%, return_rate 21%, …) describes the generating formula's own weights, **not** anything about sellers — and it must never be presented as a finding.

### RI-3 — The integrity engine rejects its own training population. *(Critical — and it is your best paper finding)*

`integrity_engine.revenue_reconciliation()` flags any submission where claimed revenue diverges from `orders × AOV`. Run it against the data the risk model was fit on:

```
revenue-reconciliation on 1,000 training rows : flag 62.3% · pass 37.7%
```

**The fraud screen would reject 62% of the population the credit model was trained on.** The two engines encode contradictory beliefs about what a seller looks like.

This is currently a bug. **Reframed, it is the strongest honest result in the project**: a concrete, reproducible demonstration that synthetic underwriting data can silently violate the accounting identities that downstream fraud controls depend on. That is a genuine, publishable methodological finding about model risk — and it is *yours*, discovered in your own system. It belongs in the paper's limitations section and in your Q&A prep, where it converts your biggest vulnerability into evidence of exactly the rigor the project claims.

### RI-4 — Methodology validation is real but off-target. *(High)*
`validate_on_real_data.py` is honest, reproducible, and uses genuinely real data (UCI German Credit n=1,000; UCI Taiwan n=30,000). But both are **consumer** credit datasets — individual borrowers, fixed-installment products, 1994 Germany and 2005 Taiwan. Neither contains an e-commerce seller, a revenue share, or a repayment cap. It demonstrates that RF+LR is a working classifier, which was never in doubt. **Keep it as a reproducibility exhibit; do not let it anchor the paper.** State the population mismatch explicitly.

### RI-5 — Live product makes claims the model cannot support. *(High)*
The deployed page states *"Risk priced correctly — our model prices risk from operations, so strong sellers get 12.5% instead of the 40–80% informal market rate."* The 12.5% is a hardcoded constant in `ml_engine.py`, not a priced output. The 40–80% comparison has no cited source. This is an unsourced impact claim on a public page and must be removed or sourced.

### RI-6 — PII collected as part of an underwriting submission. *(Medium)*
`MerchantSubmission` collects `owner_name` and `phone`. They are correctly excluded from `FEATURES` and never scored — but they are stored in the same record, exported in CSV, and the live form presents them inside the credit application flow. Your brief prohibits owner names and phone numbers as underwriting variables. They are not variables here, but their presence is indefensible under scrutiny and they serve no research purpose. **Drop both fields.**

### RI-7 — Shared secret in version control. *(Medium)*
`DASHBOARD_PASSWORD` defaults to `demo2025`, committed in three files. Production overrides it, so exposure is limited — but a "no secrets exposed" checklist item cannot be signed off while a working default password is in the public repo.

### RI-8 — Competition framing embedded in the repo. *(Medium)*
The README contains a full section answering a **GXS Bank problem statement**. This is a different audience with different success criteria (adaptive fraud/credit unification, continuous learning) than a research portfolio project. It pulls the narrative toward capabilities you have explicitly not built. **Move it to a separate branch or appendix.**

---

## 5. Proposed final scope

### 5.1 Confirmed research framing

> **Revenue-Contingent Financing Under Volatile Sales: A Model-Based and Simulation Study Motivated by Vietnamese E-commerce Sellers**
>
> *(title as of 2026-08-04; see D-020. Earlier working titles are superseded.)*

**Primary question (revised — one word changed, and it matters):**
> Compared with a principal- and cost-matched fixed-payment structure, **under what revenue conditions** does revenue-based financing reduce cash-flow stress for small online sellers, and what trade-offs does it create for the financing provider?

I recommend **"Simulation-Based"** in the title rather than "Evidence-Based." You will not have observed seller repayment data by August 31. A title that announces its own method is unattackable; a title that overstates its evidence invites the first hostile question. The evidence hierarchy still holds — Layer A public evidence motivates the problem, calibrated simulation answers the mechanical question.

### 5.2 Hypothesis disposition after audit

| ID | Status | Note |
|---|---|---|
| H1 — lower payment burden in low-revenue months | **Testable** | Core deliverable. Note: partly true *by construction*; the research contribution is quantifying magnitude and cost, not discovering direction. Say so first, before a reviewer does. |
| H2 — fewer distress months under shocks | **Testable** | Requires pre-registered distress definition + threshold sensitivity. |
| H3 — flexibility costs duration/recovery variance | **Testable** | The provider-side finding. Likely the most interesting result. |
| H4 — stability/turnover/returns beat revenue size as affordability signals | **Reframe** | Untestable as a *predictive* claim without labels. Reframe as: which signals best predict **affordability under simulated stress** — a mechanical, honest question. |
| H5 — data quality + diversion are material risks | **Testable, and partly already demonstrated** | RI-3 is your first result. |

### 5.3 In scope for August

**Research:** protocol · literature matrix (12–18 sources, Layer A) · pre-registered analysis plan with mathematical metric definitions · calibrated revenue-path generator with documented provenance · fixed-vs-RBF paired comparison · stress scenarios · sensitivity + bootstrap · 8–12pp paper · exec summary · poster.

**Product:** revenue-history input · fixed-vs-RBF comparison view · stress-test panel · explainability panel · methodology page · **results page rendered from the analysis output file, not hand-typed** · model card · privacy notice · README rewrite · redeploy.

**Presentation:** 10 slides · 30s / 2–3min / 5–7min pitches · demo script · Q&A · resume bullets · abstract.

### 5.4 Frozen (explicitly not August work)

Stripe/payments · API keys, quotas, plans, pricing page · leads capture and email alerts · multi-tenancy · PDF export · document upload · GXS competition framing · supervised fraud model · any retraining of the synthetic ensemble · domain rename.

**On the synthetic ensemble:** do not retrain it, do not improve it, do not delete it. Demote it to a clearly-labeled structural placeholder and move the project's quantitative weight onto the deterministic comparison engine — which needs no labels, has no circularity, and can be verified line by line. This is the single most important scoping decision in the project.

---

## 6. Prioritized execution plan

### Immediate — Aug 3–4 (Phase 0 completion)

| # | Action | Why |
|---|---|---|
| P0-1 | Redeploy Railway from `bff1477`; verify the live page says RBF and returns a `financing` object | Kills GAP-2. Highest ratio of credibility gained to effort spent in the entire project. |
| P0-2 | Retire 0.92 from README, `/api/model/status`, and UI | Kills RI-1 before anything is built on top of it. |
| P0-3 | Remove the "12.5% vs 40–80%" claim | Kills RI-5. |
| P0-4 | Drop `owner_name` / `phone` from model, form, DB writes, CSV | Kills RI-6. |
| P0-5 | Un-ignore `docs/`, create `research/` under version control | Research work must be traceable from day one. |
| P0-6 | Commit `audit_evidence.py` as `research/analysis/00_audit_evidence.py` | Makes RI-1/2/3 reproducible by a third party — this is itself a research artifact. |
| P0-7 | Fix README test count 29 → 47; remove `demo2025` default | Kills GAP-6, RI-7. |

### Aug 5–8 (Phase 1) — Research design
Protocol · hypotheses · **mathematical metric definitions written before any result is computed** · literature matrix · pre-registered analysis plan · human-subjects determination.

**Non-negotiable ordering:** the distress-month definition and all metric formulas are frozen in a committed file **before** the comparison engine runs once. That commit timestamp is your defense against "you tuned the threshold to get the result."

### Aug 9–15 (Phase 2) — Evidence + data
Layer A sources → literature matrix · calibrated revenue-path generator (documented, seeded, provenance-tagged) · data dictionary · provenance record · scenario library.

### Aug 16–22 (Phase 3) — Analysis + integration
`comparison_engine.py` (fixed arm + RBF arm + guardrailed RBF arm, principal/cost-matched) · paired scenario runs · bootstrap CIs · sensitivity across distress thresholds and revenue-share parameters · figures · then wire into the app.

### Aug 23–27 (Phase 4) — Write
Paper · exec summary · poster · deck · README/model card · pitches · demo script · Q&A.

### Aug 28–31 (Phase 5) — Red-team + ship
Every number traced · every citation opened · every figure regenerated from committed code · app tested · deploy verified · mock defense · release tag.

### Critical path
```
P0-1 redeploy ─┐
P0-2 retire 0.92 ─┼─► metric definitions ─► comparison engine ─► results ─► paper ─► deck
GAP-4 history input ─┘                                    └─► product integration ─┘
```
**The comparison engine is the bottleneck.** Everything downstream — findings, paper, slides, product differentiation — waits on it. If August compresses, cut poster and pitch variants before cutting comparison-engine rigor.

---

## 7. Questions

Five, all genuinely blocking. Assumptions I will proceed on if you don't answer are stated.

**Q1 — Geographic scope.** Vietnam-specific (Shopee/TikTok Shop/Lazada, VND, CIC-gap framing), Southeast Asia, or platform-agnostic?
*Default if unanswered:* Vietnam-focused framing, with generalizability limits stated explicitly.

**Q2 — Where are the Excel model and the Research Scholars materials?** Neither is in the repo (`docs/` is git-ignored and absent from the clone; the knowledge folder contains only metadata). If the Excel model contains calibration assumptions or the Scholars work contains a literature review, both are directly reusable and I should not rebuild them.
*Default if unanswered:* build the comparison model from scratch in Python; treat the Excel work as unavailable.

**Q3 — Real seller data: any prospect at all?** Even 3–5 sellers' anonymized 12-month revenue histories would move Layer C from "calibrated simulation" to "simulation calibrated against observed data" — a materially stronger claim.
*Default if unanswered:* pure simulation with parameters calibrated to cited public statistics and full sensitivity analysis.

**Q4 — Human subjects.** Are you affiliated with an institution whose IRB would cover seller interviews, and do you want Layer B in scope? Layer B is the most schedule-risky item on the plan.
*Default if unanswered:* **drop Layer B.** Run a Layer A + Layer C project and state the absence of primary seller evidence as an explicit limitation. This is the safer August.

**Q5 — Audience priority.** If faculty/research reviewers rank first, I bias toward the paper and methodological rigor. If recruiters rank first, I bias toward the deployed product and deck. Both get built; the ranking decides where the last week goes.
*Default if unanswered:* recruiters first, faculty close second — product polish and deck weighted slightly over paper length.

---

## 8. Evidence appendix

All findings in §4 are reproducible:

```bash
git clone https://github.com/hoangle0919/sellerflow && cd sellerflow/backend
pip install -r requirements.txt
python3 train_model.py          # → Ensemble AUC 0.9182
python3 -m pytest tests/ -q     # → 47 passed
python3 audit_evidence.py       # → RI-1, RI-2, RI-3 measurements
```

`audit_evidence.py` output, 2026-08-03:

```
A. CIRCULARITY OF THE SYNTHETIC BENCHMARK
   label prevalence                       : 6.20%
   AUC of the hand-written generating fn  : 0.9098
   reported model AUC (train_model.py)    : 0.9182

B. THE SYNTHETIC DATA IS INTERNALLY IMPOSSIBLE
   max |pairwise corr| among 10 features  : 0.0448   (independent draws)
   median revenue / (orders x AOV)        : 0.98
   share with ratio outside [0.55,1.75]   : 61.0%

C. THE INTEGRITY ENGINE REJECTS ITS OWN TRAINING DATA
   revenue-reconciliation on 1,000 training rows: {'flag': 0.623, 'pass': 0.377}
```

Live-site staleness, verified 2026-08-03: page title `SellerFlow — Credit decisions for digital merchants`; body presents credit limit / 12.5% p.a. / PD; zero occurrences of remittance, repayment cap, scenario, or integrity. Repo `frontend/index.html` @ `bff1477`: zero occurrences of "SellerFlow", 17 of "RBF", 12 of "remittance", 18 of "scenario", 11 of "integrity".
