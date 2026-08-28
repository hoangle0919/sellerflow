# Career Package — RBF / Revenue-Contingent Financing Study

**Purpose.** Résumé, LinkedIn and portfolio text for this project, plus interview preparation. Every claim below is traceable to `research/CLAIM_LEDGER.md`, a canonical artifact, or the decision log.

**The rule that governs this file.** A CV is where research overclaiming usually happens, because nobody audits a résumé bullet. So the same constraints apply here as in the paper:

- **No predictive-validity claim.** The model is a demonstration trained on synthetic data with a circular label.
- **No production or lending claim.** There is a live *demonstration* deployment at sellerflow-production.up.railway.app. It holds no capital and makes no offers. **As of August 2026, no external merchant data were used in this study; the public deployment is a demonstration, not a lending service** — its database holds demonstration records and developer tests only. Say "live demo", never "in production" or "serving merchants". *(Dated deliberately: "has never received a submission" is a claim about the present that decays the moment anyone visits the site. Anchor it to a date, or re-verify before repeating it.)*
- **No affordability, causal, or population claim.** Nothing here is evidence about real sellers.
- **No "improved X by Y%"** unless Y is a registered figure with an artifact behind it.
- Numbers appear with their meaning attached — a simulated magnitude is labelled as one.

---

## 1. Résumé entry

### Long form (for a research or quant-leaning role)

> **Revenue-Contingent Financing Under Volatile Sales** — independent research project · 2026
>
> - Designed and built a **paired simulation study** of revenue-contingent versus fixed-instalment financing across 10 revenue scenarios × 4 contract arms × 500 paths. All four arms run on identical generated revenue paths; the primary revenue-contingent / fixed pair is additionally **cost-matched** on principal, total repayment and term on a reference path, so that comparison isolates payment *timing*.
> - Established the study's central methodological result: **financing price and payment structure are separable questions**, and conflating them produces false conclusions — demonstrated by repricing an identical payment rule at a second cap factor and showing the cost comparison reverses while the rule is unchanged.
> - **Formally derived and engine-tested seven contract properties** characterising behaviour independent of the simulation, each asserted numerically against the implementation, including an exact finite-time completion criterion that corrected a boundary error in an earlier draft.
> - Built a **reproducibility pipeline**: five checksummed canonical artifacts, byte-versus-numeric equality reported separately across platforms, and a clean-copy regeneration verifier — after discovering that a previous "verification" step had re-hashed a committed file rather than regenerating it.
> - Wrote and enforced a **claim ledger** binding every registered quantitative claim to an artifact, a derivation, or a cited source, backed by **1,145 non-browser tests passing — 502 backend and 643 simulation, with nine browser checks defined and excluded from that total** — including a regression tripwire for known retracted phrasings, supplemented by adversarial review for the paraphrases a string test cannot catch.
> - **Retracted several claims from earlier internal drafts** — a 2.3× cost ratio, an unqualified byte-reproducibility claim, and a false null result about a guardrail arm — and documented each retraction with the evidence that overturned it.

### Short form (three lines, for a general CV)

> **Revenue-Contingent Financing Under Volatile Sales** — independent research, 2026
> Paired simulation study (10 scenarios × 4 contract arms on identical paths, one cost-matched pair, 500 paths) separating financing *price* from payment *structure*; seven formally derived and engine-tested contract properties; five checksummed reproducible artifacts; 1,145 non-browser tests passing — 502 backend and 643 simulation, with nine browser checks defined and excluded from that total. Produced a working paper, a claim ledger binding every registered quantitative claim to its source, and a documented record of my own retracted claims.

### Single bullet (for a crowded CV)

> Built a reproducible paired simulation study of revenue-contingent versus fixed small-business financing — separating price from payment structure, deriving the contract's completion and recovery conditions analytically and testing them against the engine, and binding every registered simulation result to a checksummed artifact via an automated claim ledger.

---

## 2. LinkedIn

### Project / featured section

> **Revenue-Contingent Financing Under Volatile Sales: Separating Price from Structure**
>
> Revenue-based financing takes a fixed share of a seller's revenue instead of a fixed monthly payment. The seller-side effect is mechanical — the payment falls when eligible revenue falls. The provider-side effect is conditional: recovery may lead or lag a cost-matched fixed schedule depending on the realised revenue path, measured against a break-even level implied by the matched instalment. Both directions occur in my scenario library, so I report the direction per scenario rather than as a property of the structure.
>
> They are the same mechanism seen from opposite sides, so reporting either alone misrepresents the product.
>
> I built a paired simulation to measure both at once: all four contract arms run on the identical generated revenue path, and the primary pair is cost-matched, so that comparison isolates payment timing rather than confounding it with price.
>
> Two things I did not expect going in:
>
> **The price/structure conflation is easy to commit.** I committed it myself. An early draft stated that the revenue-contingent contract "costs about 2.3× the interest of a conventional loan" — a claim that fixed one cap factor as though it were intrinsic. Reprice the identical payment rule and the comparison reverses. That claim is now withdrawn, and the retraction is in the paper, because it's the clearest example of the error the paper argues against.
>
> **Reporting failure honestly is harder than finding it.** The contract does not always reach its contractual repayment target. Where a business closes permanently before the cap is reached, recovery genuinely fails — closure from month 7 leaves every simulated path incomplete under both cap factors. But a 76.2% incomplete-recovery rate is *not* a 76.2% loss rate, and I had to build the distinction explicitly so the headline number couldn't be misread.
>
> The study is a simulation, not evidence about real sellers. It has no observed revenue, no repayment outcomes, and makes no predictive or affordability claim. What it does have is a claim ledger binding every registered simulation result to a checksummed artifact, and 1,145 non-browser tests passing — 502 backend and 643 simulation, with nine browser checks defined and excluded from that total — including guards that fail if a known retracted phrase reappears.

### Short post

> Spent this project learning that the hard part of research isn't producing a result — it's noticing when your own result is stated more strongly than your evidence supports.
>
> I built a paired simulation comparing revenue-contingent financing against a cost-matched fixed loan. Along the way I retracted three of my own claims: a cost ratio that confused price with structure, a reproducibility claim resting on a check that couldn't have failed, and a null result about a guardrail that turned out to be false in 6 of 10 scenarios.
>
> Each retraction is documented next to the evidence that overturned it. That record is the part of the work I'd most want a reviewer to read.

---

## 3. Portfolio summary

### The problem

Small e-commerce sellers with thin credit files are a natural audience for financing that flexes with revenue. But in searches documented through 2026-08-13 I did not identify a public dataset showing what a revenue-contingent contract and a fixed-instalment contract each do **to the same seller under the same revenue path**, nor a head-to-head comparison of seller burden and provider recovery for small-business financing — each seller takes at most one contract. Without that counterfactual, the trade-off can be asserted but not measured.

### What I built

A paired simulation supplying the counterfactual by construction, plus the infrastructure to keep it honest:

| Component | What it is |
|---|---|
| `research/rbf_sim/` | Simulation package — revenue generation with enforced accounting identities, four contract arms, paired runner |
| `research/DERIVATIONS.md` | Seven contract properties, formally derived and each asserted numerically against the engine |
| `research/CLAIM_LEDGER.md` | Every registered quantitative claim with its class, artifact, JSON path, checksum and required qualifier |
| `research/verify_reproduction.py` | Clean-copy regeneration reporting byte and numeric equality separately |
| Simulation Lab | Web surface rendering every simulation result from checksummed artifacts, with no financial arithmetic in the frontend |
| 1,145 non-browser tests passing | 502 backend and 643 simulation. Nine browser checks are defined and excluded from that total. They **executed and passed, 9/9, in 21.55s** — an independent run on macOS 26.0 arm64, Python 3.11.5, Playwright Chromium, at commit `dcbfc3b`; every input they exercise is byte-identical at HEAD. Where Chromium is absent they skip, and a skip is never counted as a pass. Includes a named-regression tripwire for known retracted phrasings — a tripwire, not a semantic proof, so adversarial review covers the paraphrases it cannot catch |

### What I found

**Both halves, always.** In a severe-downturn scenario the revenue-contingent arm removes 6.85 months above a 15% burden band and holds mean burden near its stable-scenario level, while recovering 65.46% of its target by month 12 against the fixed arm's 92.31%, with mean duration extending from 13 to 18.718 months. *(Simulated; 15% is an illustrative band; burden is payment ÷ GMV; the fixed arm assumes full, on-time payment.)*

**Price and structure are separable — and both matter.** Repricing the identical payment rule from f = 1.20 to f\* = 1.0945 reverses the cost comparison. The pre-cap payment rule is unchanged; the cap factor moves the contractual target and therefore completion timing and the realised stream.

**Failure is real and needs precision.** Permanent closure before completion leaves a balance unrecovered: closure from month 7 leaves every path incomplete under both cap factors. But incomplete recovery is not principal loss — closure at month 13 recovers ≈214.3M VND against a 185M advance despite 76.2% of paths missing the target at `f = 1.20`, and that rate falls to 7.6% at `f* = 1.0945` on the cap factor alone.

### What I'd want a reviewer to look at

Not the results — the **decision log**. It records every claim I retracted and why, including three that survived multiple review rounds before an adversarial reader caught them. The pattern in each case was the same: I fixed the instance in front of me and not the family.

---

## 4. Interview preparation

### The question you will be asked first

**"Walk me through the project."**

> Revenue-based financing takes a percentage of revenue instead of a fixed payment. The seller-side payment response is mechanical; the provider-side recovery ordering is conditional on the realised path. In searches I documented through 2026-08-13 I found no head-to-head measurement of both sides on the same revenue path, because you can't observe one seller on two contracts.
>
> So I simulated it. All four contract arms run on the identical generated path, and the primary pair is matched on principal, total repayment and term, so that comparison differs only in payment timing.
>
> The result I care about most isn't a number, it's a distinction: **price and payment structure are separate questions.** I got that wrong in an early draft — I wrote that the contract "costs 2.3× the interest of a conventional loan", which fixed one cap factor as though it were a property of the structure. It isn't. Reprice the same payment rule and the comparison reverses.

### Questions designed to catch you

**"Is your model accurate?"**
> It isn't a predictive model, and I don't claim accuracy for it. The simulation describes contract mechanics under assumptions I specified. There's also a machine-learning risk score in the demonstration product — that one I explicitly withdrew, because its training label was generated by a formula over the same features the model consumes. The generating function scores 0.9098 against its own label; the reported ensemble scored 0.9182. It was measuring the noise I chose, not skill.

**"So what does the study actually prove?"**
> Two classes of thing, and I keep them separate. The propositions are proved and hold for any revenue path — the completion condition, the burden elasticity, the recovery-ordering condition. The magnitudes are illustrations under parameters I chose, and they're labelled as such. What the study does *not* establish is anything about real sellers.

**"Why should I trust the numbers?"**
> Every simulation result traces to one of five checksummed artifacts, and the claim ledger names the JSON path. You can regenerate them. Analytical results are backed by their derivation rather than by an artifact, and external facts by the literature matrix — I keep those three classes separate. I'd also point at what I got wrong: I originally claimed byte-for-byte reproducibility on the strength of a check that re-hashed the committed file instead of regenerating it — a check that couldn't have failed. The corrected claim is numeric reproducibility everywhere, byte reproducibility within a fixed runtime, and 3 of 5 byte-identical on macOS — that last figure from an independent audit run of the current artifacts, not inherited from the previous generation, which measured differently.

**"What's the weakest part?"**
> Three things. The revenue process is one I specified, and structural uncertainty — whether that process is the right model — is not quantified. The fixed arm is modelled as always paid in full and on time, which flatters it. And almost all the supporting literature on contingent repayment is about student loans, not firms; the construct transfers, the findings don't, and I flag that at every citation.

**"Would you deploy this?"**
> Not as an underwriting system, no. It's a demonstration. The financing arithmetic is deterministic and tested, and I'd stand behind that — but only *given a risk tier*. The determinism starts after the tier is supplied. Upstream of that, the scorer chooses the tier, and the tier sets the advance percentage, the remittance rate, the cap factor and whether an offer is shown at all. So "deterministic" describes the arithmetic, not the end-to-end output: change the active scoring path and the displayed numbers can change. That is exactly why the risk score is not validated and shouldn't drive a decision about anyone.

### The answer worth rehearsing

**"Tell me about a mistake you made."**

> I made the same mistake three times in a row, which is the interesting part.
>
> Round one: an audit found overreaching claims in the product copy. I fixed them and wrote a test to catch regressions. Round two: an adversarial reviewer found that the sentence I'd called "the most misleading in the product" was still live on the README and the landing page — my test matched a literal string and the README used a paraphrase. Round three: the same reviewer found my *correction* had restored the retracted sentence two clauses later.
>
> Each time I fixed the instance in front of me rather than the family. What actually worked was handing the work to a reader instructed to attack it. That's now a standing step, not a one-off.

---

## 5. What must never be said about this project

Kept explicit because these are the claims that would be tempting.

| Do not say | Say instead |
|---|---|
| "Built a credit risk model with 0.92 AUC" | "Built a demonstration scoring component; its benchmark was withdrawn as circular" |
| "Deployed to production" / "serving merchants" | "Live demonstration deployment. As of August 2026, no external merchant data were used in this study; the public deployment is a demonstration, not a lending service" |
| "No external merchant has ever submitted data" (undated) | Same sentence with the date attached. An undated negative about a live site expires without warning |
| "Proved RBF is better/cheaper for sellers" | "Measured a trade-off: lower simulated burden, and slower simulated recovery **in the scenarios where it was slower** — the ordering depends on the realised revenue path, not on the structure alone" |
| "RBF always repays the financier more slowly" | "Recovery ordering is path-dependent: revenue-contingent recovery leads a matched fixed schedule when the realised mean base clears the break-even level `B* = P/r`, and lags when it does not" |
| "Showed RBF prevents default" | "Showed no guarantee of contractual completion — closure before completion leaves a balance unrecovered" |
| "Validated on real data" | "The UCI figures are pending re-run; the merchant model has no real outcomes" |
| "Calibrated to the Vietnamese market" | "Vietnam-motivated and illustratively parameterised; no parameter estimated from Vietnamese data" |
| "Reproducible byte-for-byte" | "Numerically reproducible at published precision; byte-reproducible within a fixed runtime" |
| "Analysed 500 sellers" | "Simulated 500 revenue paths per scenario. No seller was observed." |

---

## 6. Source index

| Claim used above | Where it comes from |
|---|---|
| 6.85 months, 65.46%, 92.31%, 18.718 | `baseline_v3_canonical.json` → `/scenarios/severe_downturn` · ledger S-1 |
| f\* = 1.0945, residual ≈0.02416pp | `validation_v2_canonical.json` → `/pricing` · ledger P-1, P-2 |
| 100%, 76.2%, ≈214.3M, ≈98.3M | closure artifacts → `/scenarios/*/RBF` · ledger S-3, S-4, I-3 |
| 0.9098 vs 0.9182 | `research/analysis/00_audit_evidence.py` · registry R-000 |
| 1,042 non-browser tests — 403 backend, 639 simulation | test run. Nine browser checks defined and excluded from the total; passed in the browser-capable run at D-036 (see DECISION_LOG); skip where Playwright or Chromium is absent, never counted as passes |
| Five artifacts, byte vs numeric | `research/verify_reproduction.py` · decision log D-041, D-043 |
| Retractions | decision log D-015 (2.3×), D-040 (RBF-G null), D-041 (reproducibility), D-042/D-046 (incomplete corrections) |
