# Profilo MySQL

## Ambito e rilevamento
- MySQL databases, InnoDB and migration files; inspect DSN, drivers and migration config.
- Apply only when explicitly selected or confirmed from project evidence. Determine versions from manifests; never invent versions.

## Organizzazione del codice
- Prefer InnoDB, parameterized queries, explicit constraints and transactions; design indexes from actual query patterns.
- Follow established repository structure; avoid introducing competing architectural patterns.

## Dipendenze e toolchain
- Confirm server major version, SQL modes, character sets and ORM compatibility.
- Ask for approval before adding major dependencies or changing the framework.

## Testing e qualità
- Test migration reversibility, deadlocks, unique constraints, transaction boundaries and EXPLAIN plans.
- Report executed commands and results; never claim tests passed without running them.

## Sicurezza e dati
- Least-privilege DB credentials, secrets outside repo, careful data retention and safe backups.
- Do not store credentials or production customer data in AIFlow Markdown artifacts.

## Deployment e operatività
- Review table locks, online migration constraints and rollback before applying schema changes.
- Never push, deploy, run destructive migrations or modify live services without explicit authorization.

## Interazione con AIFlow
- Can coexist with postgresql when separate databases have explicit responsibilities; never silently convert one engine to the other.
- Record stack-specific assumptions in analysis, decisions in the approved workflow, and test evidence in task reports.
- Multiple active profiles are complementary; when rules conflict, stop and ask the developer.

## Riferimenti
- https://dev.mysql.com/doc/refman/8.4/en/
