# Profilo Shopify Admin REST API (legacy)

## Ambito e rilevamento
- Existing Shopify Admin REST integrations; inspect API version, app scopes and current endpoint usage. REST Admin API is legacy; prefer GraphQL for new public app development.
- Apply only when explicitly selected or confirmed from project evidence. Determine versions from manifests; never invent versions.

## Organizzazione del codice
- Isolate API clients, DTO-free if repository convention requires, pagination, throttling and idempotent synchronization; preserve existing contracts.
- Follow established repository structure; avoid introducing competing architectural patterns.

## Dipendenze e toolchain
- Use existing HTTP client and authenticated Shopify app/session credentials; pin supported API version.
- Ask for approval before adding major dependencies or changing the framework.

## Testing e qualità
- Mock HTTP failures, pagination, 429, 5xx, retries and webhook duplicates; contract-test supported endpoints.
- Report executed commands and results; never claim tests passed without running them.

## Sicurezza e dati
- Keep tokens server-side; validate webhook HMAC against raw request body; enforce least-privilege scopes and redact logs.
- Do not store credentials or production customer data in AIFlow Markdown artifacts.

## Deployment e operatività
- Observe rate limits, version deprecations and reconciliation jobs; require approval for writes to live shops.
- Never push, deploy, run destructive migrations or modify live services without explicit authorization.

## Interazione con AIFlow
- May coexist with shopify-graphql during migration; do not translate REST endpoints to GraphQL without parity checks.
- Record stack-specific assumptions in analysis, decisions in the approved workflow, and test evidence in task reports.
- Multiple active profiles are complementary; when rules conflict, stop and ask the developer.

## Riferimenti
- https://shopify.dev/docs/api/admin-rest
