from pydantic import BaseModel
from typing import Optional


class DigitStats(BaseModel):
    count: int
    avg_confidence: float

    class Config:
        from_attributes = True


class DayStats(BaseModel):
    date: str
    count: int
    avg_confidence: float

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_predictions: int
    avg_confidence: float
    by_digit: dict[str, DigitStats]
    by_day: list[DayStats]

    class Config:
        from_attributes = True


class PredictionOut(BaseModel):
    id: int
    prediction: str
    confidence: float
    model_version: str
    created_at: str

    class Config:
        from_attributes = True
