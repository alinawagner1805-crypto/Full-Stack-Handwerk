"""
init_db.py – Erstellt das Datenbankschema (predictions-Tabelle).

Verwendung:
    source .venv/bin/activate
    python init_db.py
"""
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)
print("✓ Datenbankschema erfolgreich erstellt.")
