# Governance e fonti autorevoli

Priorità: vincoli di sicurezza e autorizzazioni > decisioni/ADR approvati > requisiti Epic approvati > Task approvato > stato/checkpoint > conversazione. In caso di conflitto: fermarsi e chiedere conferma, senza sovrascrivere.

## Decisioni
Ogni decisione ha ID, data, Epic/Task, contesto, alternative, stato (`proposed`, `approved`, `superseded`, `rejected`), motivazione e impatti. L'agente può scrivere bozze, ma solo l'utente approva. L'approvazione può avvenire per gruppo di decisioni. Non attribuire approvazione a un silenzio.

## Checkpoint
Scrivere subito dopo decisioni approvate, cambi di scope, completamento di una fase o prima di una possibile compattazione. Registrare stato, prossimo passo, blocchi, file modificati, test e riferimenti. Dopo compattazione rileggere i documenti pertinenti e dichiarare ciò che non è recuperabile.

## Subagenti
Proporre prima: ruolo, motivo, attività, file in lettura/scrittura, durata della delega, limiti e modalità di review. Attendere autorizzazione esplicita. Un solo writer per documento; nessun subagente può approvare decisioni o acquisire permessi superiori a quelli concessi. In assenza di subagenti, eseguire il processo in sequenza.

## Operazioni sensibili
Niente accessi a server, credenziali, push, deploy, migrazioni distruttive o servizi esterni reali senza autorizzazione specifica e controlli nativi del tool. La skill `trust-server` è esterna e non installata per default. Mai inserire segreti nei Markdown.
