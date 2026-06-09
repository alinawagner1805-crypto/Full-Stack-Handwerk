#!/bin/bash
# collect_stats.sh – ruft GET /stats auf und speichert den Response als
# datierte JSON-Datei unter /opt/pixelwise/stats_snapshots/.
# Wird taeglich per systemd-Timer ausgefuehrt.
set -euo pipefail

OUTDIR="/opt/pixelwise/stats_snapshots"
mkdir -p "$OUTDIR"

DATE=$(date +%F)
OUTPUT="$OUTDIR/stats_${DATE}.json"

curl -sf http://localhost:8000/stats \
  -H "x-api-key: ${SECRET_API_KEY}" \
  -o "$OUTPUT"

echo "[$(date --iso-8601=seconds)] Snapshot gespeichert: $OUTPUT"
