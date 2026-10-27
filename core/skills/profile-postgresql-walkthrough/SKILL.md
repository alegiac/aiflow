# AIFlow postgresql profile walkthrough

## Purpose
Provide a complete, interactive, read-only walkthrough of the bundled `postgresql` technology profile. This is educational guidance, not permission to modify project files or make architectural decisions.

## Invocation
- Codex: invoke the installed `aiflow-profile-postgresql-walkthrough` skill.
- Claude Code: invoke the installed `aiflow-profile-postgresql-walkthrough` skill.
- CLI equivalent: `aiflow profile walkthrough postgresql`.

## Procedure
1. Run `aiflow profile walkthrough postgresql` or read the installed `profiles/postgresql/PROFILE.md` source directly. Do not invent rules or treat other profiles as this profile.
2. Explain **every** heading and every rule in source order, including applicability, architecture, dependencies, tests, security, operations, and AIFlow workflow interactions. Quote brief rules and explain practical implications in the user's language.
3. For each section, provide a concrete implementation example relevant to the current project when evidence exists; otherwise label examples as hypothetical.
4. Explain how the profile interacts with the other active profiles from `.ai/config.json` if a project is initialized. Identify conflicts and missing prerequisites rather than resolving them silently.
5. Pause for questions at the user's request, and offer a section-by-section walkthrough. Never claim that a dependency is installed or a test passed without checking.
6. Do not write project files, install dependencies, run migrations, push commits, or deploy as part of the walkthrough.

## Source of truth
The installed `profiles/postgresql/PROFILE.md` is authoritative. If a rule is absent, say so; do not present generic recommendations as profile requirements.
