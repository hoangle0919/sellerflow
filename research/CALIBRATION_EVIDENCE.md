# Calibration evidence table — feasibility assessment

**Status: draft input for review. Registers no claim, no result, and no artifact.**
Produced 2026-10-05 at commit `c36c98a`, revised the same day after review, to
answer one question *before* any simulation work begins: **is calibrating this
study to Vietnamese e-commerce conditions feasible, and which parameters can
actually be estimated?**

**Scope.** Everything here concerns the **RBF financing simulation**
(`research/rbf_sim/`) and nothing else. The product's underwriting classifier is
a separate system with separate inputs, and no statement in this document
transfers to it. (This conflation was made twice in earlier drafts and is called
out here so the next reader does not inherit it.)

§§1–5 are the pre-search feasibility assessment. **§6 is the bounded search
itself**, run 2026-10-05, and it **revises §5** — the parameter the pre-search
assessment called least estimable turned out to have the best evidence.

---

## 1. Baseline freeze

Any calibrated result must be comparable against a fixed reference. This is it.

| | |
|---|---|
| Commit | `c36c98a` |
| Spec | v1.0 + amendments A-1 … A-9 |
| Base seed | `20260803` |
| Design | 10 scenarios × 4 arms × 500 paths |
| Local runtime | Python 3.11.5 · NumPy 2.4.6 · pandas 2.2.3 |

Canonical artifacts, re-checksummed at this commit (first 16 hex):

| Artifact | SHA-256 |
|---|---|
| `baseline_v3_canonical.json` | `363729016298b3d7` |
| `baseline_equalcost_v2_canonical.json` | `b3ebfe6a5a7e7f48` |
| `baseline_closure_v2_canonical.json` | `21b8e207ff2db9ac` |
| `baseline_closure_equalcost_v2_canonical.json` | `e1e6d81bbeeb60f0` |
| `validation_v2_canonical.json` | `7d9b9d0f9b0fd0fe` |

**Caution carried over from the P3 correction:** that correction concerned the
classifier's `train_model.py`, which reads a cached `backend/data/sellers.csv`
when present and only falls through to the seeded generator otherwise. The
simulation does **not** have this defect — `rbf_sim` reads no external data at
all (only `canonical.py` touches the filesystem, to write and verify artifacts),
so a seed match here *is* sufficient for comparability. The transferable lesson
is narrower: record input data, code version and environment together. The
mistake itself does not carry over.

---

## 2. Parameter inventory and evidence status

Every calibratable input in `rbf_sim/generator.py::PathParams`, with its value as
shipped. "Declared" means the code already labels it an assumption. The verdict
column is **post-search** — see §6 for the evidence behind each.

| Parameter | Current | Declared? | In the 45-source matrix | Post-search verdict (§6) |
|---|---|---|---|---|
| `R0` starting monthly revenue | 185,000,000 VND | no | **Nothing.** L-01 is a benchmarking construct over 128 economies and explicitly supports no Vietnam-specific parameter | **Flagged as implausibly high** — ~3.1× the mean per-shop figure implied by Metric, which is itself far above the median (§6, C-8) |
| `growth` monthly drift | 0.0 | no | Nothing | Not searched this pass |
| `sigma` idiosyncratic volatility | 0.15 | no | Nothing | **Not estimable from public data.** Model form supported, magnitude not (§6, C-3) |
| `seasonality` 12-month shape | `_SHAPE` vector | **yes** — "ASSUMPTION, not measurement" | Nothing in-matrix | **Usable proxy exists** — GSO monthly retail series, with stated mismatch (§6, C-6) |
| `shock_depth` | 0.40 | no | Nothing | Not searched this pass; keep as declared range |
| `shock_onset` | month 7 | no | n/a | Keep as scenario (not a population parameter) |
| **closure timing** | deterministic month | no | Nothing | **Direct evidence found** — see §4 and §6, C-1. Best-evidenced parameter in the study |
| `aov0` average order value | 440,000 VND | no | Nothing | No source met the four-field bar (§6, C-9) |
| `aov_sigma` | 0.05 | no | Nothing | Not searched this pass; keep as declared range |
| `return_rate` | 0.03 | no | Nothing | **No suitable source found under this protocol** (§6, C-5, C-10) |
| `platform_fee_rate` | 0.0 | **yes** — "ILLUSTRATIVE, unsourced; swept in S-15" | Nothing in-matrix; schedules are published | **Deprioritised — see §2a.** Schedules are published and estimable, but the parameter does not affect repayment |
| FIX-B nominal rate | 18% | **yes** — on the withdrawn-claims list; must never be called "conventional" | Nothing | **Contextual evidence only** (§6, C-4) |

### 2a. Why platform fees are deprioritised, not merely unsourced

`contracts.py` sets `remittance_basis: str = "net_sales"` (spec A-1). The platform
fee reduces `cash_receipts` but **does not enter the remittance base**, so it does
not affect repayment at all. Calibrating it would move no result in this study.
Published fee schedules do exist — figures encountered this pass put Shopee
Vietnam commission at 1.5–17% for non-mall sellers plus a ~6% transaction fee and
a ₫3,000 per-order infrastructure fee from 2025-07-01, **via third-party fee
trackers, not verified against Shopee's own published schedule**. So this is a
case of *estimable but not load-bearing*.

It becomes load-bearing only if the study later models the seller's **remaining
cash or affordability**, which depends on receipts rather than on the remittance
base. If that extension happens, this parameter moves back up the list.

---

## 3. What the existing search already told us

Of 45 source identifiers assembled under a documented protocol through
2026-08-13, three mention Vietnam and none supply a seller-level parameter:

- **L-01** — IFC/SME Finance Forum MSME finance gap. 128 developing economies
  including Vietnam. The matrix's own exclusion note says it supports no
  Vietnam-specific parameter. A counterfactual benchmarking estimate, not an
  observation.
- **L-02** — World Bank *Digital Vietnam*. Establishes only that Vietnam is a
  policy-salient digital setting. The matrix records that it does **not**
  establish that financiers observe seller revenue; that observability is a
  modelling premise of this study.
- **L-03** — **declined as evidence**: commercial market-sizing relayed through
  ministry news pages, methodology not public.

And **Gap V-1** records that credit-bureau coverage prevalence among Vietnamese
e-commerce sellers could not be verified.

Those gaps are statements about the searches performed, not proof that nothing
exists — and §6 confirms that reading: the searches were documented and
deliberate, and they still missed the household-business literature entirely.

---

## 4. Closure: the parameter most likely to be measured wrongly

Flagged in review, and it deserves its own section — it has the largest effect on
the headline finding and is the most vulnerable to a measurement error that looks
like data.

The study's strongest result is that revenue-contingency reschedules a decline but
does not survive a stop. Its magnitude depends on **when** trading stops —
currently a chosen month, not a hazard.

The tempting proxy is seller disappearance from a platform, and it remains the
wrong quantity. **A seller vanishing from a platform does not establish that the
business closed, and closure does not establish that repayment failed.** A
disappearance can be a move to another channel, a dormant or seasonal account, a
rebrand or new storefront, a policy suspension, or a change in how the platform
reports.

**What the closure scenarios do and do not require.** They show what happens *if*
revenue stops. They are valid as scenarios without any estimated hazard, and
nothing below is needed to defend them. A hazard would add something different:
it would let the study say how *often* the stop case arises, turning a
conditional statement into a probability-weighted one. That is an extension, not
a repair.

§6 found a source that measures this in the right country and separates
permanent closure from temporary suspension. That changes the assessment below.

---

## 5. Pre-search feasibility assessment — superseded in part by §6

Recorded as written, because one of its predictions was wrong and the error is
instructive.

1. **Estimable, probably:** seasonality shape, platform fee rate, possibly return
   rate.
2. **Proxy only, with the population stated:** revenue level, AOV, benchmark
   lending rate.
3. **Likely not estimable from public data:** seller-level revenue volatility
   (`sigma`) and the exit hazard.

**What §6 changed.** Item 3 was half wrong. `sigma` is indeed not estimable. The
**exit hazard is the best-evidenced parameter in the study** — measured in
Vietnam, on a population that overlaps the study's sellers, from a tax census.
Meanwhile `return_rate` from item 1 found nothing usable. The pre-search ranking
tracked *how hard the quantity sounded*, not where anyone had actually looked;
the household-business tax literature was simply outside the frame of both
earlier search rounds.

**On the contribution framing.** An earlier draft of this section said the phase
converts "hidden assumptions into declared ones." That mischaracterises the
original study, which already disclosed these assumptions in code and in the
spec. The contribution is narrower and should be stated as: **calibrating the
minority of parameters that published data can support, with populations named,
and attaching sensitivity ranges to the rest.**

---

## 6. Bounded search, 2026-10-05

**Protocol.** Every candidate records four fields — **population** (whose
activity), **frequency**, **measured quantity**, **granularity** — plus the
parameter it could inform and **the assumptions required to connect them**.

**Classification.** Each candidate starts at **unverified** and is sorted into one
of four states. A source can be entirely credible and still be unsuitable for a
given parameter; "unsuitable" is a statement about the fit, not about the source.

- **Direct evidence** — right quantity, population overlapping the study's
- **Usable proxy** — right quantity, different population, mismatch stated
- **Contextual evidence** — supports the model's *form* but not its magnitude
- **Unsuitable measure** — credible source, wrong quantity for this parameter

**Coverage.** Six lanes were planned. One (Vietnamese-language) ran on
2026-10-05 before a tool limit stopped it four queries in; the rest were run
inline afterwards. Lane coverage is recorded in §6c. **Empty results are reported
narrowly: "no suitable source found in these sources under this protocol," which
is a feasibility finding about the search, not a claim that the data do not
exist.**

### 6a. Direct evidence

**C-1 · exit hazard, and the suspension/closure split**

> Islamaj, E., Le, D. T., & Pham, T. M. (2022). *Firm Entry, Exit and
> Suspension: Evidence from Household Businesses in Vietnam.* World Bank Policy
> Research Working Paper 10223. An advance article of the same work appears in
> the *World Bank Economic Review* (`doi:10.1093/wber/lhaf038`, listing seen
> 2026-10-05; the published version was not opened — every figure below comes
> from the working-paper PDF, which was read in full).

| Field | |
|---|---|
| **Measured quantity** | Counts of administrative **tax filings** of two distinct kinds: (i) permanent business closure, (ii) temporary suspension of ≥1 month |
| **Population** | The **universe of tax-registered household businesses** (hộ kinh doanh) in Vietnam, all communes. Registration liability begins above **100m VND annual revenue** (~USD 4,300). The paper states plainly that most Vietnamese HBs are *not* tax-registered |
| **Frequency** | Monthly (commune-month panel); annual aggregates also published |
| **Granularity** | Firm-level filing events, aggregated to commune-month |

Figures, from the paper's Table 1 and Table A.1:

| | 2018 | 2019 |
|---|---|---|
| Annual regular filings (stock) | 908,679 | 917,917 |
| Closure filings | 33,673 | 52,042 |
| Suspension filings (firms, ≥1 month) | 227,205 | 225,230 |
| **Closure rate** | **3.71%/yr** | **5.67%/yr** |
| **Suspension rate** | **25.0%/yr** | **24.5%/yr** |
| Entry rate | — | 4.95%/yr |
| Mean dormancy of suspending firms | 2.8 months | 2.5 months |

Pre-COVID commune-month averages: **0.5 closure** and **6.7 suspension** filings
per commune per month, against a stock of 92.5 — i.e. **0.54%/month closure** and
**7.2%/month suspension**. Two independent routes agree: the 2019 annual closure
rate implies **0.49%/month** if spread uniformly, against 0.54% measured
directly. That internal consistency is the main reason to trust the figure.

Two heterogeneities that bear directly on this study:

- **Wholesale and retail accounts for more than half** of all closure and
  suspension filings — the sector nearest the study's sellers.
- **Suspension falls as revenue grows**, but **closure is most likely in the top
  revenue quartile**. This cuts against the intuitive assumption that larger
  sellers are safer, and should be checked before any size-conditioned hazard is
  built.

**Assumptions required to use this for closure timing:**

1. **Filings approximate cessation.** The authors argue this holds better for HBs
   than for enterprises, because Vietnamese HBs face low exit barriers — the
   objection that dissolution paperwork lags reality applies to the *doanh
   nghiệp* register, not here. But their footnote 14 concedes some HBs close
   without filing, so closure is **undercounted** by an unquantified amount.
2. **Online sellers resemble the tax-registered HB population.** Partly
   supported: >half of filings are wholesale/retail, and the study's seller at
   185m VND/month is 22× the registration threshold, so it would certainly sit
   inside this population. Not supported for channel-specific risks.
3. **Constant hazard over 24 months.** The paper includes month fixed effects but
   publishes no pre-pandemic monthly seasonal profile, so a Tet concentration of
   exits can be neither confirmed nor excluded here. C-2 suggests it exists.
4. **2018–19 generalises to 2026.** The 2020 figures are pandemic-contaminated
   (suspension >40%) and should not be pooled with the pre-COVID baseline.

**What it buys the study.** At 0.49%/month, the probability that trading stops at
least once inside the 24-month horizon is **≈11%** (7.3% at the 2018 rate). The
closure arms currently apply a stop to every path; this supplies the weight they
would need to be read as a population statement rather than a conditional one.

**The more useful finding may be suspension, not closure.** ~25% of these firms
suspend for part of a year, averaging 2.5–2.8 months. A temporary revenue stop of
a few months is much closer to what a revenue-share contract actually has to
absorb than permanent closure is — and it is an order of magnitude more common.
The study has no arm for it.

### 6b. Usable proxies, contextual evidence, and unsuitable measures

**C-2 · seller-level survival on a platform — usable proxy** *(wrong country)*

> Fan, Y., Ju, J., & Xiao, M. (2016). *Reputation premium and reputation
> management: Evidence from the largest e-commerce platform in China.*
> International Journal of Industrial Organization.

- **Measured quantity:** each seller's monthly revenue, transaction volume, and
  survival. Survival = "still in the data" in month *t+6* / *t+12*.
- **Population:** a **25% random sample of all Taobao sellers** who sold ≥1 item
  between March 2010 and April 2011 — 1,322,546 Marketplace + 9,462 Mall sellers.
- **Frequency:** monthly. **Granularity:** seller-month (the right unit).

Month-2 cohort survival:

| Cohort | n | 6-month | 12-month | Implied monthly hazard |
|---|---|---|---|---|
| Established | 104,138 | 91.94% | 79.16% | 1.4% → 1.9%/mo |
| New | 52,998 | 33.52% | 21.73% | ~12–17%/mo |

The "disappearance ≠ closure" objection was **tested rather than asserted**: the
authors report that sellers absent from the data six months later **never
reappear**. That is materially stronger than the Metric shop-count series (C-7).
Their stated caveat is the opposite direction — a seller pausing in Month 14, the
last month of the sample, is scored as dead, so the 12-month figure is biased
*down*.

- **Assumptions required:** that Vietnamese Shopee/TikTok Shop sellers in 2026
  resemble Taobao sellers in 2010–11 — different country, platform, era and
  logistics regime. Weak on its own.
- **What it buys:** a bracket. 1.4–1.9%/month here against 0.49–0.54%/month in
  C-1 is a 3–4× spread across two populations measured very differently. That
  spread *is* the honest sensitivity range for the hazard, and it is far better
  than an unsourced chosen month.
- Also relevant to seasonality: the paper documents that in February 2011 both
  seller count and average monthly revenue "took a plunge" for Chinese New Year,
  and that while many sellers merely pause, "some consider the time a natural
  point for exiting the market." Exit and seasonality are **coupled** at the
  holiday. The Vietnamese analogue is Tet.

**C-3 · `sigma` — contextual evidence only**

Same source. Table 6 regresses **log(revenue)** on reputation with **seller and
month fixed effects**: within R² = **0.022** (established), **0.028–0.029** (new).
So ~97–98% of within-seller month-to-month variation in log revenue is left
unexplained by reputation and calendar month.

- **What this supports:** the *model form* — treating a seller's month-to-month
  revenue as dominated by idiosyncratic noise rather than by observable seller
  characteristics.
- **What it does not support:** the magnitude. **No residual standard deviation
  is reported**, so `sigma = 0.15` is not calibrated by this and the direction of
  any error is unknown.
- **A trap worth recording.** Table 4's Std. Dev. — $44,993.89 on a mean of
  $5,966.28 (established); $8,459.18 on $876.61 (new) — is **pooled over
  seller-months**. It mixes between-seller dispersion with within-seller
  variation over time and, given the skew, is dominated by the former. The
  implied CVs of 7.5 and 9.7 are **not** volatility estimates and must not be
  used as such. The within-seller quantity *is* identified in these data (the
  fixed-effects specification uses exactly that variation) but is not published.
- **Verdict:** `sigma` stays a declared sensitivity range. Estimating it needs
  platform cooperation or primary collection from sellers.

**C-4 · FIX-B 18% nominal rate — contextual evidence only**

- **Measured quantity:** average commercial-bank lending rates, reported by the
  State Bank of Vietnam and by banks' own rate disclosures.
- **Population:** formal bank credit to registered enterprises — typically
  secured, with documentary requirements. **Frequency:** periodic SBV releases.
  **Granularity:** bank or system aggregate.
- Figures encountered (search summaries only, **SBV primary not opened**):
  average lending rate across new and outstanding loans ~**7.8–10%/yr**;
  short-term priority-sector ~3.9%; SMEDF preferential facilities 1.2–4.4%;
  one 2026 press figure of 10.7% average.
- **Why this is not a calibration:** FIX-B stands for an **unsecured,
  small-ticket, revenue-based** product. Bank SME lending is a different market
  with different collateral, screening and ticket size. These rates cannot
  identify 18%.
- **What it buys:** 18% sits roughly **2× above** documented formal bank SME
  pricing, which is the right *direction* for an unsecured alternative product.
  That is sayable, sourced and much better than leaving the figure bare. It is
  still not a market rate for this product, and must continue to carry its
  withdrawn-claims note — **never "conventional."**

**C-5 · Shopee's own non-fulfilment metric — unsuitable (definitional, not a rate)**

Shopee Vietnam's Seller Education Hub publishes "Tỷ lệ đơn hàng không thành công"
(non-fulfilment rate), computed **per seller** for policy enforcement.

- **Population:** sellers on Shopee Vietnam. **Frequency:** one-off policy
  document. **Granularity:** seller-level. **Measured quantity:** the platform's
  own enforcement metric — not opened, so its composition is unverified.
- **Why unsuitable:** a penalty metric is constructed for enforcement, not
  measurement, and typically carries carve-outs; and it is a **definition, not a
  value**. It cannot calibrate 0.03.
- **What it buys:** it proves per-seller return data **exists inside the platform
  and is not published**, and it is the right document to force the distinction
  between (a) cancellations, (b) refunds, (c) returned orders and (d) returned
  sales value before any number is sought. The simulation's `return_rate` reduces
  sales *value*, i.e. (d) — the quantity least often reported.

**C-6 · seasonality — usable proxy, mismatch stated**

- **Source:** Vietnam General Statistics Office, **total retail sales of goods
  and consumer services**, monthly.
- **Measured quantity:** retail and consumer-services turnover at current prices,
  **not seasonally adjusted**. **Population:** all retail and consumer services
  nationwide — **offline and online together**. **Frequency:** monthly, back to
  1990. **Granularity:** national, macroregion and province.
- *(Series description taken from data-vendor pages; the GSO primary release was
  not opened this pass.)*
- **Assumptions required:** (i) that online sellers share the economy-wide Tet
  shape; (ii) that the series is detrended first — at ~9% YoY growth a raw
  monthly series conflates trend with season; (iii) that offline-dominated
  categories do not drive the shape.
- **Verdict:** the most defensible seasonality source found. Good enough for the
  **Tet trough**, not for an e-commerce-specific 12-month multiplier. Metric's
  quarterly platform GMV is worse for this purpose: aggregate GMV also moves with
  seller entry and exit and with platform promotion calendars, none of which is
  within-seller seasonality.

**C-7 · Metric shop-count decline — unsuitable measure**

Metric's year-on-year change in the count of order-generating storefronts
(2025: 601,780 shops, −7.43% YoY; press framing "165,000 shops left the
platforms").

- **Measured quantity:** a **net change in a stock**. A hazard needs gross exits
  from a defined cohort; a net change nets entry against exit and recovers
  neither. The underlying event is "storefront had zero orders this period,"
  which does not establish closure.
- **Framing correction, carried from the Vietnamese-language lane:** the press
  systematically relabels this as "rời sàn" / "đóng cửa" — shop closed. If any of
  this is ever cited, it must be described as a net change in the count of
  order-generating storefronts, never as closure. Unlike C-2, no re-entry check
  is published.

**C-8 · `R0` — unsuitable as a level, but a flag worth acting on**

Metric's 2025 four-platform GMV (429.7 trillion VND) ÷ its count of
order-generating shops (601,780) implies a mean of **~714m VND/yr ≈ 59.5m
VND/month** per shop. The simulation's `R0` = **185m VND/month is ~3.1× that
mean** — and the mean itself sits far above the median under the skew Metric
itself describes (growth concentrated among large sellers).

- Both inputs are **unverified relays**, so this is not a correction. It is a
  flag: `R0` likely does not represent a typical small seller, and if the study's
  framing is small-seller financing, that gap matters more than most parameters
  on this list. A mean over a skewed distribution is the wrong statistic anyway;
  the study needs the small-seller region, which is not published.

**C-9 · CEIC "Vietnam E-Commerce AOV" — unsuitable (internally inconsistent)**

The public snippet reports USD 236.852 for April 2025 against a USD 29.377 median
for Dec 2018–Apr 2025 **in the same series** — an ~8× internal inconsistency,
with no published population definition and behind a paywall. Not usable without
opening the series definition, and not worth citing in this state.

**C-10 · Sea Limited gross orders — unsuitable, and it explains the gap**

Sea Limited's investor reporting defines an order as each confirmed buyer–seller
order "regardless of whether the transaction is settled **or if the item is
returned**" — definition as relayed in search summaries of Sea's results releases
and Form 20-F; **the filing itself was not opened this pass**.

- **Why this matters beyond being unusable:** the issuer's own public order metric
  is *constructed to be return-insensitive*, so no return rate can be differenced
  out of platform disclosures. Together with C-5 this is a real feasibility
  finding: `return_rate` is unpublished by construction at both the platform and
  the issuer level, not merely missed by this search.

### 6c. Coverage, and what "nothing found" means here

**Searched, and no suitable source found under this protocol** — a statement
about these sources and this protocol, not about whether the data exist:

- **`return_rate`, numeric value.** The Vietnamese-language lane returned
  logistics-vendor and seller-tool marketing blogs (GHTK, Sapo, Tuha, SuperShip
  and similar) carrying mutually inconsistent figures with no methodology, no
  population and no sample — "10–15% overall," "apparel 5–10%," and "apparel
  25–40%, up to 50% during mega-sales" appeared in the same result set; one
  attributed a figure to a US shopper study. **None is usable and none should be
  cited.** The issuer and platform routes are closed by construction (C-5, C-10).
- **`sigma`.** No Vietnamese source encountered reports month-to-month revenue
  dispersion for individual sellers; everything public is platform-aggregate. An
  aggregate is smoother than its components by construction, so using it even as
  a lower bound would err in the dangerous direction.

**Not searched — no conclusion drawn, and these are the first things to do next:**

- **VECOM's EBI report** (Báo cáo Chỉ số Thương mại điện tử). Located but only
  index scores and market-size forecasts were visible in public summaries. The
  underlying **survey of ~5,000 enterprise responses** is the most likely
  Vietnamese source of *seller-reported* quantities that platform-scraped vendor
  data cannot provide. The report itself was not obtained. **Highest-value
  remaining lead.**
- **Sách trắng Thương mại điện tử** (MoIT white book) — not reached.
- The **published WBER version** of C-1, which may add sector-specific rates or a
  monthly profile the working paper does not report.
- `growth`, `shock_depth`, `aov_sigma` — not searched this pass.
- SBV **primary** releases for C-4; **GSO primary** monthly series for C-6. Both
  currently rest on secondary descriptions.

**Not reported, because nothing was found that met the bar:** no candidate is
listed for `growth`, `shock_depth` or `aov_sigma`, and none should be inferred
from their absence here.

---

## 7. Revised feasibility assessment

**Calibration is partially feasible, and the achievable version is narrower and
differently shaped than the proposal language implied.**

| | Parameters | Basis |
|---|---|---|
| **Calibratable now, with the population named** | closure/exit hazard; suspension incidence and duration | C-1, direct evidence, Vietnam, tax census |
| **Calibratable as a stated proxy** | seasonality (Tet trough); platform fee schedule *(not load-bearing — §2a)* | C-6, C-2; published schedules |
| **Sensitivity range only, sourced direction** | FIX-B nominal rate | C-4 — 18% is ~2× documented bank SME pricing, direction defensible, level not |
| **Sensitivity range only, no source** | `sigma`, `aov0`, `aov_sigma`, `return_rate`, `growth`, `shock_depth` | C-3, C-5, C-9, C-10; §6c |
| **Flagged for reconsideration** | `R0` | C-8 — likely not a typical small seller |

**The contribution this supports.** Not "calibrated therefore real." Rather: one
parameter — the one carrying the headline result — moves from an unsourced chosen
month to a **measured Vietnamese rate with a named population and a stated
3–4× uncertainty bracket**, and the rest become declared sensitivity ranges with
their populations and failure modes written down. That is a smaller claim than the
proposal made and it is defensible.

**Two substantive findings beyond the parameter table:**

1. **Suspension, not closure, may be the better-matched risk.** ~25% of
   tax-registered Vietnamese household businesses suspend for part of a year,
   averaging 2.5–2.8 months, against a ~5% annual permanent-closure rate. A
   months-long revenue interruption is both far more common than closure and
   closer to what a revenue-share contract must absorb. **The study has no arm
   for it.** Adding one is a design question, not a calibration question, and it
   does not depend on any further data.
2. **Exit and seasonality are coupled.** C-2 documents sellers treating the
   holiday as a natural exit point. A constant monthly hazard and an independent
   seasonality vector may therefore both be wrong in the same place — at Tet.
   Worth testing before either is calibrated.

**Recommended next step:** obtain the VECOM EBI report and the published WBER
version of C-1 before any simulation change. If VECOM yields nothing seller-level,
the honest shape of this phase is **one calibrated hazard plus a sensitivity
study**, and it should be described that way rather than as a calibration.
