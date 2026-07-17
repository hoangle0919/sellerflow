#!/bin/bash
set -e

echo ""
echo "  RBF — Starting"
echo ""
cd "$(dirname "$0")/backend"
pip install -r requirements.txt -q --break-system-packages 2>/dev/null || pip3 install -r requirements.txt -q

if [ ! -f "models/rf_model.pkl" ]; then
    echo "  Training models (first run)..."
    python3 train_model.py
fi

echo "  App:       http://localhost:8000"
echo "  API docs:  http://localhost:8000/api/docs"
echo "  Password:  demo2025"
echo ""

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
