---
name: aiflow-help
description: Mostra l’aiuto contestuale AIFlow quando l’utente scrive «aiflow?», «ai flow?», «help aiflow» o chiede cosa può fare con AIFlow.
---
# AIFlow — aiuto conversazionale

## Trigger
Quando l’utente scrive **`aiflow?`**, **`ai flow?`**, **`help aiflow`**, **`cosa posso fare con aiflow`**, o invoca esplicitamente questa skill, mostra subito lo specchietto qui sotto. Non avviare analisi, Epic, Task o sessioni per rispondere all’help. Non chiedere autorizzazioni solo per mostrare aiuto.

## Prima di rispondere
- Se sei nella radice di un progetto AIFlow, esegui `aiflow status` (sola lettura) per contestualizzare. Se disponibile, leggi `.aiflow/state/current.md` per identificare Epic, Task e sessione correnti. Non presumere stati o comandi supportati.
- Se la CLI non è disponibile, mostra comunque l’help generale e spiega brevemente che lo stato non è verificabile.
- Usa `aiflow --help` per verificare la sintassi effettiva prima di suggerire comandi terminale. Per richieste in linguaggio naturale, l’agente può tradurre l’intento in comandi CLI esistenti.

## Specchietto da mostrare
| Area | Cosa puoi chiedermi |
| --- | --- |
| Progetto | «Mostrami lo stato AIFlow», «Controlla la configurazione» |
| Analisi | «Avvia analitica», «Riprendi l’intervista» |
| Epic | «Crea una Epic», «Mostra la Epic corrente», «Concludi la Epic» |
| Task | «Proponi i Task», «Avvia il Task», «Prepara la review», «Chiudi il Task» |
| Sessioni | «Avvia una sessione», «Chiudi la sessione», «Riprendi dal checkpoint» |
| Decisioni | «Mostra le decisioni aperte», «Registra questa decisione», «Approva questa proposta» |
| Tracking | «Mostra il resoconto», «Esporta attività in CSV» |
| Server | «Mostrami come funziona trust-server» (accesso remoto solo con autorizzazione esplicita) |

Dopo la tabella mostra **Stato attuale** con dati realmente letti, oppure «Stato non disponibile», e **Prossimo passo suggerito** basato sullo stato, formulato come proposta, mai eseguito automaticamente. Mantieni la risposta compatta. Per approvazioni, non dedurre consenso dalla richiesta di help.


## Governance condivisa (v1.1)
Le decisioni GLOBAL valgono per tutti i progetti, PLATFORM:php-laravel per i progetti Laravel. Prima dell'analisi leggi `aiflow decision list` e applica le decisioni approvate pertinenti. Non trasformare le proposte in vincoli. Se una decisione locale confligge con una condivisa approvata, fermati e chiedi conferma prima di procedere. Per approvare una decisione condivisa usa `aiflow decision approve ID --ref GLOBAL|PLATFORM:php-laravel --by ... --evidence ...`.
