"""
compare_stats.py – Vergleicht zwei Stats-Snapshots und gibt die Differenz
der Durchschnittskonfidenz je Ziffer aus.

Verwendung:
    python compare_stats.py stats_2026-05-01.json stats_2026-06-01.json
"""
import json
import sys


def load(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def main():
    if len(sys.argv) != 3:
        print("Verwendung: python compare_stats.py <baseline.json> <current.json>")
        sys.exit(1)

    baseline = load(sys.argv[1])
    current  = load(sys.argv[2])

    print(f"Gesamt-Predictions : {baseline['total_predictions']:>6}"
          f" -> {current['total_predictions']:>6}")
    print(f"Avg Konfidenz      : {baseline['avg_confidence']:>8.4f}"
          f" -> {current['avg_confidence']:>8.4f}"
          f"  ({current['avg_confidence'] - baseline['avg_confidence']:>+.4f})")
    print()
    print(f"{'Ziffer':<10} {'Vorher':>10} {'Nachher':>10} {'Delta':>10}")
    print("-" * 44)

    for digit, cur in sorted(current["by_digit"].items()):
        prev_data = baseline["by_digit"].get(digit)
        if prev_data is None:
            print(f"{digit:<10} {'--':>10} {cur['avg_confidence']:>10.4f} {'(neu)':>10}")
            continue
        prev  = prev_data["avg_confidence"]
        delta = cur["avg_confidence"] - prev
        print(f"{digit:<10} {prev:>10.4f} {cur['avg_confidence']:>10.4f} {delta:>+10.4f}")


if __name__ == "__main__":
    main()
