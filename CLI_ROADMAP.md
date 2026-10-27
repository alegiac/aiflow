# Roadmap CLI e UI

## Disponibile in v0.2.0-alpha
- CLI Python 3 standard library, menu essenziale e comandi scriptabili.
- Init non distruttivo del progetto, profilo configurabile.
- Epic/Task con ID automatici o espliciti, documenti separati e stato persistente.
- Analisi, UX, criteri di accettazione e report come Markdown editabili dagli agenti.
- Note per decisioni in bozza, checkpoint, logbook.
- Sessioni, tracking tempi, export CSV, status, doctor.
- SQLite per contatori e stato; nessun accesso server.

## Da implementare prima di una release stabile
1. Comandi dedicati per proposte, approvazioni umane tracciate, ADR versionati e impatto sui Task.
2. Stato e recovery ricostruibili dai Markdown, sincronizzazione affidabile e gestione di conflitti Git/SQLite.
3. Installer e aggiornamento skill per Codex e Claude Code; verifica compatibilità e smoke test reali.
4. Workflow interattivi analitica/UX, task review, report automatici basati su dati verificati.
5. Compatibilità con workbook XLSX originale, import/export e reporting tempi.
6. TUI completa e possibile UI web sullo stesso core.
7. Test di concorrenza, migrazioni schema, locking e recovery da crash.
8. Permessi e audit delle approvazioni; `--confirm` attuale è solo un guardrail UX.

`trust-server` è intenzionalmente esclusa.
