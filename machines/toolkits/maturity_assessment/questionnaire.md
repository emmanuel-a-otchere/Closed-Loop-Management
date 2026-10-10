# CLAM Maturity Assessment Questionnaire

Score each dimension from 0 to 4:

- 0: not present
- 1: planned / partial
- 2: defined and documented
- 3: implemented and observed
- 4: measured and continuously improved

Record the scores in `scoring-template.csv` (one row per dimension).

## Dimensions

### 1. Closed-loop inventory

Does the organisation maintain a current inventory of every closed loop
in production? Can a new operator find them in one place?

### 2. Decision-model coverage

Are the closed loops using explicit decision models (OODA, MAPE, or
custom)? Or are decisions implicit in code?

### 3. Goal definition

Does each loop have a measurable goal with a target value, a direction
(AT_LEAST / AT_MOST / EXACTLY), and an owner?

### 4. State lifecycle

Are the closed loops managed via an explicit state machine
(designed -> validated -> published -> active -> paused -> retired)?
Or are loops simply turned on and off without audit?

### 5. Feedback / feedforward separation

Are feedback paths and feedforward paths modeled as separate
workflows? Or are they tangled together?

### 6. Metrics collection

Does each closed loop emit metrics (goal target, current value, drift,
state-transition counts) into a metrics backend?

### 7. Activation / deactivation controls

Can an operator activate or deactivate a closed loop through a managed
control plane (the CLAM API or equivalent)? Or is it via ad-hoc shell
commands?

### 8. Cross-loop interlink

Are closed loops connected to each other (daisy-chained, hierarchical,
or feedback-driven)? Or are they silos?

### 9. Observability

Are logs, metrics, and traces emitted from every closed loop into a
unified observability stack?

### 10. Continuous improvement

Is there a process for retiring, redesigning, or upgrading closed
loops based on observed metrics? Or are they set-and-forget?

## Scoring

Average across all 10 dimensions. The CLAM maturity level is the integer
floor of the average.

| Avg | Level | Name |
| --- | --- | --- |
| 0.0 - 0.5 | 0 | Ad-hoc |
| 0.5 - 1.5 | 1 | Defined |
| 1.5 - 2.5 | 2 | Measured |
| 2.5 - 3.5 | 3 | Managed |
| 3.5 - 4.0 | 4 | Optimised |