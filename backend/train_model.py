import os
import sys
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from generate_data import generate_seller_data, FEATURES

BASE_DIR = os.path.dirname(__file__)
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

MODEL_FILES = ['rf_model.pkl', 'lr_model.pkl', 'scaler.pkl', 'feature_importance.pkl']


def models_exist():
    return all(os.path.exists(os.path.join(MODELS_DIR, f)) for f in MODEL_FILES)


def main(skip_if_exists=False):
    if skip_if_exists and models_exist():
        print('Models already present — skipping training.')
        return

    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    csv_path = os.path.join(DATA_DIR, 'sellers.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = generate_seller_data()
        df.to_csv(csv_path, index=False)

    X = df[FEATURES]
    y = df['defaulted']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    rf = RandomForestClassifier(
        n_estimators=300, max_depth=8, min_samples_leaf=10,
        class_weight='balanced', random_state=42
    )
    rf.fit(X_train, y_train)
    rf_auc = roc_auc_score(y_test, rf.predict_proba(X_test)[:, 1])

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    lr = LogisticRegression(max_iter=1000, class_weight='balanced')
    lr.fit(X_train_scaled, y_train)
    lr_auc = roc_auc_score(y_test, lr.predict_proba(X_test_scaled)[:, 1])

    ensemble_proba = rf.predict_proba(X_test)[:, 1] * 0.65 + lr.predict_proba(X_test_scaled)[:, 1] * 0.35
    ensemble_auc = roc_auc_score(y_test, ensemble_proba)

    feature_importance = dict(zip(FEATURES, rf.feature_importances_))

    joblib.dump(rf, os.path.join(MODELS_DIR, 'rf_model.pkl'))
    joblib.dump(lr, os.path.join(MODELS_DIR, 'lr_model.pkl'))
    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler.pkl'))
    joblib.dump(feature_importance, os.path.join(MODELS_DIR, 'feature_importance.pkl'))

    print(f'RF AUC:       {rf_auc:.4f}')
    print(f'LR AUC:       {lr_auc:.4f}')
    print(f'Ensemble AUC: {ensemble_auc:.4f}')
    print('Feature importance:')
    for f, imp in sorted(feature_importance.items(), key=lambda x: -x[1]):
        print(f'  {f:<20} {imp:.2%}')
    print(f'Saved models to {MODELS_DIR}')


if __name__ == '__main__':
    main(skip_if_exists='--skip-if-exists' in sys.argv)
