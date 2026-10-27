# Profilo shadcn/ui

## Ambito e rilevamento
- shadcn/ui component sources and configuration; detect components.json and installed component sources.
- Apply only when explicitly selected or confirmed from project evidence. Determine versions from manifests; never invent versions.

## Organizzazione del codice
- Reuse project-owned components and design tokens; compose primitives; preserve accessible states, labels, focus and keyboard support.
- Follow established repository structure; avoid introducing competing architectural patterns.

## Dipendenze e toolchain
- Verify supported React framework, Tailwind integration and existing component installation before adding dependencies.
- Ask for approval before adding major dependencies or changing the framework.

## Testing e qualità
- Test forms, dialogs, keyboard navigation and responsive states with project tools.
- Report executed commands and results; never claim tests passed without running them.

## Sicurezza e dati
- Keep user input validation server-side; avoid unsafe HTML and client-only authorization.
- Do not store credentials or production customer data in AIFlow Markdown artifacts.

## Deployment e operatività
- Validate production build and styles; never overwrite customized generated components without review.
- Never push, deploy, run destructive migrations or modify live services without explicit authorization.

## Interazione con AIFlow
- Works with react and tailwind profiles; if prerequisites absent, report and request approval rather than silently installing.
- Record stack-specific assumptions in analysis, decisions in the approved workflow, and test evidence in task reports.
- Multiple active profiles are complementary; when rules conflict, stop and ask the developer.

## Riferimenti
- https://ui.shadcn.com/docs
