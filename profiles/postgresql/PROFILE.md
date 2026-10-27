# Profilo PostgreSQL

## Ambito e rilevamento
- PostgreSQL databases and migrations; detect DSN, migration definitions, drivers or deployment config.
- Apply only when explicitly selected or confirmed from project evidence. Determine versions from manifests; never invent versions.

## Organizzazione del codice
- Use parameterized SQL, explicit transactions, constraints and appropriate indexes; consider JSONB and schema-per-tenant only when required.
- Follow established repository structure; avoid introducing competing architectural patterns.

## Dipendenze e toolchain
- Respect server version, client drivers, migration framework and extensions already deployed.
- Ask for approval before adding major dependencies or changing the framework.

## Testing e qualità
- Test migrations, rollback strategy, query plans (EXPLAIN ANALYZE where safe), isolation and concurrency.
- Report executed commands and results; never claim tests passed without running them.

## Sicurezza e dati
- Apply least-privilege DB roles, protect credentials and personal data; never log secrets.
- Do not store credentials or production customer data in AIFlow Markdown artifacts.

## Deployment e operatività
- Back up before destructive schema operations; validate lock impact, replication and connection pooling.
- Never push, deploy, run destructive migrations or modify live services without explicit authorization.

## Interazione con AIFlow
- Can be used with any backend profile; conflicts with mysql only if both are claimed as the same single datastore without an explicit architecture.
- Record stack-specific assumptions in analysis, decisions in the approved workflow, and test evidence in task reports.
- Multiple active profiles are complementary; when rules conflict, stop and ask the developer.

## Riferimenti
- https://www.postgresql.org/docs/current/
