import os
import numpy as np
import pandas as pd

FEATURES = [
    'monthly_revenue',
    'revenue_growth',
    'order_volume',
    'avg_order_value',
    'return_rate',
    'rating',
    'days_active',
    'inventory_turnover',
    'late_ship_rate',
    'previous_loans',
]


def generate_seller_data(n=3000, seed=42):
    np.random.seed(seed)
    df = pd.DataFrame({
        'seller_id': [f'VN{str(i).zfill(5)}' for i in range(1, n + 1)],
        'monthly_revenue': np.random.lognormal(mean=18.42, sigma=0.75, size=n).round(0),
        'revenue_growth': np.random.uniform(-0.35, 0.90, n).round(4),
        'order_volume': np.random.randint(15, 1200, n),
        'avg_order_value': np.random.lognormal(mean=12.21, sigma=0.5, size=n).round(0),
        'return_rate': np.random.beta(2, 12, n).round(4),
        'rating': np.clip(np.random.normal(4.2, 0.5, n), 1.0, 5.0).round(1),
        'days_active': np.random.randint(30, 1800, n),
        'inventory_turnover': np.random.uniform(0.5, 14.0, n).round(2),
        'late_ship_rate': np.random.beta(1.5, 12, n).round(4),
        'previous_loans': np.random.randint(0, 6, n),
        'platform': np.random.choice(['Shopee', 'TikTok Shop', 'Lazada'], n, p=[0.55, 0.30, 0.15]),
        'category': np.random.choice(['Fashion', 'Electronics', 'Food', 'Beauty', 'Home'], n),
    })

    risk_score = (
        0.28 * (df['return_rate'] / df['return_rate'].max()) +
        0.22 * (1 - (df['rating'] - 1) / 4) +
        0.18 * (df['late_ship_rate'] / df['late_ship_rate'].max()) +
        0.15 * (1 - df['revenue_growth'].clip(-0.35, 0.90).add(0.35) / 1.25) +
        0.10 * (1 - df['days_active'] / 1800) +
        0.07 * (1 - df['inventory_turnover'] / 14)
    )
    noise = np.random.normal(0, 0.08, n)
    df['defaulted'] = ((risk_score + noise) > 0.475).astype(int)
    return df


if __name__ == '__main__':
    os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
    df = generate_seller_data()
    out_path = os.path.join(os.path.dirname(__file__), 'data', 'sellers.csv')
    df.to_csv(out_path, index=False)
    print(f'Generated {len(df)} rows -> {out_path}')
    print(f'Default rate: {df["defaulted"].mean():.2%}')
