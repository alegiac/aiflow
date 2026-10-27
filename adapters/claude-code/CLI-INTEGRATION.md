# Claude Code + AIFlow

La CLI è la stessa usata da Codex: installare `aiflow` nel PATH e usarla dalla directory del progetto. Per creare un'Epic eseguire `aiflow epic create "Titolo"`, per i Task `aiflow task create <EPIC-ID> "Titolo"`. Claude Code deve poi redigere e aggiornare `.aiflow/epics/<ID>/analysis.md`, `ux.md`, `tasks/<ID>/task.md` e `report.md` mediante discussione con l'utente.

Le decisioni si registrano come bozze con `aiflow note decision`, non si considerano approvate per implicazione. Per lo stato `approved` o `completed` usare `--confirm` solo a fronte di conferma esplicita. La configurazione dei comandi/skill nativi Claude Code è ancora da testare.
