import sqlite3, os, uuid, random
from datetime import datetime, timedelta

DB_PATH = os.environ.get("DATABASE_URL", "data/sellerflow.db")


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    # Sellers table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sellers (
            id TEXT PRIMARY KEY,
            shop_name TEXT NOT NULL,
            platform TEXT NOT NULL,
            owner_name TEXT,
            phone TEXT,
            monthly_revenue REAL,
            revenue_growth REAL,
            order_volume INTEGER,
            avg_order_value REAL,
            return_rate REAL,
            rating REAL,
            days_active INTEGER,
            inventory_turnover REAL,
            late_ship_rate REAL,
            previous_loans INTEGER,
            pd_score REAL,
            pd_rf REAL,
            pd_lr REAL,
            decision TEXT,
            credit_limit REAL,
            interest_rate REAL,
            risk_tier TEXT,
            reasoning TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'active'
        )
    """)

    # Waitlist table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS waitlist (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            company TEXT,
            role TEXT,
            position INTEGER,
            created_at TEXT
        )
    """)

    # API keys table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id TEXT PRIMARY KEY,
            key_hash TEXT UNIQUE NOT NULL,
            company TEXT,
            email TEXT,
            plan TEXT DEFAULT 'pilot',
            assessments_used INTEGER DEFAULT 0,
            assessments_limit INTEGER DEFAULT 100,
            created_at TEXT,
            active INTEGER DEFAULT 1
        )
    """)

    # Migration: monthly quota period (YYYY-MM) for databases created before metering
    try:
        conn.execute("ALTER TABLE api_keys ADD COLUMN period TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # column already exists

    # One key issuance per Stripe checkout session (replay protection)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stripe_claims (
            session_id TEXT PRIMARY KEY,
            key_id TEXT,
            email TEXT,
            created_at TEXT
        )
    """)

    conn.commit()

    # Seed sellers if empty
    count = conn.execute("SELECT COUNT(*) FROM sellers").fetchone()[0]
    if count == 0:
        _seed_sellers(conn)

    conn.close()


def _seed_sellers(conn):
    """20 realistic Vietnamese ecommerce sellers with varied risk profiles"""
    import sys
    sys.path.insert(0, os.path.dirname(__file__))

    try:
        import joblib, pandas as pd
        rf     = joblib.load(f"{os.path.dirname(__file__)}/models/rf_model.pkl")
        lr     = joblib.load(f"{os.path.dirname(__file__)}/models/lr_model.pkl")
        scaler = joblib.load(f"{os.path.dirname(__file__)}/models/scaler.pkl")
        models_loaded = True
    except Exception:
        models_loaded = False

    FEATURES = ['monthly_revenue', 'revenue_growth', 'order_volume', 'avg_order_value',
                'return_rate', 'rating', 'days_active', 'inventory_turnover',
                'late_ship_rate', 'previous_loans']

    sellers = [
        # (shop, platform, owner, phone, rev, growth, orders, aov, return, rating, days, inv, late, loans)
        ("Thời Trang Linh Chi",   "Shopee",     "Nguyễn Thị Linh Chi", "0901234567", 185_000_000, 0.22, 420, 440_000, 0.028, 4.9, 680,  6.2, 0.018, 2),
        ("Mỹ Phẩm Hà Nội Store",  "TikTok Shop", "Trần Văn Hà",        "0912345678",  92_000_000, 0.14, 210, 438_000, 0.051, 4.6, 320,  4.1, 0.032, 1),
        ("Điện Tử Minh Tuấn",     "Shopee",     "Lê Minh Tuấn",        "0923456789", 340_000_000, 0.31, 580, 586_000, 0.019, 4.8, 920,  8.5, 0.012, 3),
        ("Đồ Gia Dụng Kim Anh",   "Lazada",     "Phạm Thị Kim Anh",    "0934567890",  65_000_000, 0.05, 145, 448_000, 0.089, 4.1, 185,  2.8, 0.071, 0),
        ("Fashion House VN",      "TikTok Shop", "Hoàng Văn Nam",      "0945678901", 128_000_000, 0.18, 310, 413_000, 0.034, 4.7, 445,  5.4, 0.025, 1),
        ("Thực Phẩm Sạch Hoa",    "Shopee",     "Ngô Thị Hoa",         "0956789012",  48_000_000, -0.08,  98, 490_000, 0.142, 3.8,  95,  3.1, 0.108, 0),
        ("Tech Gadgets Plus",     "Shopee",     "Vũ Đức Long",         "0967890123", 520_000_000, 0.28, 890, 584_000, 0.016, 4.9, 1240, 9.8, 0.009, 4),
        ("Giày Dép Thảo Nguyên",  "TikTok Shop", "Đinh Thị Thảo",      "0978901234",  75_000_000, 0.09, 185, 405_000, 0.062, 4.3, 260,  3.8, 0.048, 1),
        ("Đồng Hồ Cao Cấp VN",    "Shopee",     "Bùi Văn Cao",         "0989012345", 210_000_000, 0.16, 128, 1_640_000, 0.024, 4.8, 780,  4.2, 0.019, 2),
        ("Nội Thất Phong Cách",   "Lazada",     "Trịnh Thị Lan",       "0990123456", 155_000_000, 0.11,  95, 1_630_000, 0.038, 4.5, 560,  3.5, 0.028, 1),
        ("Sách Và Văn Phòng",     "Shopee",     "Lý Văn Thành",        "0901234568",  38_000_000, -0.12, 210, 181_000, 0.178, 3.5,  75,  5.2, 0.142, 0),
        ("Baby & Kids Store",     "TikTok Shop", "Nguyễn Thị Mai",     "0912345679", 168_000_000, 0.24, 485, 346_000, 0.029, 4.8, 590,  6.8, 0.021, 2),
        ("Sport & Fitness VN",    "Shopee",     "Cao Văn Dũng",        "0923456780",  95_000_000, 0.13, 225, 422_000, 0.045, 4.5, 380,  4.9, 0.036, 1),
        ("Hàng Nhập Khẩu Đức",    "Lazada",     "Phan Thị Bích",       "0934567891", 285_000_000, 0.19, 195, 1_462_000, 0.022, 4.7, 850,  3.8, 0.017, 3),
        ("Mỹ Phẩm Hàn Quốc",      "TikTok Shop", "Trương Thị Yến",     "0945678902", 142_000_000, 0.29, 520, 273_000, 0.033, 4.9, 410,  7.2, 0.024, 1),
        ("Đồ Chơi Trẻ Em ABC",    "Shopee",     "Đặng Văn Bình",       "0956789013",  52_000_000, 0.06, 165, 315_000, 0.076, 4.0, 145,  3.2, 0.065, 0),
        ("Phụ Kiện Xe Hơi Pro",   "Lazada",     "Lê Thị Hương",        "0967890124", 195_000_000, 0.21, 308, 633_000, 0.027, 4.6, 720,  5.1, 0.022, 2),
        ("Quần Áo Vintage",       "TikTok Shop", "Vũ Thị Ngọc",        "0978901235",  28_000_000, -0.18,  72, 389_000, 0.212, 3.2,  45,  2.1, 0.186, 0),
        ("Đặc Sản Vùng Miền",     "Shopee",     "Hoàng Thị Cúc",       "0989012346",  88_000_000, 0.17, 295, 298_000, 0.041, 4.6, 490,  5.8, 0.033, 1),
        ("Camera & Photography",  "Shopee",     "Nguyễn Văn Hùng",     "0990123457", 375_000_000, 0.25, 245, 1_531_000, 0.018, 4.9, 1080, 4.6, 0.014, 3),
    ]

    # Spread created_at dates over the last 6 months
    base_date = datetime.now()

    for i, s in enumerate(sellers):
        (shop, plat, owner, phone, rev, grow, orders, aov, ret, rat, days, inv, late, loans) = s
        sid = f"RBF-{str(uuid.uuid4())[:6].upper()}"

        features = {
            'monthly_revenue': rev, 'revenue_growth': grow, 'order_volume': orders,
            'avg_order_value': aov, 'return_rate': ret, 'rating': rat,
            'days_active': days, 'inventory_turnover': inv,
            'late_ship_rate': late, 'previous_loans': loans
        }

        if models_loaded:
            import pandas as pd
            X = pd.DataFrame([{f: features[f] for f in FEATURES}])
            pd_rf = float(rf.predict_proba(X)[0][1])
            pd_lr = float(lr.predict_proba(scaler.transform(X))[0][1])
            pd_s  = round(pd_rf * 0.65 + pd_lr * 0.35, 4)
        else:
            # Simple heuristic fallback
            pd_s = (ret / 0.40) * 0.28 + ((5 - rat) / 4) * 0.20 + (late / 0.40) * 0.18
            pd_s = min(0.99, max(0.01, pd_s))
            pd_rf = pd_s
            pd_lr = pd_s

        if pd_s < 0.25:
            dec, tier, cl, ir = "APPROVED",    "Low Risk",    rev * 0.45, 12.5
        elif pd_s < 0.55:
            dec, tier, cl, ir = "CONDITIONAL", "Medium Risk", rev * 0.20, 18.0
        else:
            dec, tier, cl, ir = "REJECTED",    "High Risk",   0,          0.0

        reasoning = _build_reasoning(dec, features)
        created = (base_date - timedelta(days=random.randint(0, 180))).isoformat()

        conn.execute("""
            INSERT INTO sellers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (sid, shop, plat, owner, phone, rev, grow, orders, aov, ret, rat, days,
              inv, late, loans, pd_s, pd_rf, pd_lr, dec, round(cl, -3), ir, tier, reasoning, created, 'active'))

    conn.commit()


def _build_reasoning(decision, features):
    signals = []
    if features['return_rate'] > 0.10:
        signals.append(f"high return rate ({features['return_rate']:.0%})")
    if features['revenue_growth'] < 0:
        signals.append(f"declining revenue ({features['revenue_growth']:+.0%} MoM)")
    if features['rating'] < 4.0:
        signals.append(f"low store rating ({features['rating']:.1f}/5.0)")
    if features['late_ship_rate'] > 0.08:
        signals.append(f"elevated late shipments ({features['late_ship_rate']:.0%})")

    if decision == "APPROVED":
        return (f"Strong behavioral signals: {features['revenue_growth']:+.0%} MoM growth, "
                f"{features['return_rate']:.0%} return rate, {features['rating']:.1f} star rating. "
                f"Credit limit set at 45% of monthly revenue.")
    elif decision == "CONDITIONAL":
        issues = " and ".join(signals) if signals else "moderate risk indicators"
        return (f"Mixed signals: {issues}. Reduced credit limit applied. "
                f"Recommend monitoring for 60 days.")
    else:
        issues = " and ".join(signals) if signals else "multiple risk factors"
        return (f"Risk threshold exceeded due to {issues}. "
                f"Application does not meet current underwriting criteria.")
