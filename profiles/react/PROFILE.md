# Profilo React

## Ambito e rilevamento
- React applications and components; detect react dependency in package.json, JSX/TSX files.
- Apply only when explicitly selected or confirmed from project evidence. Determine versions from manifests; never invent versions.

## Organizzazione del codice
- Use functional components and hooks; keep state closest to consumers; use effects only to synchronize external systems; prefer semantic accessible markup.
- Follow established repository structure; avoid introducing competing architectural patterns.

## Dipendenze e toolchain
- Follow repository package manager and lockfile; use existing router, framework and build tooling.
- Ask for approval before adding major dependencies or changing the framework.

## Testing e qualità
- Test behavior with existing test runner and React Testing Library when available; check keyboard interaction and accessibility.
- Report executed commands and results; never claim tests passed without running them.

## Sicurezza e dati
- Never render unsanitized HTML; validate server input and avoid exposing secrets in browser bundles.
- Do not store credentials or production customer data in AIFlow Markdown artifacts.

## Deployment e operatività
- Validate build, bundle behavior and hydration where SSR is used; deploy only with approval.
- Never push, deploy, run destructive migrations or modify live services without explicit authorization.

## Interazione con AIFlow
- Compose with shadcn, tailwind and nodejs when explicitly enabled; do not assume React implies a particular backend.
- Record stack-specific assumptions in analysis, decisions in the approved workflow, and test evidence in task reports.
- Multiple active profiles are complementary; when rules conflict, stop and ask the developer.

## Riferimenti
- https://react.dev/learn
