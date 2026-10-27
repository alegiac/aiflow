# Profilo Tailwind CSS

## Ambito e rilevamento
- Tailwind CSS utility-first styling; detect package dependency, @import tailwindcss or tailwind.config.*.
- Apply only when explicitly selected or confirmed from project evidence. Determine versions from manifests; never invent versions.

## Organizzazione del codice
- Prefer existing utilities, design tokens and shared components; avoid redundant classes and unnecessary @apply.
- Follow established repository structure; avoid introducing competing architectural patterns.

## Dipendenze e toolchain
- Respect installed Tailwind major version (v3 config vs v4 CSS-first) and existing bundler.
- Ask for approval before adding major dependencies or changing the framework.

## Testing e qualità
- Check responsive breakpoints, dark mode, contrast, keyboard focus and production CSS output.
- Report executed commands and results; never claim tests passed without running them.

## Sicurezza e dati
- Do not interpolate untrusted input into arbitrary class names or dynamic style values.
- Do not store credentials or production customer data in AIFlow Markdown artifacts.

## Deployment e operatività
- Confirm content scanning and generated CSS in production; avoid unreviewed design changes.
- Never push, deploy, run destructive migrations or modify live services without explicit authorization.

## Interazione con AIFlow
- Compose with React and shadcn; do not assume a frontend framework from Tailwind alone.
- Record stack-specific assumptions in analysis, decisions in the approved workflow, and test evidence in task reports.
- Multiple active profiles are complementary; when rules conflict, stop and ask the developer.

## Riferimenti
- https://tailwindcss.com/docs
