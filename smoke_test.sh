#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE_URL:-http://localhost:8000}"
echo "== health =="
curl -fsS "$BASE/health"; echo
curl -fsS "$BASE/info"; echo
echo "== prediction =="
curl -fsS -X POST "$BASE/predict" -H 'Content-Type: application/json' \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'; echo
echo "== upload =="
curl -fsS -X POST "$BASE/datasets" -F "file=@sample.csv"; echo
echo "== state =="
curl -fsS "$BASE/predictions"; echo
curl -fsS "$BASE/datasets"; echo
