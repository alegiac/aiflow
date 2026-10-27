# AIFlow v0.4 — operational contract

## Sources of truth

- SQLite in `.aiflow/state/aiflow.sqlite3`: IDs, lifecycle state, timestamps, approvals, events and activity tracking.
- `.aiflow/epics/<ID>/epic.md`, `analysis.md`, `ux.md`: functional requirements, UX and scope.
- `.aiflow/epics/<ID>/tasks/<ID>/task.md`, `report.md`: implementation contract and verifiable outcome.
- `.aiflow/epics/<ID>/decisions.md`, `approvals.md`, `checkpoints.md`: durable project evidence.
- `.aiflow/state/checkpoints.md`: chronological recovery journal.

Agents **must not** edit the SQLite database directly or manufacture user confirmations. CLI `--by` and `--evidence` are audit fields, not proof of identity. Approval requires an actual explicit user instruction in the current interaction; agents must not self-approve. All `analysis.md`, `ux.md`, and `task.md` content is authored through discussion and validated against the repository. Never invent business requirements.

## Workflow

1. `aiflow epic create "Title"` (optional `--id`). Inspect repository and draft `analysis.md`, `ux.md`, `epic.md` using `analitica`. **No application code.**
2. Record assumptions as draft prose. For meaningful decisions use `aiflow decision propose EPIC-001 "Statement" --rationale "..."`.
3. When the user explicitly approves, `aiflow decision approve 1 --by "user" --evidence "verbatim or precise reference"`. For scoped approval use `aiflow approve EPIC-001 requirements --by user --evidence "..."`.
4. Once user approves the scoped analysis and proposed Task breakdown, use `aiflow workflow-epic approve EPIC-001 --by user --evidence "..."`; `aiflow task create EPIC-001 "Title"` for approved tasks.
5. `aiflow workflow-task start EPIC-001 TASK-001`, optionally `aiflow session start`, `aiflow track start --epic EPIC-001 --task TASK-001`. Before coding, verify accepted criteria and read project tech profile.
6. Update Task Markdown and `report.md` with actual changes, tests run, impacts and remaining work. Run `aiflow checkpoint EPIC-001/TASK-001 "Completed X" --next "..."` after substantial milestones, before compaction and when interrupted.
7. `aiflow workflow-task review EPIC-001 TASK-001`; request human validation, then `aiflow workflow-task finish EPIC-001 TASK-001 --by user --evidence "..."` only on explicit approval. Stop tracking; export time if desired.
8. Close Epic only after all tasks are completed/cancelled and human approval: `aiflow workflow-epic finish EPIC-001 --by user --evidence "..."`.
9. On context loss, run `aiflow recover`, read referenced documents and reconcile with `git status`. Never assume a chat summary is authoritative.

## Safety and quality

- No implementation during `analitica`. User-approved architecture and acceptance criteria take precedence over generated tests.
- Never commit, push, deploy, use privileged servers, or run external integrations without explicit user permission. `trust-server` is excluded.
- Independent review may be **proposed**, not silently delegated. A review must report issues independently of the authoring agent.
- CLI persistence is not a guarantee of crash-atomic file+DB transactions. Back up and version-control Markdown; use `aiflow doctor` and git diff to detect divergence.
