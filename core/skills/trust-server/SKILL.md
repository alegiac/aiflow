---
name: trust-server
description: Accesso controllato a server remoti, esclusivamente dopo autorizzazione esplicita per ogni intervento.
---
# trust-server

## Finalità
Ispezionare o intervenire su server di test, staging o produzione esclusivamente su richiesta dell'utente. L'installazione della skill non concede permessi.

## Prima di ogni accesso
1. Identificare host/ambiente, operazione, impatto, comandi previsti, verifiche e rollback.
2. Presentare il piano e ottenere **autorizzazione esplicita e nuova dell'utente** per questa destinazione e questi comandi, anche per operazioni di sola lettura.
3. Rispettare i permessi dell'ambiente host, della CLI e degli strumenti. Non aggirare sandbox o richieste di conferma.
4. Se cambia il piano, la destinazione o emergono rischi, fermarsi e richiedere nuova autorizzazione.

## Durante l'intervento
Usare minimo privilegio. Non eseguire automaticamente deploy, restart, migrazioni, cancellazioni, modifiche di produzione o accessi a dati sensibili. Non stampare o salvare segreti. Interrompere in caso di errore imprevisto.

## Dopo l'intervento
Registrare ambiente, timestamp, piano autorizzato, azioni effettive, verifiche, esito e problemi in report Task/logbook, senza segreti. Non dichiarare successi non verificati.

## Integrazione
Skill installabile per Codex e Claude Code, ma **mai invocata automaticamente** da hook, session recovery, task, checkpoint o approvazioni documentali. `aiflow approve` non è autorizzazione a operare sui server.

## Limite della versione
Questa è una nuova specifica di sicurezza, non una copia della skill personale originale dell'utente, che non è stata fornita. L'installer preserva le versioni preesistenti.
