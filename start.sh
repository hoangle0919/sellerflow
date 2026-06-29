#!/bin/bash
echo "SellerFlow — Starting..."
cd "$(dirname "$0")/backend"
pip install -r requirements.txt -q --break-system-packages 2>/dev/null \
  || pip install -r requirements.txt -q

if [ ! -f "models/rf_model.pkl" ]; then
  echo "Training models..."
  python3 train_model.py
fi

echo "  App:       http://localhost:8000"
echo "  API docs:  http://localhost:8000/docs"
echo "  Dashboard: password = vietcredit"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
