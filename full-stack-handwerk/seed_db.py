"""
seed_db.py – Füllt die predictions-Tabelle mit 200 zufälligen Einträgen.

Verwendung:
    source .venv/bin/activate
    python seed_db.py
"""
import random
from datetime import datetime, timedelta

from app.database import SessionLocal, engine
from app.models import Base, Prediction

# Schema sicherstellen
Base.metadata.create_all(bind=engine)

DIGITS = [str(i) for i in range(1, 10)]
MODEL_VERSIONS = ["v1", "v1", "v1", "v2"]  # v1 häufiger

db = SessionLocal()

try:
    entries = []
    for _ in range(200):
        digit = random.choice(DIGITS)
        # Einige Ziffern sind schwieriger → niedrigere Confidence
        base_conf = 0.95 if digit not in ("6", "8", "9") else 0.75
        confidence = round(random.uniform(base_conf - 0.15, base_conf), 4)
        days_ago = random.randint(0, 30)

        entries.append(
            Prediction(
                prediction=digit,
                confidence=confidence,
                model_version=random.choice(MODEL_VERSIONS),
                created_at=datetime.utcnow() - timedelta(
                    days=days_ago,
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                ),
            )
        )

    db.bulk_save_objects(entries)
    db.commit()
    print(f"✓ {len(entries)} Predictions erfolgreich eingespielt.")
finally:
    db.close()
