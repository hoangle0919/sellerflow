# Bilingual site + USD reference equivalents — verification record

Branch `codex/bilingual-daily-fx`, based on `origin/main` `b3683e5`.
Implementation only. Not pushed, not merged, not deployed.

## What was verified, and how

| Check | Result |
|---|---|
| Backend suite (`--ignore=test_lab_browser.py`) | **599 passed, 2 skipped** |
| Simulation suite (`research/rbf_sim/tests`) | **651 passed** |
| Node prototype-state tests (`tools/check_prototype_state.cjs`) | **7 passed** |
| Catalogue parity (`tools/check_i18n.py`) | **en=583 vi=583**, every referenced key resolves |
| 20 registered research artifacts vs `origin/main` | **unchanged** (SHA-256) |
| 3 publication PDFs vs `origin/main` | **unchanged** (SHA-256) |

Baseline before this work was 556 passed / 1 skipped. The increase is 42 new FX
tests plus one new i18n-isolation guard.

## Not executed

- The nine Playwright Lab browser tests. Not run.
- VoiceOver and any screen-reader behaviour. Not run, by instruction.
- No live merchant submission, no dashboard login against production, no
  payment, no notification.
- Browser checks were performed against a local preview at 360px and desktop
  width only. 390/768/1440 were not separately exercised.

## FX adapter

Provider reconfirmed before implementation: no API key, free for commercial use
of blended rates, daily updates, caching encouraged, **no SLA stated**. One
successful fetch demonstrates connectivity and nothing more; the observed rate
is not hardcoded anywhere.

A failing fetch was diagnosed rather than guessed at: the cause was the **CA
bundle, not the User-Agent** — three different agents failed identically with
`CERTIFICATE_VERIFY_FAILED`, and an explicit `certifi` context fixed it. The
same root cause had previously broken the operator-alert path. `certifi` was
already pinned, so no dependency changed.

42 tests, all mocked, covering orientation, cents rounding, wrong pair, inverted
orientation, malformed and future dates, the three freshness bands and their
boundaries, timeouts, 429/5xx, oversized responses, cache expiry, failed refresh
preserving `fetched_at`, concurrency dedupe and recovery. One live smoke test is
gated behind `RBF_FX_LIVE=1` and is never used as a correctness oracle.

A guard asserts no calculation module imports `fx`, checked by source inspection
rather than `sys.modules`, because an import inside a function would not appear
in a fresh-import check.

## Defects found and fixed during the work

1. **85 catalogue keys were referenced but undefined**, via lookup tables and
   arrays (`VERDICT`, `CHIP_DEFS`, `TIER_LABEL`, `DECISION_STEPS`). `t()` returns
   `''` for an unknown key, so verdict labels, tier names, severity levels and
   chip states rendered **blank in every language, English included**. The parity
   checker reported OK because its regex only saw direct `t('key')` call sites.
   The checker now treats any namespaced string literal as a reference.
2. **An A-9 qualifier was lost.** `origin/main` read "…observed window, not a
   lifetime return)". After the string moved into the catalogue it read only
   "Observed return to closure", which is the exact misreading A-9 forbids.
   Restored in both languages.
3. **Approved hero copy was replaced with paraphrases** while inferring English
   for keys whose source text existed on `origin/main` ("Preview unavailable"
   became "Unavailable", and six similar). All restored verbatim.

## Guards updated rather than relaxed

Six guards asserted English literals that now live in the catalogue. Each was
rebound to assert the copy where it actually is, **and to require a non-empty
Vietnamese value** — a disclaimer that exists only in English is not a
disclaimer for a Vietnamese reader. That is stricter than the assertion it
replaced. No guard was deleted or weakened.

## Known gap

`backend/lab.py` generates user-visible English prose (scenario labels, arm
names, findings, metric definitions). **102 of 436 visible text nodes on the Lab
page remain English in Vietnamese mode** as a result. Keying it means changing
the shape of an API response that renders registered research output, which is a
broader change than this task authorises. Reported, not attempted.
