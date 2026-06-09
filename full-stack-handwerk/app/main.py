from fastapi import FastAPI, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.database import get_db, engine
from app.models import Base
from app.schemas import StatsResponse
from app.stats import get_stats

# Datenbank-Schema beim Start erstellen (falls nicht vorhanden)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PixelWise Analytics API",
    description="Erweiterung von Block 6: GET /stats – Prediction Analytics Endpoint",
    version="1.0.0",
)


# --- API-Key-Authentifizierung (aus Block 5 übernommen) ---
def verify_api_key(x_api_key: str = Header(...)):
    expected = os.getenv("SECRET_API_KEY", "dev-secret")
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Ungültiger API-Key")


# --- Bestehende Endpunkte (Stub-Kompatibilität) ---
@app.get("/health")
def health():
    return {"status": "ok", "model_version": "v1"}


@app.get("/results")
def results(db: Session = Depends(get_db)):
    from app.models import Prediction
    rows = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(20).all()
    return {
        "results": [
            {
                "id": r.id,
                "prediction": r.prediction,
                "confidence": r.confidence,
                "model_version": r.model_version,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    }


# --- Neuer Analytics-Endpunkt ---
@app.get(
    "/stats",
    response_model=StatsResponse,
    summary="Prediction Analytics",
    description=(
        "Liefert aggregierte Statistiken über alle gespeicherten Predictions. "
        "Optionale Filter: `model_version` und `since` (ISO-Datum)."
    ),
)
def stats_endpoint(
    model_version: Optional[str] = Query(
        default=None,
        description="Filtert auf eine bestimmte Modellversion, z.B. 'v1'",
        example="v1",
    ),
    since: Optional[str] = Query(
        default=None,
        description="Nur Predictions ab diesem Datum (ISO-Format), z.B. '2026-01-01'",
        example="2026-01-01",
    ),
    db: Session = Depends(get_db),
):
    return get_stats(db=db, model_version=model_version, since=since)
