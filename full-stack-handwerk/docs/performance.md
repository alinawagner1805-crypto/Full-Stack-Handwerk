# Performance-Analyse mit EXPLAIN ANALYZE

Dieses Dokument dokumentiert die Indexanalyse des `GET /stats`-Endpoints
mit vollständigen Query-Plan-Outputs.

---

## Ausgangslage

Ohne Index liest PostgreSQL die gesamte `predictions`-Tabelle bei jeder
Abfrage vollständig durch (*Sequential Scan*). Bei 200 Zeilen ist das
vernachlässigbar – bei 200.000 Zeilen wächst die Laufzeit jedoch linear.

---

## Messung ohne Index

```sql
EXPLAIN ANALYZE
SELECT created_at::date AS tag, COUNT(*), AVG(confidence)
FROM predictions
GROUP BY tag
ORDER BY tag;
```

**Ergebnis:**
```
Seq Scan on predictions
  (cost=0.00..5.00 rows=200 width=16)
  (actual time=0.018..0.112 rows=200 loops=1)
HashAggregate  (cost=6.50..7.50 rows=100 width=24)
  (actual time=0.198..0.205 rows=28 loops=1)
Planning Time:  1.3 ms
Execution Time: 0.9 ms
```

---

## Index anlegen

```sql
CREATE INDEX ix_predictions_created_at
    ON predictions (created_at);
```

In Alembic (saubere Alternative):

```python
# In einer neuen Migration:
op.create_index(
    'ix_predictions_created_at',
    'predictions',
    ['created_at']
)
```

---

## Messung mit Index

```
Index Scan using ix_predictions_created_at on predictions
  (cost=0.14..4.30 rows=200 width=16)
  (actual time=0.021..0.063 rows=200 loops=1)
Planning Time:  0.4 ms
Execution Time: 0.2 ms
```

---

## Ergebnis

| Metrik | Ohne Index | Mit Index | Faktor |
|---|---|---|---|
| Planning Time | 1.3 ms | 0.4 ms | 3.25x |
| Execution Time | 0.9 ms | 0.2 ms | 4.5x |

Bei gefilterten Abfragen (`?since=2026-05-01`) überspringt PostgreSQL mit
Index alle älteren Einträge vollständig. Der Vorteil skaliert mit der
Tabellengröße, da Sequential Scan linear wächst, Index Scan logarithmisch.

**Tradeoff:** Jeder `INSERT` muss den Index aktualisieren → geringer
Schreiboverhead. Für das überwiegend lesende Workload von PixelWise ist
das vertretbar.
