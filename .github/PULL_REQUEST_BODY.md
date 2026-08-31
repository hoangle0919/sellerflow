Publication package for the revenue-contingent financing study, plus the runtime-disclosure corrections found while preparing it. Branch `publication-final`.

*No base commit is named here.* This branch has merged `main` four times during its life, so any base hash written down goes stale at the next merge — `f652b94` sat in this line for weeks after it stopped being the merge base. GitHub computes and displays the real one; a hand-maintained copy can only disagree with it.

**This PR changes one result layer, deliberately, and preserves the old one.** An independent audit demonstrated three implementation defects in the effective-rate calculation. Spec amendment **A-9** corrects them; five new canonical artifacts are registered and the five superseded ones are preserved byte-for-byte as the record of what was published. Burden, recovery, duration, settlement arithmetic, scenario inputs and seeds are unchanged — verified leaf-by-leaf. Everything else in this PR is documentation catching up to what the code does.

---

## 1. Publication deliverables

| Artifact | State |
|---|---|
| `research/publication/MANUSCRIPT.md` / `.pdf` | ~9,600 words, 15 sections plus data-availability, declarations and Appendix A. PDF is 19 pages, built by `build_pdf.sh`, gated by `check_pdf_bounds.py` at zero text outside the media box |
| `research/publication/RBF_DECK.pptx` | 13 slides with speaker notes; `[Sources]` blocks on the slides carrying externally sourced claims. Built by `build_deck.js` |
| `research/publication/LITERATURE_MATRIX.md` | 44 verified sources, 6 evidence gaps stated explicitly |
| `research/publication/PAPER_OUTLINE.md` | Every figure bound to a ledger ID and artifact path |
| `research/publication/CAREER_PACKAGE.md` | Résumé, LinkedIn, portfolio and interview text, with a "what must never be said" table |

The PDF build is three-stage because two defects could not be fixed from the markdown: reference URLs were plain text that TeX cannot break, and long artifact paths and SHA-256 digests were being clipped at the page edge — including all five registered checksums. `fix_tex.py` inserts break opportunities that emit no glyph, so extracted text is unchanged, and fills the PDF Title/Author properties pandoc leaves empty. `check_pdf_bounds.py` (requires PyMuPDF) measures the rendered result rather than trusting an overfull-hbox warning, which does not say whether the overflow was cosmetic or truncated a checksum.

## 2. Runtime disclosure — the substantive fix

A previous commit on `main` stated that when scoring falls back from the ensemble to the heuristic, "the numbers shown are identical either way". **That is false end to end**, and the same claim or an ambiguous variant of it was live in five places.

```
scoring_path → pd_score → risk tier → advance %, remittance %,
                                      cap factor, eligibility
```

`ml_engine.score()` computes `pd_score` differently on each path and thresholds it into Low / Medium / High Risk; `financing_engine.RATES` keys every term off that tier. At 200M monthly revenue the repayment cap is **414,000,000 at Low Risk against 249,600,000 at Medium**, and High Risk zeroes the advance, remittance rate and cap, so no offer appears at all.

Corrected in `README.md`, `frontend/index.html`, `backend/ml_engine.py`, `backend/ENVIRONMENT.md`, `verify_native_macos.sh` (which *generated* the claim into every verification report) and this file. The agreed wording throughout: **the financing formulas are deterministic once a risk tier is supplied; the active scoring path can change the assigned tier and therefore the advance, remittance rate, cap factor, repayment amounts and eligibility.**

**Observability.** `railway.toml` previously ran `python train_model.py --skip-if-exists 2>/dev/null; python -m uvicorn ...`. The redirect discarded the only evidence of why training failed and the bare `;` started the service regardless, so entering the fallback was silent and indistinguishable from success. `backend/start_railway.sh` keeps the fallback — it is supported and documented — but never discards stderr, logs the failure and its consequence, and continues deliberately. `/api/health` now exposes `sklearn_runtime` alongside `scoring_path`; the startup message previously told operators to read a field that did not exist. The landing page reads the active path from `/api/health` and **fails closed**: unreachable means "ACTIVE SCORER — UNKNOWN", never "ensemble".

**The underlying failure is now diagnosed, and the candidate offered here was wrong.** This paragraph previously proposed that scikit-learn was absent from the production image, so the service booted and only *training* failed. Deploy logs disprove it: training **succeeded** and wrote the artifact. The load discarded it. `ml_engine` wrapped the load in `warnings.simplefilter("error")`, which promoted a benign NumPy `DeprecationWarning` raised inside a dependency into an exception, so a usable model was thrown away and scoring fell back to the heuristic. `00f6b37` narrows the filter to `InconsistentVersionWarning` — the only warning that signals a real version hazard.

This matters beyond the bug. That same commit flipped production from heuristic to ensemble, and the two paths assign different risk tiers for a majority of profiles, so it **changed live assessment outcomes** rather than being the neutral repair it was described as. The defect and the outcome change are one event seen from two sides.

Worth recording how the wrong candidate survived: `00f6b37` was already in this branch's history, and its commit message — *"Stop discarding a usable model over a dependency's deprecation"* — states the answer outright. It was written up as undiagnosed because nobody re-read it.

## 3. Claim families swept repo-wide

Three families were corrected across every tracked surface rather than at the reported instance, because the recurring failure in this project has been fixing the instance and missing the family:

- **Recovery ordering.** Universal formulations contradicted P4, which makes the ordering conditional on realised mean eligible base against `B* = P/r`. Both directions occur in the registered scenarios: recovery lags in the severe downturn and leads at exactly baseline revenue. Scenario-specific statements are retained where the scenario is named.
- **Cost proportional to `f`.** Only the contractual repayment **target** `A·f` is proportional to `f`; realised repayment equals that target only upon completion.
- **Time-sensitive negatives.** "Has never received an external submission" expires the moment anyone visits the site. Replaced with the dated form: *as of August 2026, no external merchant data were used in this study; the public deployment is a demonstration, not a lending service.*

## 4. Registered artifacts and research integrity

- **All reported simulated magnitudes are simulation output under modelled assumptions.** No observed seller revenue, repayment or default outcome exists in this project. The seven propositions are **derivation-backed**, not simulation output, and the cited literature is neither — saying "all quantitative output" swept proofs into a category that under-claims them.
- The underwriting ensemble is a **secondary, explicitly unvalidated component**. Its 0.92 AUC benchmark was withdrawn as circular (D-026): the training label was generated by a hand-written formula over the same features the model consumes. `GET /api/model/status` reports `auc: null` with `validation_status: "withdrawn"`.
- **Intervals are Monte Carlo intervals over simulated paths** — they measure whether enough paths were run, not population uncertainty about real sellers.
- **No contract parameter is externally sourced.** All are illustrative or derived, with sensitivity analysis rather than claimed calibration. The 18% amortizing reference is an assumption of this project, not a market rate.
- **Reproducibility, at the strength the measurement supports.** All five artifacts reproduce numerically at published precision on every platform tested — **5/5 numerically equal** at relative tolerance `1e-9`. Byte equality is **platform-dependent and not claimed across platforms**: 5/5 byte-identical on Linux/aarch64 CPython 3.10.12, and **3/5** on macOS 26.0 arm64 / CPython 3.11.5 / NumPy 2.2.6, where `baseline_v3` differs in 11 last-bit leaves (worst relative difference `5.351e-15`) and `baseline_equalcost_v2` in 3 (`1.532e-16`). The macOS figures are from an **independent audit run** of `verify_reproduction.py` against this branch's HEAD, not from this environment, which has no macOS host. They replace a "not measured" placeholder, which in turn replaced counts (9 and 2) inherited from the superseded generation — those counts were wrong for these files in both rows, which is why they were removed rather than carried. An earlier unqualified byte-identity claim rested on a step that re-hashed the committed file instead of regenerating it, and is withdrawn.
- **`validation_v2` is canonicalized** (D-038, regenerated under A-9) — SHA-256 `7d9b9d0f…`. Its predecessor `validation_v1` is retained unchanged.
- **The RBF-G guardrail null is narrow.** The hardship *floor* never activates — 0 of 36,000 month-observations, because the floor multiplier sits below the hardship threshold. The **ceiling does bind**: 6,009 of 36,000 in the breakpoint scan, changing results in 6 of 10 baseline scenarios. The earlier whole-arm null (N-2) is superseded; only N-2′ survives.
- **The Simulation Lab is shipped**, not future work — `frontend/lab.html` + `backend/lab.py` render every figure from the canonical artifacts, with no financial arithmetic in the frontend.

## 5. Tests

**1,145 non-browser tests pass: 502 backend and 643 simulation.** The nine Playwright browser checks are excluded from that total. They executed and passed 9/9 in 23.55 seconds on macOS 26.0 arm64, Python 3.11.5 and Playwright 1.62.0 with Chromium, against a local server at commit `c8261c6`. When Chromium is unavailable, the checks skip; a skip is never counted as a pass.

## 6. Decision log

`D-047` records the scoring-path disclosure and the three-family sweep; `D-048` the publication-integrity reconciliation. `D-049` and `D-050` cover spec amendment **A-9** — the corrected IRR definition, domain and conditioning — and the controlled migration to the five current artifacts. `D-051` and `D-052` close the convergence work: one IRR solver across the product and research layers, a reproduction verifier that genuinely regenerates the validation battery, artifact-lineage drift, and the Lab's pricing provenance. `D-053` and `D-054` record the browser gate executing — first at `dcbfc3b` with the carry-forward argued, then directly on the merged tip. `D-055` records two release-metadata statements that outlived their facts. Dated records are not rewritten: earlier decision entries keep their contemporaneous counts, `CORRECTED_CLAIMS.md` is marked as a 2026-08-03 snapshot with pointers to current state, and `evidence/2026-08-07-native-macos-verification.md` keeps its incorrect closing note under a dated addendum — an evidence record edited after the fact cannot be relied on.

---

**Review focus.** §2 is the one that matters operationally. The rest is documentation catching up to what the code already did.
