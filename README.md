# SellerFlow

**Credit decisions for sellers banks cannot see.**

SellerFlow is a credit-decisioning platform for Southeast Asian ecommerce merchants. Most Vietnamese sellers have no credit-bureau (CIC) record — but two years of orders, ratings, returns, and delivery performance is a richer behavioral dataset than any bureau file. SellerFlow turns that operational data into a complete credit decision — probability of default, credit limit, interest rate, and plain-language reasoning — through one API call in under a second.

**Live:** https://sellerflow-production.up.railway.app

The model scores; the lender lends. SellerFlow holds no capital and makes no loans.

## How it works

```
seller metrics ──▶ RF + LR ensemble ──▶ PD score ──▶ decision engine ──▶ APPROVED / CONDITIONAL / DECLINED
(revenue, growth,   (scikit-learn)                    (limit, rate,
 returns, ratings,                                     signal flags,
 fulfillment, tenure)                                  reasoning)
```

- **Model:** Random Forest + Logistic Regression ensemble (0.92 AUC on held-out validation data). Trained on a synthetic baseline calibrated to realistic seller distributions; designed for retro-validation on lender loan books.
- **Decision:** PD < 0.25 → approved (limit = 45% of monthly revenue at 12.5%); PD < 0.55 → conditional reduced facility; otherwise declined. Every decision ships with per-signal flags and human-readable reasoning.

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

Free pilot keys (100 assessments/month) are self-serve from the [pricing page](https://sellerflow-production.up.railway.app/#pricing). Full reference: [/api/docs](https://sellerflow-production.up.railway.app/api/docs).

| Endpoint | Auth | Purpose |
|---|---|---|
| `POST /api/sellers/submit` | API key (or rate-limited keyless) | Score a merchant, get a full decision |
| `GET /api/keys/usage` | API key | Quota usage for the current month |
| `POST /api/keys/issue` | — | Self-serve pilot key issuance |
| `GET /api/portfolio` | Session token | Lender portfolio with aggregate risk stats |
| `GET /api/health` | — | Service and model status |

## Stack

- **Backend:** Python 3.11, FastAPI, SQLite (persistent volume in production)
- **ML:** scikit-learn — Random Forest + Logistic Regression ensemble, StandardScaler pipeline
- **Frontend:** single-file HTML/CSS/vanilla JS — no framework, no build step
- **Payments:** Stripe Payment Links; paid checkouts are verified server-side and issue metered API keys automatically
- **Infra:** Railway (Nixpacks), health-checked deploys, models trained at first boot

Security: server-side session auth with expiry, SHA-256-hashed API keys, per-plan monthly quotas, per-IP sliding-window rate limits on every public endpoint, strict Pydantic input validation.

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

## Status

Pilot. The scoring model is a synthetic baseline — output is not a lending commitment or an offer of credit. Contact: hello@sellerflow.io

---

Built by [Huu Hoang Le](https://linkedin.com/in/huuhoangle).
