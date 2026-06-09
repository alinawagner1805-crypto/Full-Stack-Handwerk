"""
seed_db_v2.py – Fuellt die predictions-Tabelle mit 200 weiteren Eintraegen
fuer Modellversion v2. Die Konfidenzen sind bewusst hoeher angesetzt als
bei v1, um einen sinnvollen Baseline-Vergleich zu ermoeglichen.

Verwendung:
    1. Zuerst seed_db.py ausfuehren (v1-Daten)
    2. Snapshot speichern:
         curl -s http://localhost:8000/stats > stats_baseline.json
    3. Dieses Skript ausfuehren (v2-Daten hinzufuegen)
    4. Zweiten Snapshot speichern:
         curl -s http://localhost:8000/stats > stats_current.json
    5. Vergleichen:
         python compare_stats.py stats_baseline.json stats_current.json
"""
import random
from datetime import datetime, timedelta

from app.database import SessionLocal, engine
from app.models import Base, Prediction

Base.metadata.create_all(bind=engine)

DIGITS = [str(i) for i in range(1, 10)]

# v2 ist generell besser -- hoehere Basis-Konfidenz
# Ziffern 6, 8, 9 waren bei v1 schwach, v2 verbessert sie spuerbar
CONFIDENCE_PROFILE = {
    "1": (0.91, 0.99),
    "2": (0.88, 0.97),
    "3": (0.87, 0.96),
    "4": (0.86, 0.95),
    "5": (0.85, 0.95),
    "6": (0.83, 0.93),  # bei v1 war das ~0.75
    "7": (0.90, 0.98),
    "8": (0.82, 0.92),  # bei v1 war das ~0.76
    "9": (0.81, 0.91),  # bei v1 war das ~0.74
}

db = SessionLocal()

try:
    entries = []
    for _ in range(200):
        digit = random.choice(DIGITS)
        low, high = CONFIDENCE_PROFILE[digit]
        confidence = round(random.uniform(low, high), 4)

        # v2-Daten liegen zeitlich nach den v1-Daten
        days_ago = random.randint(0, 14)
        entries.append(
            Prediction(
                prediction=digit,
                confidence=confidence,
                model_version="v2",
                created_at=datetime.utcnow() - timedelta(
                    days=days_ago,
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                ),
            )
        )

    db.bulk_save_objects(entries)
    db.commit()
    print(f"OK: {len(entries)} v2-Predictions eingespielt.")
    print("Naechster Schritt: curl -s http://localhost:8000/stats > stats_current.json")
finally:
    db.close()
