# Profilo Shopify Admin GraphQL API

## Ambito e rilevamento
- Shopify Admin GraphQL queries, mutations, webhooks and bulk operations; detect Shopify clients and explicit scopes.
- Apply only when explicitly selected or confirmed from project evidence. Determine versions from manifests; never invent versions.

## Organizzazione del codice
- Use typed query documents when supported; implement pagination cursors, userErrors handling, idempotent writes and bulk operations for large datasets.
- Follow established repository structure; avoid introducing competing architectural patterns.

## Dipendenze e toolchain
- Pin API version, inspect current schema and use existing GraphQL client; never assume fields exist across versions.
- Ask for approval before adding major dependencies or changing the framework.

## Testing e qualità
- Test throttling/cost budgets, GraphQL top-level errors, mutation userErrors, pagination, webhook replay and partial failures.
- Report executed commands and results; never claim tests passed without running them.

## Sicurezza e dati
- Protect offline/online access tokens, verify webhooks using raw body and HMAC, use minimum scopes, avoid PII in logs.
- Do not store credentials or production customer data in AIFlow Markdown artifacts.

## Deployment e operatività
- Track query cost and API version upgrades; monitor retries, reconciliation and webhook delivery.
- Never push, deploy, run destructive migrations or modify live services without explicit authorization.

## Interazione con AIFlow
- Works with php-laravel or nodejs backends and mysql/postgresql storage; do not couple frontend directly to private Admin API tokens.
- Record stack-specific assumptions in analysis, decisions in the approved workflow, and test evidence in task reports.
- Multiple active profiles are complementary; when rules conflict, stop and ask the developer.

## Riferimenti
- https://shopify.dev/docs/api/admin-graphql
