# Audit del documento legacy

Fonte: `setup_ai_for_a_project.txt` fornito dall'utente. È una specifica storica, non una regola superiore alle decisioni concordate.

## Da mantenere
- Intervista iniziale e conferma prima della generazione dei file.
- Divieto di inventare contesto, refactor non richiesti e modifiche distruttive.
- Regole su segreti, migration, integrazioni e test.
- Separazione documentazione per umani e contesto per agenti.
- Logbook, recovery e ADR.

## Da modificare
- Sostituire il prompt monolitico con skill a responsabilità limitata.
- Introdurre Epic/Task, analitica, decisioni approvate e checkpoint incrementali.
- Evitare duplicazione tra backlog, logbook, recovery e Task.
- Trasferire assunzioni Laravel 13/Valet/shadcn/sidebar in preferenze di profilo verificabili.
- Non creare un numero fisso di skill o documenti solo per soddisfare una checklist.
- Distinguere le capacità degli adapter dalle regole di processo.

## Non ancora verificato
- Skill originali start/end task e start/end session.
- Formato reale del workbook e rilevazione del tempo.
- Installazione concreta e supporto subagenti delle versioni Codex/Claude Code.
- Skill trust-server: esclusa dal pacchetto per sicurezza.
