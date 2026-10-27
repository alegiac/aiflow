## v1.4.1 — Safe adoption after initialization

- Fix: `aiflow adopt --apply --force` now works after `aiflow init` without rerunning initialization.
- Existing `.ai/config.json`, database, selected profiles, Epic/Task documents and project specifications remain untouched.
- Existing adoption reports are not silently overwritten; archive them before retrying.
- `--force` requires `--apply`; a plain `aiflow adopt` remains a safe read-only preview for projects not yet initialized.
- Regression coverage for `init → epic create → adopt --apply --force`.

## v1.4.0 — Daily continuity and living specifications

- `aiflow day start` resumes sessions and synchronizes project documentation.
- `aiflow day end --summary ... --next ...` closes tracking and writes a dated Markdown checkpoint.
- `aiflow adopt` safely previews an existing repository; `--apply` initializes AIFlow and writes reviewable findings. Optional `--conversation` reads an explicit local export; private agent history is not automatically accessible.
- `aiflow epic create` and `aiflow task create` create draft Epic/Task with dedicated Markdown and automatically refresh project inventory.
- `aiflow specs sync` updates the project inventory and consolidates explicitly approved decisions.
- `aiflow specs record project|architecture` appends evidence-backed specification changes.
- Jira/MCP integration is excluded from this release.

# AIFlow v1.1 (candidate)

- Decisioni GLOBAL e PLATFORM con registro persistente centrale, distinte dalle decisioni di progetto.
- Riepilogo giornaliero multi-progetto e invio SMTP opzionale; scheduler locale da configurare.
- Skill analitica/help aggiornate per consultare governance condivisa.
- Non è implementata una sincronizzazione cloud tra macchine o un mail scheduler preconfigurato.
