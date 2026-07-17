# RBF

**Revenue-Based Financing** — evaluate revenue-based financing with evidence, not guesswork.

RBF analyzes ecommerce-merchant revenue, tests repayment scenarios, and surfaces the risks and assumptions behind every financing recommendation. Most Vietnamese sellers have no credit-bureau (CIC) record — but their platform revenue, growth, returns, and fulfillment history is a richer, third-party-verified dataset than any bureau file. RBF turns that data into a structured financing analysis: recommended advance, remittance percentage, repayment cap, downside scenarios, and the categorized risk findings behind the recommendation — through one API call in under a second.

**Live:** https://sellerflow-production.up.railway.app *(hostname predates the RBF rename; see [Retained identifiers](#retained-identifiers) below)*

RBF analyzes. It does not hold capital or make loans — a lender or financier structures and funds the actual advance.

## What RBF is not

- Not a lending commitment or an offer of credit. Every result carries this disclaimer in-product.
- Not a fully automated underwriting decision. It is decision *support* — a human should review the recommendation before financing.
- Not a risk model validated on real outcomes yet. See [Model status](#model-status).

## How it works

```
merchant revenue ──▶ RF + LR ensemble ──▶ PD estimate ──▶ deterministic financing engine ──▶ recommendation
(revenue, growth,      (scikit-learn,                        (backend/financing_engine.py —        + scenarios
 returns, ratings,       synthetic baseline)                   plain Python, no model calls           + risk findings
 fulfillment, tenure)                                          arithmetic, unit-tested)
```

The risk score (PD) comes from a trained ensemble. Everything downstream of it — the advance amount, remittance percentage, repayment cap, scenario durations, and risk categorization — is **plain deterministic arithmetic in `backend/financing_engine.py`, with no model or AI call anywhere in the path.** That split is deliberate: a language model may explain a number in this product; it never computes one.

- **Risk model:** Random Forest + Logistic Regression ensemble (0.92 AUC on held-out *synthetic* validation data — see [Model status](#model-status) for what that does and doesn't mean).
- **Financing structure:** advance = 15% of annual revenue (low risk) or 8% (medium risk); repayment cap = advance × 1.15–1.30; remittance = 8–12% of monthly revenue. Because remittance is a percentage of revenue rather than a fixed installment, a revenue decline extends the repayment term instead of triggering a default — that mechanical fact is the actual point of the scenario analysis below, and is stated explicitly rather than left implicit in a chart.
- **Scenario analysis:** base case, moderate decline (-20%), severe decline (-40%), and a growth case, each showing the resulting monthly remittance and repayment duration.
- **Risk findings:** revenue trend, revenue stability, fulfillment quality, business maturity, operational efficiency, existing obligations, and data completeness — each with a severity, the supporting evidence, why it matters, and (where applicable) what information would resolve it. Every finding is `deterministic: true`; none of it is inferred by a model.

## Data provenance

Every value RBF returns is one of: **user-entered fact**, **system-derived metric**, or **assumption** — and the API response says which. The current submission form collects a single current-period revenue figure plus a reported growth rate, not a monthly time series, so volatility, seasonality, and drawdown metrics are honestly reported as `null` with a `missing_data_note` rather than invented from one data point. Submitting monthly revenue history (`backend/financing_engine.py::revenue_metrics`) unlocks them.

## API

```bash
curl -X POST https://sellerflow-production.up.railway.app/api/sellers/submit \
  -H "X-API-Key: sf_live_..." \
  -H "Content-Type: application/json" \
  -d '{
    "shop_name": "Thời Trang Linh Chi",
    "platform": "Shopee",
    "monthly_revenue": 185000000,
    "revenue_growth": 0.22,
    "order_volume": 420,
    "avg_order_value": 440000,
    "return_rate": 0.028,
    "rating": 4.9,
    "days_active": 680,
    "inventory_turnover": 6.2,
    "late_ship_rate": 0.018,
    "previous_loans": 2
  }'
```

The response includes a `financing` object with the full structure, scenarios, and risk findings shown above. Free pilot keys (100 assessments/month) are self-serve from the [pricing page](https://sellerflow-production.up.railway.app/#pricing). Full reference: [/api/docs](https://sellerflow-production.up.railway.app/api/docs).

| Endpoint | Auth | Purpose |
|---|---|---|
| `POST /api/sellers/submit` | API key (or rate-limited keyless) | Analyze a merchant, get the full financing structure |
| `GET /api/assess/preview` | Rate-limited, keyless | Same analysis, no persistence — powers the live interactive demo |
| `GET /api/keys/usage` | API key | Quota usage for the current month |
| `POST /api/keys/issue` | — | Self-serve pilot key issuance |
| `GET /api/portfolio` | Session token | Merchant/assessment list with aggregate risk stats |
| `GET /api/health` | — | Service and model status |

## Stack

- **Backend:** Python 3.9–3.11, FastAPI, SQLite (persistent volume in production)
- **Risk model:** scikit-learn — Random Forest + Logistic Regression ensemble, StandardScaler pipeline
- **Financing engine:** plain Python, `backend/financing_engine.py`, zero external calls — see [Testing](#testing)
- **Frontend:** single-file HTML/CSS/vanilla JS — no framework, no build step
- **Payments:** Stripe Payment Links; paid checkouts are verified server-side and issue metered API keys automatically
- **Infra:** Railway (Nixpacks), health-checked deploys, models trained at first boot

Security: server-side session auth with expiry, SHA-256-hashed API keys, per-plan monthly quotas, per-IP sliding-window rate limits on every public endpoint, strict Pydantic input validation.

## Testing

```bash
cd backend && ./venv/bin/python -m pytest tests/ -v
```

18 tests cover `financing_engine.py` with hand-computed expected values (not just "it ran without error"): revenue-metric statistics with and without history, financing-structure math across risk tiers and requested-vs-recommended amounts, scenario-duration ordering under decline and growth, zero/edge-case inputs, risk-finding severity and categorization, and end-to-end completeness scoring. There is no test coverage yet for the FastAPI routes themselves, the ML ensemble's training pipeline, or the frontend — see [Known gaps](#known-gaps).

## Run locally

```bash
./start.sh
```

- App: http://localhost:8000
- API docs: http://localhost:8000/api/docs
- Local dashboard password defaults to `demo2025` — set `DASHBOARD_PASSWORD` to override (production always overrides).

Optional environment variables: `DASHBOARD_PASSWORD`, `STRIPE_SECRET_KEY`, `STRIPE_PAYMENT_LINK`, `RESEND_API_KEY`, `NOTIFY_EMAIL`, `DATABASE_URL`.

## Deploy

```bash
railway login && railway init && railway up && railway domain
```

`railway.toml` configures the build; health checks run against `/api/health`. Attach a volume at `/app/backend/data` to persist the database across deploys.

## Model status

The risk ensemble is trained on a **synthetic baseline** calibrated to realistic seller distributions — it has not seen a real merchant's real repayment outcome, and the 0.92 AUC figure describes how well it separates synthetic-good from synthetic-bad, not real-world predictive power. It's designed to be retro-validated against a lender's or financier's historical loan book: score their past decisions, compare the ranking, and recalibrate from there. Until that happens, treat every recommendation as a structured hypothesis, not a proven one.

## Retained identifiers

Renaming SellerFlow → RBF touched every user-facing surface (landing page, nav, dashboard, result page, footer, privacy page, error messages, notification templates, CSV export filenames, generated assessment-ID prefix). A few internal identifiers were deliberately **not** renamed, because doing so would risk breaking the deployed app for no user-visible benefit:

| Identifier | Where | Why retained |
|---|---|---|
| `sellerflow-production.up.railway.app` | Production hostname, GitHub repo name, Railway project name | Already distributed on a resume, LinkedIn, and unsent outreach emails; renaming is a real branding decision, not a code change — left for deliberate action, not silent rename. |
| `data/sellerflow.db` | `DATABASE_URL` default in `backend/database.py` | The production persistent volume already contains a file at this path. Changing the default would make the app write a new, empty database on next deploy and orphan the existing one. |
| `sellers` table, `/api/sellers/*` routes | `backend/database.py`, `backend/main.py` | Internal/API identifiers, not shown in any UI. Renaming is pure churn with no user-facing benefit. |
| `sf_live_...` API key prefix | `backend/main.py` | Opaque token prefix, not brand text. Rotating it would invalidate a handful of already-issued test keys for no benefit. |
| `SF-XXXXXX` on historical records | Rows created before this rename | New assessments generate `RBF-XXXXXX` (`backend/main.py`, `backend/database.py`); existing rows keep their original ID rather than being mutated. |

## Known gaps

Kept explicit rather than silently absent: no per-user accounts or multi-tenant data isolation (the dashboard is a single shared operator view behind one password); no merchant document upload or AI field extraction; no PDF export (CSV only); no revenue-history time-series input in the current form (see [Data provenance](#data-provenance)); no admin tooling beyond the dashboard; no route-level or end-to-end test coverage (only the financing engine is tested).

Status: pilot. Contact: lehuuhoang1909@gmail.com

---

Built by [Huu Hoang Le](https://linkedin.com/in/huuhoangle).
