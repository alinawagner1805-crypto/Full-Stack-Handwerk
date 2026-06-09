#!/bin/bash
# live_demo.sh – Demonstriert den GET /stats Endpoint live.
# Startet einen lokalen Server, spielt Testdaten ein und macht
# mehrere Requests gegen den Endpoint.
#
# Voraussetzung:
#   source .venv/bin/activate
#   pip install -r requirements.txt
#   cp .env.example .env

set -euo pipefail

BASE_URL="http://localhost:8000"
SEPARATOR="─────────────────────────────────────────"

# ── Server starten ────────────────────────────────────────────────────────────
echo ""
echo "==> Datenbank initialisieren..."
python init_db.py

echo "==> v1-Testdaten einspielen (200 Predictions)..."
python seed_db.py

echo "==> Server starten (im Hintergrund)..."
uvicorn app.main:app --port 8000 &
SERVER_PID=$!
sleep 2  # kurz warten bis der Server hochgefahren ist

# Cleanup bei Abbruch
trap "kill $SERVER_PID 2>/dev/null; echo 'Server gestoppt.'" EXIT

# ── Demo-Requests ─────────────────────────────────────────────────────────────
echo ""
echo "$SEPARATOR"
echo "  LIVE DEMO: GET /stats"
echo "$SEPARATOR"

echo ""
echo "1) GET /stats – alle Predictions (v1):"
echo "$SEPARATOR"
curl -s "$BASE_URL/stats" | python3 -m json.tool
echo ""

echo "2) GET /stats?model_version=v1 – nur Modell v1:"
echo "$SEPARATOR"
curl -s "$BASE_URL/stats?model_version=v1" | python3 -m json.tool
echo ""

echo "3) GET /stats?confidence_below=0.85 – unsichere Ziffern:"
echo "$SEPARATOR"
curl -s "$BASE_URL/stats?confidence_below=0.85" | python3 -m json.tool
echo ""

echo "4) GET /stats?since=$(date -d '7 days ago' +%F) – letzte 7 Tage:"
echo "$SEPARATOR"
curl -s "$BASE_URL/stats?since=$(date -d '7 days ago' +%F)" | python3 -m json.tool
echo ""

# ── v2-Daten + Vergleich ──────────────────────────────────────────────────────
echo "$SEPARATOR"
echo "  BASELINE-VERGLEICH: v1 vs. v2"
echo "$SEPARATOR"
echo ""

echo "==> Snapshot v1 speichern..."
curl -s "$BASE_URL/stats" > /tmp/stats_v1.json

echo "==> v2-Testdaten einspielen (200 weitere Predictions)..."
python seed_db_v2.py

echo "==> Snapshot v2 speichern..."
curl -s "$BASE_URL/stats" > /tmp/stats_v2.json

echo ""
echo "==> Vergleich v1 vs. v2:"
echo "$SEPARATOR"
python compare_stats.py /tmp/stats_v1.json /tmp/stats_v2.json

echo ""
echo "$SEPARATOR"
echo "  Swagger UI verfuegbar unter: $BASE_URL/docs"
echo "$SEPARATOR"
echo ""
echo "Druecke ENTER um den Server zu stoppen..."
read -r
