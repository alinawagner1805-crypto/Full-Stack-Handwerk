# SQL-Konzepte: Vertiefung

Dieses Dokument beschreibt die SQL-Konzepte, die im `GET /stats`-Endpoint
eingesetzt werden. Es ergänzt den Projektbericht und enthält vollständige
Abfragen mit Erklärungen.

---

## GROUP BY, COUNT, AVG

Die Grundaggregation gruppiert alle Predictions nach Ziffer:

```sql
SELECT prediction,
       COUNT(*)                           AS anzahl,
       ROUND(AVG(confidence)::numeric, 4) AS avg_konfidenz
FROM predictions
GROUP BY prediction
ORDER BY prediction;
```

---

## HAVING – Filterung auf Gruppenebene

`HAVING` filtert Gruppen **nach** der Aggregation. Das ist der entscheidende
Unterschied zu `WHERE`, das auf einzelne Zeilen **vor** der Aggregation wirkt:

```sql
-- FALSCH: filtert einzelne Predictions raus → verfälschter Durchschnitt
SELECT prediction, AVG(confidence)
FROM predictions
WHERE confidence < 0.80
GROUP BY prediction;

-- RICHTIG: verwirft ganze Gruppen nach der Aggregation
SELECT prediction, AVG(confidence)
FROM predictions
GROUP BY prediction
HAVING AVG(confidence) < 0.80
ORDER BY AVG(confidence) ASC;
```

Im Endpoint als Parameter: `GET /stats?confidence_below=0.80`

---

## CAST AS DATE – Zeitreihe

Der `DateTime`-Wert in `created_at` wird auf den Datumsteil reduziert,
um Predictions tagesweise zu aggregieren:

```sql
SELECT created_at::date                    AS tag,
       COUNT(*)                            AS anzahl,
       ROUND(AVG(confidence)::numeric, 4)  AS avg_konfidenz
FROM predictions
GROUP BY tag
ORDER BY tag;
```

In SQLAlchemy: `cast(Prediction.created_at, Date).label("day")`

---

## Window Function – RANK()

Eine Window Function berechnet den Rang jeder Prediction innerhalb ihrer
Zifferngruppe, **ohne** die Zeilen zu kollabieren:

```sql
SELECT id,
       prediction,
       confidence,
       RANK() OVER (
           PARTITION BY prediction
           ORDER BY confidence DESC
       ) AS rang_in_gruppe
FROM predictions;
```

Unterschied zu `GROUP BY`: Alle Originalzeilen bleiben erhalten, der Rang
wird als zusätzliche Spalte angehängt. Damit lässt sich z.B. die
konfidenzstärkste Erkennung pro Ziffer identifizieren.

---

## Filterparameter

Alle Parameter sind optional und kombinierbar:

| Parameter | Beispiel | Wirkung |
|---|---|---|
| `model_version` | `?model_version=v1` | Nur Predictions von v1 |
| `since` | `?since=2026-01-01` | Nur Predictions ab diesem Datum |
| `confidence_below` | `?confidence_below=0.80` | Nur Gruppen unter Schwellenwert |
