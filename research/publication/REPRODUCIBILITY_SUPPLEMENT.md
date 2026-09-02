# Reproducibility Supplement

**Companion to:** *Revenue-Contingent Financing under Volatile Sales: A Paired Simulation of Seller Burden and Provider Recovery* (English reader edition) and *Tài trợ dựa trên doanh thu trong điều kiện doanh số biến động* (Vietnamese reader edition).

**Le Huu Hoang** · Independent research · August 2026
`lehuuhoang1909@gmail.com` · https://github.com/hoangle0919/sellerflow

---

## 0. What this document is, and why it is separate

The reader editions carry the argument. This supplement carries the proof that the argument's numbers are what the code produced.

They are deliberately separate. An earlier version of this project put the full audit apparatus — checksums, JSON paths, verification commands, decision-log pointers — inside the paper itself. The result read like an engineering audit rather than a research argument, and the qualifications that matter most to a reader were buried among digests that matter only to a verifier. Splitting them lets each document address one reader.

**This supplement does not independently define or revise findings.** It reports identities, paths and procedures for figures defined elsewhere. If it and a reader edition ever disagree about a magnitude, the registered artifact in §2 settles it, and the disagreement is a defect to be logged.

---

## 1. Document set and identities

| Document | Role | Pages | SHA-256 |
|---|---|---|---|
| `reader_editions/papers/Revenue_Contingent_Financing_Professional_Paper.pdf` | **Current reader edition, English** | 14 (Letter) | `f3a0aec26a1437620909ab8a13402525d5939bd087f19ad2087e830cb2a3aa78` |
| `reader_editions/papers/Tai_Tro_Hoan_Tra_Theo_Doanh_Thu_Bai_Nghien_Cuu.pdf` | **Current reader edition, Vietnamese** | 14 (Letter) | `1f36142e33a3db7baf635e556c0c470a91b656bf47517129cd572787d4b41c5c` |
| `MANUSCRIPT.pdf` | **Historical technical manuscript** — superseded as the public paper, retained for provenance | 19 (A4) | `8d4d59df6ab5f7a7cd14111f18f97641bba35d6be05705a041d0df30a7683a56` |
| `TONG_QUAN_VI.pdf` | **Superseded Vietnamese overview** — a 5-page summary, not the scholarly edition | 5 (Letter) | `10a4569bd4977bbcd6f20bd8b5c1f339299a3b6511776babb718e03ca9b4a212` |

The Vietnamese reader edition is an **independently written Vietnamese scholarly paper**, not a sentence-by-sentence translation of the English. The two are parallel in status and in claim boundaries; they are not mechanically identical in prose.

The historical documents are retained because figures were published from them. Deleting them would break the ability to check what was said and when. They are never cited as current.

---

## 2. Registered result artifacts

Every **registered simulation result** in either reader edition derives from one of these five files. Three categories are **not** covered by this table: the propositions, which are derivation-backed; the cited literature, which is neither; and **Figure 1, which is an explicitly schematic illustrative series embedded in each builder and generated from no artifact** (§3.2).

### 2.1 Current generation (produced under amendment A-9)

| Artifact | SHA-256 |
|---|---|
| `research/results/baseline_v3_canonical.json` | `363729016298b3d7307ec066c8df37c60e1c9aa2582db2c058c5cc74df894d55` |
| `research/results/baseline_equalcost_v2_canonical.json` | `b3ebfe6a5a7e7f48726d7e501295b02f84258a3fe9ee4e048875125b1270e0ee` |
| `research/results/baseline_closure_v2_canonical.json` | `21b8e207ff2db9ac866b8cb2bab47c8c2e434d2bff03d802eb6f53a66fdcea4b` |
| `research/results/baseline_closure_equalcost_v2_canonical.json` | `e1e6d81bbeeb60f0e923c27a8df44d26674f4b8ad788c6c9796c17ef40622665` |
| `research/results/validation_v2_canonical.json` | `7d9b9d0f9b0fd0fea7011625026a7a5da28c1d4fab009e9a2bf2bd7639af52cc` |

### 2.2 Superseded generation (pre-A-9), retained byte-for-byte

| Artifact | SHA-256 |
|---|---|
| `research/results/baseline_v2_canonical.json` | `264d319be6854533b4a51a7114c34dbffb0728d9ed3bfd50973b6ab4ac5a7849` |
| `research/results/baseline_equalcost_v1_canonical.json` | `6f9c71b111400aea1b2ea5c06527404f849fa390de0eef47e22b75a552da68e7` |
| `research/results/baseline_closure_v1_canonical.json` | `0fe503d7f96b4c21d68b2fb812e0e9645ac21bdb6308208be4182cdef6179470` |
| `research/results/baseline_closure_equalcost_v1_canonical.json` | `49b6f8ef19c81eebe1288d0d090c858a64b30f35cd5263afd6f4a971696b15f9` |
| `research/results/validation_v1_canonical.json` | `f89fd2baab7f5628f9aed7e7a6be7ae40e0e72919b0f9f41e20875946c67ddb4` |

**Why both generations exist.** Amendment A-9 corrected the internal-rate-of-return calculation: the solver was fed a filtered payment vector rather than the complete monthly vector including internal zeros, the search domain excluded rates below zero, and completion was conflated with the existence of a rate. Every figure published before 2026-08-20 was computed from the superseded files. They are retained so the record of what was published stays independently checkable. `backend/tests/test_validation_artifact.py` asserts their integrity on every run.

The digests are of the **canonical** form, which excludes the non-deterministic run date. That field is preserved in a `*_provenance.json` sidecar beside each artifact, together with the interpreter and library versions, the wall-clock time and the source commit.

---

## 3. Claim-to-artifact map

Ledger identifiers resolve in `research/CLAIM_LEDGER.md`; literature identifiers in `research/publication/LITERATURE_MATRIX.md`; propositions in `research/DERIVATIONS.md`.

### 3.1 Headline magnitudes

| Figure | Value | Artifact → JSON path | Ledger |
|---|---|---|---|
| High-burden months removed, severe downturn, `f = 1.20` | 6.85 | `baseline_v3` → `/tradeoff/severe_downturn/d_n_hpb_015/mean` (the paired FIX-A − RBF difference, Monte Carlo interval [6.802, 6.898], n = 500). Equivalently from both arms: `/scenarios/severe_downturn/FIX-A/n_high_burden/0.15` = 6.85 minus `…/RBF/n_high_burden/0.15` = 0.0 | S-1 |
| RBF recovery by month 12, severe downturn | 65.46% | `baseline_v3` → `/scenarios/severe_downturn/RBF/recovery_ratio/12` | S-1 |
| Matched fixed recovery by month 12 | 92.31% | `baseline_v3` → `/scenarios/severe_downturn/FIX-A/recovery_ratio/12` | S-1 |
| RBF mean duration, severe downturn | 18.718 mo | `baseline_v3` → `/scenarios/severe_downturn/RBF/duration_mean` | S-1 |
| Reference-path cost-matched factor | `f* = 1.0945` | `validation_v2` → `/pricing/equal_cost/f_star` | P-1 |
| Its reference-path APR | 19.537656% | `validation_v2` → `/pricing/equal_cost/apr` | P-1 |
| Benchmark B APR | 19.561817% | `validation_v2` → `/pricing/benchmark_b_apr` | P-1 |
| APR at `f = 1.20` | 39.90% | `validation_v2` → `/pricing/sweep/1.2/apr` | P-2 |
| Incomplete recovery, closure month 7 | 100.0% at **both** factors | `baseline_closure_v2` and `baseline_closure_equalcost_v2` → `/scenarios/closure_m7/RBF/incomplete_recovery_rate` | S-3, S-4 |
| Incomplete recovery, closure month 13 | 76.2% → 7.6% | same, `/scenarios/closure_m13/RBF/incomplete_recovery_rate` | S-3, S-4 |
| Incomplete recovery, temporary closure | 2.0% → 0.0% | same, `/scenarios/temp_closure/RBF/incomplete_recovery_rate` | S-3, S-4 |
| Mean repaid, closure month 7 | 98.35m VND | `baseline_closure_v2` → `/scenarios/closure_m7/RBF/total_repaid_mean` | I-3 |
| Convergence, 5,000 → 10,000 paths | 0.0027 mo, 0.042 pp | `validation_v2` → `/convergence` | P-3 |

### 3.2 Figures in the reader editions

Figure 1 is an **explicitly illustrative** series embedded in each builder; it is not generated from a registered artifact and is labelled as such in the papers. Figures 2–5 are generated at build time from the four baseline artifacts listed in §4.2. Prose, equations, tables, captions, references and disclosures live in the HTML sources and are governed by the claim ledger rather than generated from JSON.

### 3.3 Conditioning that must travel with the rate and duration statistics

Amendment A-9 separated two events that had been treated as one:

- **`duration_mean`** averages paths that **completed** within the 24-month window.
- **`apr_mean`** averages paths where an internal rate of return **exists** — a different and usually larger set. A path that stopped short of the contractual target but made payments has a well-defined rate over the **observed window**; that is not a lifetime return.

At `closure_m13` the two come apart sharply: **100%** of paths are rate-defined while only **23.8%** complete at `f = 1.20`. At `closure_m7` the contract completes on **no** path and still has a defined mean rate of **−86.51%**. Any surface reporting either statistic must name its denominator. Neither conditional mean is automatically a portfolio-wide outcome.

---

## 4. Reproduction

### 4.1 Regenerate and verify the research artifacts

```bash
python3 research/verify_reproduction.py
```

The script regenerates all five artifacts into a scratch tree and reports **byte equality and numeric-leaf equality in separate columns**. It never rewrites a registered file. Expected on Linux/aarch64 CPython 3.10.12: exit 0, 5/5 byte-identical, 5/5 numerically equal at relative tolerance `1e-9`.

> ### ⚠️ Maintainer-only, and destructive to the working tree
>
> The individual generators below **overwrite tracked raw, canonical and
> provenance files in `research/results/`**. They are not part of normal
> verification and a reader checking this work should not run them — use
> `verify_reproduction.py` above, which regenerates into a **scratch tree** and
> never touches a registered file.
>
> Some of them also print commentary that predates later corrections; the
> pricing section of `run_validation.py`, for example, still says an exact APR
> match is unattainable, which **D-056 withdrew**. The generators are not edited
> for this, because their bytes are inside the artifacts' generator
> fingerprints, and editing one would force a re-registration to fix a sentence.
>
> ```bash
> cd research
> python3 run_baseline.py                 # baseline_v3
> python3 run_equal_cost_baseline.py      # baseline_equalcost_v2
> python3 run_closure_baseline.py         # both closure artifacts
> python3 run_validation.py 1             # convergence ladder
> python3 run_validation.py 2             # pricing sweep and f*
> python3 run_validation.py 4             # incomplete-recovery boundary
> python3 run_validation.py 5             # RBF-G breakpoint
> python3 run_validation.py 6             # revenue-definition sensitivity
> python3 canonicalize_validation.py --write
> ```

> `research/conv_step.py` is **retired and fails closed**. It wrote into the now-frozen `validation_v1.json`. Section 1 of `run_validation.py` computes the same convergence ladder into the current raw file. See D-052.

### 4.2 Rebuild the reader editions

```bash
python3 -m venv .venv-publication
source .venv-publication/bin/activate
python -m pip install -r research/publication/reader_editions/requirements-publication.txt

# Build into a scratch directory. Without RBF_PAPER_OUTPUT_DIR the builders
# write beside themselves, NOT into the registered reader_editions/papers/.
export RBF_PAPER_OUTPUT_DIR="$(mktemp -d)"
python research/publication/reader_editions/build_professional_paper.py
python research/publication/reader_editions/build_professional_paper_vi.py
echo "built into $RBF_PAPER_OUTPUT_DIR"
```

**A rebuild never replaces a registered PDF automatically.** Compare the fresh
output against the registered file — extracted text first, then rendered pages —
and only then decide whether a replacement is warranted. See the byte-identity
caveat below.

Both builders **verify four input checksums before rendering** and abort on any mismatch — `baseline_v3`, `baseline_equalcost_v2`, `baseline_closure_v2` and `baseline_closure_equalcost_v2`, at the digests in §2.1. This has been confirmed by negative test: mutating a single field of an input artifact causes the build to fail with a checksum mismatch rather than silently rendering a paper from altered data.

Overrides: `CHROME_BIN`, `RBF_REPO_ROOT`, `RBF_RESULTS_DIR`, `RBF_PAPER_WORK_DIR`, `RBF_PAPER_OUTPUT_DIR`, and `RBF_HTML_ONLY=1` to produce self-contained HTML without invoking Chrome. No network access is required.

**A rebuild is not byte-identical to a delivered PDF.** Matplotlib SVG metadata and Chrome PDF timestamps vary between runs. Accept a rebuild only after comparing extracted text and inspecting rendered pages; do not replace a registered PDF merely because a build completed.

### 4.3 Test suites

```bash
python3 -m pytest backend/tests -q      # 502 passed, 10 skipped
cd research && python3 -m pytest -q     # 643 passed
```

**1,145 non-browser tests.** Nine Playwright browser checks are excluded from that total; they executed and passed 9/9 in 23.55 seconds on macOS 26.0 arm64, Python 3.11.5 and Playwright 1.62.0 with Chromium, against a local server at commit `c8261c6`. When Chromium is unavailable the checks skip; a skip is never counted as a pass.

Of the 10 backend skips, 9 are the browser module and 1 is a two-scoring-path cohort comparison that requires an ensemble artifact a clean checkout does not carry.

---

## 5. Tested environments and the reproducibility qualification

**Numeric reproducibility holds everywhere tested. Byte reproducibility does not, and is not claimed across platforms.**

| Artifact | Bytes, Linux/aarch64 CPython 3.10.12 | Bytes, macOS 26.0 arm64 CPython 3.11.5 | Worst relative difference | Numeric leaves |
|---|---|---|---|---|
| `baseline_v3` | identical | 11 last-bit leaves differ | `5.351e-15` | equal |
| `baseline_equalcost_v2` | identical | 3 last-bit leaves differ | `1.532e-16` | equal |
| `baseline_closure_v2` | identical | identical | `0` | equal |
| `baseline_closure_equalcost_v2` | identical | identical | `0` | equal |
| `validation_v2` | identical | identical | `0` | equal |

**Totals:** Linux 5/5 byte-identical; macOS **3/5**; **5/5 numerically equal** at relative tolerance `1e-9` in both.

The macOS column is an **independent audit run** of `verify_reproduction.py` against the current artifacts on a platform this project does not itself have access to. It is not a self-measurement. The column previously read "not measured", and before that carried counts (9 and 2) inherited from the superseded generation — which were wrong for these files **in both rows**. That is the case for removing an unverified number rather than letting it ride.

**How to reproduce the macOS column.** On a macOS host with the repository checked out:

```bash
python3 research/verify_reproduction.py
```

Read the per-artifact `bytes` and `numeric` columns it prints. That is the procedure that produced the figures above. **`./verify_native_macos.sh` does not reproduce this table** — it installs the pinned dependency set on an external volume and runs the product test suite, which is a different check. An earlier version of this section named it here in error.

Publication build environment: CPython 3.11.5, NumPy 2.2.6, Matplotlib 3.10.3, Google Chrome 152 / Skia PDF m152, Times New Roman for text, DejaVu Serif for charts (Matplotlib converts chart glyphs to SVG paths), Poppler for acceptance checks.

IEEE-754 last-bit divergence between CPython builds is expected. Presenting it as a research defect would be as wrong as hiding it.

---

## 6. Correction history

This project retracted several of its own claims. Each retraction is recorded next to the evidence that overturned it. The full record is `research/DECISION_LOG.md` (D-001 … D-055); the pointers below are the ones a verifier is most likely to need.

| Withdrawn claim | Why | Entry |
|---|---|---|
| "RBF costs ~2.3× the interest of a conventional loan" | Conflates price with structure. The contractual **target** `A·f` is proportional to `f`; realised repayment equals it only on completion | D-015, P6 |
| "0.92 AUC" or any predictive-skill figure | Circular: the training label was generated by a hand-written formula over the same features the model consumes | D-026 |
| "RBF-G is bit-identical to RBF" | False — 6 of 10 scenarios differ. Only the narrower null survives: the hardship **floor** never activates | D-040, R-013 |
| Unqualified byte-for-byte reproducibility | Rested on a check that re-hashed the committed file instead of regenerating it — a check that could not fail | D-041 |
| "Revenue-based repayment extends the term instead of defaulting" | Asserts default prevention. `closure_m7` is 100% incomplete at **both** cap factors | D-037, S-3 |
| "Equal cost" as a name for `f*` | The factor is the nearest point on a swept grid, not an exact match; a residual of ≈0.02416 pp remains | D-037, D-052 |
| Effective APR conditioned on completion | Superseded by A-9. Completion and the existence of a rate are separate events | D-049, D-050 |
| "The numbers shown are identical either way" (scoring paths) | False. The scorer assigns the risk tier and every term keys off it; the paths disagree for a majority of profiles | D-053 |
| A 5.77% cap-overshoot rate | Author error — computed `duration × remittance` while ignoring the clipped final payment. Actual: 0 breaches in 6,794 structures | D-029 |

**Specification amendments.** `research/METHODOLOGY_SPEC.md` v1.0 was frozen before any outcome analysis; §16 logs amendments A-1 … A-9. A-9 is the one that moved registered numbers, and only in the rate layer — burden, recovery, duration, settlement arithmetic, scenario inputs and seeds were verified unchanged leaf-by-leaf.

**Recent closure entries.** D-049/D-050 (A-9 and the artifact migration), D-051 (solver unification, genuine reproduction, lineage), D-052 (Lab provenance and the retired convergence script), D-053/D-054 (browser gate executed, then re-executed on the merged tip), D-055 (release-metadata statements that outlived their facts).

---

## 7. What the audit trail does not cover

Stated because a thorough verification record can create a false impression of scope.

- **No observed seller or merchant revenue, repayment, or default outcomes enter this study.** Reproducibility means the simulation regenerates. It says nothing about whether the simulation resembles the world.

  The narrower wording is deliberate. The repository **does** contain real data — `backend/validation_data/taiwan.csv`, the UCI default-of-credit-card-clients dataset, 30,000 borrower records — used by `backend/validate_on_real_data.py` for the **separate, unvalidated scoring demonstration**. It feeds no financing result, no proposition and no registered artifact. An earlier version of this section said "no observed data exist anywhere in this project", which was false as written.
- **The propositions are proved, not measured.** Their limitation is different in kind: they describe a contract, and a contract is not a market.
- **The literature is neither.** 44 verified sources with 6 documented evidence gaps; the checksum table does not cover cited facts.
- **The underwriting ensemble is unvalidated** and plays no part in any research finding. Its benchmark was withdrawn as circular.
- **Test counts measure the tests that exist,** not the absence of defects in what nobody thought to test. Several defects in this project were found by adversarial review after a fully green suite — including one held in place *by* a passing test that pinned the wrong assertion.

---

*Governing documents: `research/METHODOLOGY_SPEC.md` (specification), `research/CLAIM_LEDGER.md` (what may be claimed), `research/DERIVATIONS.md` (propositions), `research/RESULTS_REGISTRY.md` (registered results), `research/DECISION_LOG.md` (every decision and retraction), `research/publication/LITERATURE_MATRIX.md` (external evidence).*
