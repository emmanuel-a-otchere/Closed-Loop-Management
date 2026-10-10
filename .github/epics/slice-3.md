# Epic -- Slice 3: ClosedLoopLink + Choreography

**Milestone:** v1.0.0 MVP
**Issue:** #3 (file after Slice 2 lands)
**Cards (Kanban):** see http://192.168.50.160:7000/board/14

## Goal

CRUD ClosedLoopLink instances and validate daisy-chain / hierarchical /
feedback interlinks between closed loops. Surface the conflict-resolution
and resource-allocation concerns that the 2022 README assigned to the
"Closed Loop Choreographer" sub-function (3.4).

## Acceptance criteria

- [ ] `POST/GET/DELETE /api/v1/closedLoop/{id}/link`
- [ ] Discriminated union on `kind`: `DAISY_CHAIN | HIERARCHICAL | FEEDBACK`.
- [ ] Cross-link validation: when both endpoints reference the same
      closed loop, the API surfaces a `closed_loop.link_cycle` error.
- [ ] Condition (CEL-like) syntax is parsed but not executed; stored
      verbatim. Execution engine lands in Slice 4.
- [ ] 10+ new pytest tests.

## Non-goals (Slice 3)

- Condition execution (Slice 4).
- Cross-loop runtime (Slice 4).