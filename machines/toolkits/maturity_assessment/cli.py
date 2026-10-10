"""Maturity assessment CLI.

This toolkit is intentionally light: the questionnaire lives in
``machines/toolkits/maturity_assessment/questionnaire.md`` and the scoring
template in ``scoring-template.csv``. The CLI prints the paths to both,
plus a maturity-level summary.

Five maturity levels (0-4):

- 0 Ad-hoc    -- no defined closed-loop practice.
- 1 Defined   -- closed loops are designed but not automated.
- 2 Measured  -- closed loops run, with metrics collected.
- 3 Managed   -- closed loops are activated, deactivated, and chained.
- 4 Optimised -- closed loops are dynamically choreographed across domains.

CLI usage::

    clam-maturity-assessment --show
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

LEVELS = [
    ("0", "Ad-hoc",    "No defined closed-loop practice."),
    ("1", "Defined",   "Closed loops are designed but not automated."),
    ("2", "Measured",  "Closed loops run, with metrics collected."),
    ("3", "Managed",   "Closed loops are activated, deactivated, and chained."),
    ("4", "Optimised", "Closed loops are dynamically choreographed across domains."),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--show", action="store_true", help="print the questionnaire path")
    parser.add_argument("--score", type=Path, help="score a filled-in CSV scoring template")
    args = parser.parse_args()

    questionnaire = ROOT / "questionnaire.md"
    template = ROOT / "scoring-template.csv"

    if args.score:
        if not args.score.exists():
            print(f"score file not found: {args.score}", file=sys.stderr)
            return 2
        total = 0
        count = 0
        with args.score.open() as f:
            next(f, None)  # skip header
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) >= 4:
                    try:
                        total += int(parts[2])
                        count += 1
                    except ValueError:
                        continue
        if count == 0:
            print("no scored dimensions found", file=sys.stderr)
            return 1
        avg = total / count
        level = LEVELS[min(int(avg), 4)]
        print(f"Average score: {avg:.2f} -> Level {level[0]} ({level[1]}): {level[2]}")
        return 0

    print("CLAM Maturity Assessment Toolkit")
    print(f"  questionnaire:        {questionnaire}")
    print(f"  scoring template:     {template}")
    print()
    print("Maturity levels:")
    for code, name, desc in LEVELS:
        print(f"  {code}  {name:9s}  {desc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())