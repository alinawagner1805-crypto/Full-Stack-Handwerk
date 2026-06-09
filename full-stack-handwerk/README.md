# Full Stack Handwerk – GET /stats Analytics Endpoint

**Projektbericht-Erweiterung** für den Kurs *Full Stack Handwerk*  
Prof. Dr.-Ing. Mark Schutera · DHBW Ravensburg · Studiengang DSKI

**Basis:** Block 6 – Datenbanken & SQL  
**Erweiterung:** Neuer `GET /stats`-Endpoint mit SQL-Aggregationen, Filterparametern,
Performance-Analyse und automatisiertem Monitoring via systemd-Timer.

---

## Quickstart

```bash
# 1. Repo klonen
git clone https://github.com/alinawagner1805-crypto/Full-Stack-Handwerk.git
cd Full-Stack-Handwerk

# 2. Umgebung einrichten
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Konfiguration
cp .env.example .env
# DATABASE_URL=sqlite:///./pixelwise.db ist bereits voreingestellt

# 4. Datenbank + Testdaten
python init_db.py
python seed_db.py

# 5. Server starten
uvicorn app.main:app --reload --port 8000
```

→ **Swagger UI:** http://localhost:8000/docs  
→ **Endpoint:** http://localhost:8000/stats

---

## Live-Demo

```bash
chmod +x demo/live_demo.sh
./demo/live_demo.sh
```

Das Skript startet automatisch einen lokalen Server, spielt Testdaten ein,
macht mehrere Requests gegen den Endpoint und zeigt abschließend einen
Baseline-Vergleich zwischen Modell v1 und v2.

---

## Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/health` | Liveness-Check |
| GET | `/results` | Letzte 20 Predictions (Basis, Block 6) |
| GET | `/stats` | Aggregierte Statistiken (**Erweiterung**) |
| GET | `/stats?model_version=v1` | Gefiltert nach Modellversion |
| GET | `/stats?since=2026-01-01` | Gefiltert nach Datum |
| GET | `/stats?confidence_below=0.85` | Nur unsichere Zifferngruppen |

---

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [`docs/sql_konzepte.md`](docs/sql_konzepte.md) | GROUP BY, HAVING, CAST, Window Functions – vollständige SQL-Abfragen |
| [`docs/performance.md`](docs/performance.md) | EXPLAIN ANALYZE vor/nach Index – vollständige Query Plans |
| [`docs/monitoring.md`](docs/monitoring.md) | systemd-Timer, Shell-Skript, Baseline-Vergleich |
| [`bericht.tex`](bericht.tex) | LaTeX-Projektbericht (5 Seiten) |

---

## Projektstruktur

```
Full-Stack-Handwerk/
├── app/
│   ├── main.py        # FastAPI App + Endpunkte
│   ├── models.py      # SQLAlchemy Prediction-Modell
│   ├── database.py    # Engine & Session
│   ├── schemas.py     # Pydantic Response-Modelle
│   └── stats.py       # Aggregations-Logik
├── demo/
│   └── live_demo.sh   # Live-Demo aller Endpunkte
├── deploy/
│   ├── pixelwise.service
│   ├── pixelwise-stats.service
│   └── pixelwise-stats.timer
├── docs/
│   ├── sql_konzepte.md
│   ├── performance.md
│   └── monitoring.md
├── init_db.py          # Schema erstellen
├── seed_db.py          # v1-Testdaten (200 Predictions)
├── seed_db_v2.py       # v2-Testdaten (200 Predictions, höhere Konfidenz)
├── compare_stats.py    # Baseline-Vergleich zweier Snapshots
├── collect_stats.sh    # Täglicher Stats-Snapshot (via systemd-Timer)
├── test_stats.py       # Smoke Tests (pytest)
├── bericht.tex         # Projektbericht
└── requirements.txt
```

---

## Tests

```bash
pytest test_stats.py -v
```

---

## Baseline-Vergleich

```bash
# v1-Snapshot
python seed_db.py
curl -s http://localhost:8000/stats > stats_baseline.json

# v2-Daten hinzufügen → zweiter Snapshot
python seed_db_v2.py
curl -s http://localhost:8000/stats > stats_current.json

# Vergleich
python compare_stats.py stats_baseline.json stats_current.json
```
