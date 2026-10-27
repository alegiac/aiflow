# Codex CLI + AIFlow

Installare `aiflow` nel PATH e operare nella root del progetto. L'agente deve invocare la CLI tramite il proprio terminale quando l'utente chiede creazione, stato o tracking. Esempi:

- «Crea Epic per autenticazione»: `aiflow epic create "Autenticazione"` e poi aprire `.aiflow/epics/<ID>/analysis.md` per l'analisi interattiva.
- «Crea Task»: `aiflow task create <EPIC-ID> "Titolo"`, poi completare `task.md` con requisiti e acceptance criteria approvati.
- «Checkpoint»: `aiflow note checkpoint "..." --ref <EPIC-ID/TASK-ID>`.
- «Chiudi Task»: aggiornare `report.md`, verificare test e approvazione, poi `aiflow task status <EPIC-ID> <TASK-ID> completed --confirm` solo dopo conferma esplicita.

Non confondere il comando CLI con uno slash-command nativo di Codex: il mapping delle skill e la loro installazione richiedono ancora collaudo. Non attribuire alla CLI capacità di generazione AI.
