# SellerFlow

SellerFlow is a B2B SaaS demo for ecommerce seller credit decisioning in Southeast Asia. It combines a FastAPI API, SQLite portfolio store, synthetic ML baseline, and a single-file dark editorial frontend.

## Stack

- Backend: Python 3.11, FastAPI, SQLite
- ML: Random Forest + Logistic Regression ensemble
- Frontend: single-file HTML/CSS/vanilla JS
- Deployment: Railway

## Run Locally

```bash
./start.sh
```

Open:

- App: http://localhost:8000
- API docs: http://localhost:8000/api/docs
- Lender dashboard password: `demo2025`

## API

```bash
curl http://localhost:8000/api/health
```

Submit an assessment:

```bash
curl -X POST http://localhost:8000/api/sellers/submit \
  -H "Content-Type: application/json" \
  -d '{
    "shop_name": "Thời Trang Linh Chi",
    "platform": "Shopee",
    "owner_name": "Nguyễn Thị Linh Chi",
    "phone": "0901234567",
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

## Railway Deploy

```bash
railway login
railway init
railway up
railway domain
```

Railway uses `railway.toml`; health checks run against `/api/health`.
