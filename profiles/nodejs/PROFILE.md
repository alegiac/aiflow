# Profilo Node.js

## Ambito e rilevamento
- Node.js runtime and backend tooling; detect package.json, engines field, entrypoints and lockfile.
- Apply only when explicitly selected or confirmed from project evidence. Determine versions from manifests; never invent versions.

## Organizzazione del codice
- Use async/await with explicit error handling, bounded concurrency, cancellation and separation of transport/business logic.
- Follow established repository structure; avoid introducing competing architectural patterns.

## Dipendenze e toolchain
- Respect engines, lockfile, package manager and module system (ESM/CJS); do not mix without checking.
- Ask for approval before adding major dependencies or changing the framework.

## Testing e qualità
- Use existing runner (node:test, Vitest, Jest) for unit/integration tests; check graceful shutdown and timeouts.
- Report executed commands and results; never claim tests passed without running them.

## Sicurezza e dati
- Validate input, avoid shell injection and prototype pollution, keep secrets server-side, audit dependencies.
- Do not store credentials or production customer data in AIFlow Markdown artifacts.

## Deployment e operatività
- Set resource limits, health checks, logging and graceful shutdown; no deploy without approval.
- Never push, deploy, run destructive migrations or modify live services without explicit authorization.

## Interazione con AIFlow
- Compose with react build tooling, Shopify GraphQL integrations and databases; nodejs does not imply Express or NestJS.
- Record stack-specific assumptions in analysis, decisions in the approved workflow, and test evidence in task reports.
- Multiple active profiles are complementary; when rules conflict, stop and ask the developer.

## Riferimenti
- https://nodejs.org/en/learn
