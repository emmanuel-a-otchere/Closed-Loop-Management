# CLAM Maturity Model

A non-technical toolkit for assessing a closed-loop deployment's
maturity. Two artefacts:

1. **Questionnaire** (`questionnaire.md`) -- 10 dimensions, each scored
   0-4. Designed to be filled in by an interview with the team that
   operates the closed loops, not by an automated scanner.
2. **Scoring template** (`scoring-template.csv`) -- machine-readable
   scoring sheet. Same 10 dimensions; one row per dimension. The CLI
   averages the dimension scores to derive the overall maturity level.

## Maturity levels

| Level | Name | Description |
| --- | --- | --- |
| 0 | Ad-hoc | No defined closed-loop practice. |
| 1 | Defined | Closed loops are designed but not automated. |
| 2 | Measured | Closed loops run, with metrics collected. |
| 3 | Managed | Closed loops are activated, deactivated, and chained. |
| 4 | Optimised | Closed loops are dynamically choreographed across domains. |

## How to run

1. Open `questionnaire.md` and interview the operations team.
2. Record each dimension's score (0-4) in `scoring-template.csv`.
3. Run `clam-maturity-assessment --score scoring-template.csv` to derive
   the overall level.

The toolkit is deliberately simple. The value is the shared vocabulary,
not the scoring formula.