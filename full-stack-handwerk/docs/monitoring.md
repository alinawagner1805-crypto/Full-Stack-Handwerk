# Monitoring: systemd-Timer und Baseline-Vergleich

Dieses Dokument beschreibt die Infrastruktur-Integration des `GET /stats`-
Endpoints über einen automatisierten systemd-Timer.

---

## Motivation

Ein Endpoint der nur auf Anfrage antwortet, erkennt keine Veränderungen über
Zeit. Der systemd-Timer ruft `GET /stats` täglich auf und speichert das
Ergebnis als JSON-Snapshot – damit entsteht ein einfaches Monitoring direkt
auf der bestehenden Serverinfrastruktur (kein zusätzlicher Stack nötig).

---

## Aufbau

### 1. Shell-Skript: `collect_stats.sh`

```bash
#!/bin/bash
set -euo pipefail

OUTDIR="/opt/pixelwise/stats_snapshots"
mkdir -p "$OUTDIR"

DATE=$(date +%F)
OUTPUT="$OUTDIR/stats_${DATE}.json"

curl -sf http://localhost:8000/stats \
  -H "x-api-key: ${SECRET_API_KEY}" \
  -o "$OUTPUT"

echo "[$(date --iso-8601=seconds)] Snapshot gespeichert: $OUTPUT"
```

### 2. systemd Service Unit: `pixelwise-stats.service`

```ini
[Unit]
Description=PixelWise Stats Snapshot

[Service]
Type=oneshot
User=produser
EnvironmentFile=/opt/pixelwise/.env
ExecStart=/opt/pixelwise/collect_stats.sh
```

### 3. systemd Timer Unit: `pixelwise-stats.timer`

```ini
[Unit]
Description=PixelWise Stats täglich um 02:00

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

`Persistent=true` holt verpasste Runs (z.B. nach Neustart) automatisch nach.

### 4. Aktivieren

```bash
sudo cp deploy/pixelwise-stats.service /etc/systemd/system/
sudo cp deploy/pixelwise-stats.timer   /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now pixelwise-stats.timer
systemctl list-timers --all  # Status prüfen
```

---

## Baseline-Vergleich

```bash
# Schritt 1: v1-Daten einspielen, ersten Snapshot speichern
python seed_db.py
curl -s http://localhost:8000/stats > stats_baseline.json

# Schritt 2: v2-Daten hinzufügen, zweiten Snapshot speichern
python seed_db_v2.py
curl -s http://localhost:8000/stats > stats_current.json

# Schritt 3: Vergleich ausgeben
python compare_stats.py stats_baseline.json stats_current.json
```

**Beispielausgabe nach Modellwechsel v1 → v2:**

```
Gesamt-Predictions:  200 -> 487
Avg Konfidenz:    0.8741 -> 0.9012  (+0.0271)

Ziffer     Vorher    Nachher      Delta
1          0.9312     0.9487    +0.0175
6          0.7854     0.8231    +0.0377
9          0.7621     0.8105    +0.0484
```

Die Ausgabe zeigt: v2 verbessert vor allem die schwachen Ziffern 6 und 9,
die bei v1 die niedrigsten Konfidenzen hatten.
