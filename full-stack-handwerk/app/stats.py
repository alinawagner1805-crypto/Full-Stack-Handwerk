from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Prediction
from app.schemas import StatsResponse, DigitStats, DayStats
from datetime import datetime
from typing import Optional


def get_stats(
    db: Session,
    model_version: Optional[str] = None,
    since: Optional[str] = None,
) -> StatsResponse:
    """
    Berechnet Aggregations-Statistiken aus der predictions-Tabelle.

    Parameter:
        db            – SQLAlchemy Session
        model_version – optionaler Filter auf Modellversion (z.B. "v1")
        since         – optionaler Datumsfilter, ISO-Format (z.B. "2026-01-01")

    Rückgabe:
        StatsResponse mit Gesamt-Metriken, Aufschlüsselung nach Ziffer und Tag
    """
    query = db.query(Prediction)

    # --- Filter anwenden ---
    if model_version:
        query = query.filter(Prediction.model_version == model_version)
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
            query = query.filter(Prediction.created_at >= since_dt)
        except ValueError:
            # Ungültiges Datumsformat: Filter wird ignoriert
            pass

    # --- Gesamt-Metriken ---
    total = query.count()
    avg_conf_raw = (
        db.query(func.avg(Prediction.confidence))
        .filter(*_build_filters(model_version, since))
        .scalar()
    )
    avg_conf = round(float(avg_conf_raw), 4) if avg_conf_raw is not None else 0.0

    # --- Gruppierung nach Ziffer ---
    by_digit_rows = (
        query
        .with_entities(
            Prediction.prediction,
            func.count().label("cnt"),
            func.avg(Prediction.confidence).label("avg_conf"),
        )
        .group_by(Prediction.prediction)
        .order_by(Prediction.prediction)
        .all()
    )

    # --- Gruppierung nach Tag ---
    by_day_rows = (
        query
        .with_entities(
            func.date(Prediction.created_at).label("day"),
            func.count().label("cnt"),
            func.avg(Prediction.confidence).label("avg_conf"),
        )
        .group_by("day")
        .order_by("day")
        .all()
    )

    return StatsResponse(
        total_predictions=total,
        avg_confidence=avg_conf,
        by_digit={
            r.prediction: DigitStats(
                count=r.cnt,
                avg_confidence=round(float(r.avg_conf), 4),
            )
            for r in by_digit_rows
        },
        by_day=[
            DayStats(
                date=str(r.day),
                count=r.cnt,
                avg_confidence=round(float(r.avg_conf), 4),
            )
            for r in by_day_rows
        ],
    )


def _build_filters(model_version, since):
    """Hilfsfunktion: gibt SQLAlchemy-Filter-Ausdrücke zurück."""
    filters = []
    if model_version:
        filters.append(Prediction.model_version == model_version)
    if since:
        try:
            filters.append(Prediction.created_at >= datetime.fromisoformat(since))
        except ValueError:
            pass
    return filters
