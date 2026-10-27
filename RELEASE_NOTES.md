## v1.5.1 — Digest CLI and already-closed day fix

- `aiflow digest` supports `--date`, `--format html`, `--send`, `--force-send`, `--json`.
- `aiflow day end` generates and optionally sends the digest even if the day is already closed.
- Explicit force-send overrides the successful-delivery guard; default deduplication remains.

## v1.5.0 — Project-scoped automatic daily email

- `aiflow day end` creates a project-specific HTML and plain-text digest and sends it via SMTP by default when credentials are configured.
- `aiflow day end --no-digest` suppresses email while preserving the local report.
- Daily metrics include tracked time, Epic/Task state and activity, decisions, approvals, checkpoints and event timeline.
- Report files and delivery state are saved in `.aiflow/state/digest/`; duplicate successful sends are prevented and SMTP errors never block day closure.
- Configure SMTP using environment variables documented in `DAILY_DIGEST.md`.

## v1.4.3 — Installation and PATH consistency

- Installer and upgrade report duplicate `aiflow` executables and shell PATH shadowing.
- Canonical launcher is `~/.local/bin/aiflow`; installer creates the symlink when absent and preserves conflicting existing files or symlinks with a warning.
- `aiflow doctor` reports the active PATH executable and warns about stale `.ai/` references in project-local Codex/Claude instructions and installed AIFlow skills.
- To fix PATH precedence: `export PATH="$HOME/.local/bin:$PATH"` and refresh the shell command cache (`hash -r` in bash, `rehash` in zsh).
- Existing `.aiflow/` project data is unchanged.

## v1.4.2 — Canonical project directory

- New projects use `.aiflow/` instead of `.ai/` for all framework state, configuration, SQLite database, Epic and Task Markdown, decisions, checkpoints, and adoption reports.
- Codex and Claude integration paths, bundled skills, project documentation, and test fixtures follow the canonical directory.
- No automatic migration: if a legacy `.ai/` directory exists, the CLI stops with an explicit error to avoid creating a second project state. Back up and rename the directory manually if needed.
- The global framework installation location and upgrade command are unchanged.

## v1.4.1 — Safe adoption after initialization

- Fix: `aiflow adopt --apply --force` now works after `aiflow init` without rerunning initialization.
- Existing `.aiflow/config.json`, database, selected profiles, Epic/Task documents and project specifications remain untouched.
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
