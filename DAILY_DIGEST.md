# Riepilogo quotidiano multi-progetto

La scansione cerca `.ai/state/aiflow.sqlite3` sotto `~/Development`, legge gli eventi del giorno nel fuso Europe/Rome e produce un riepilogo. I progetti fuori da quella cartella richiedono `--projects-root`. Non legge dati da GitHub: i database sono locali.

## Prova senza invio
`python3 tools/daily_digest.py --projects-root ~/Development`

## Invio SMTP
Imposta `AIFLOW_SMTP_HOST`, `AIFLOW_SMTP_PORT` (default 465), `AIFLOW_SMTP_USER`, `AIFLOW_SMTP_PASSWORD`, `AIFLOW_MAIL_TO` e opzionalmente `AIFLOW_MAIL_FROM`, poi esegui `python3 tools/daily_digest.py --send`.

**Non inserire password nel repository, nei file di progetto o nei log.** Configura le variabili in un ambiente protetto (Keychain/secret manager). Per un invio automatico giornaliero su Mac, configura un job `launchd` che esegua questo comando all'ora desiderata con credenziali disponibili in modo sicuro. La mail non viene inviata finché non configuri SMTP e scheduler.

## Decisioni condivise
`aiflow decision propose GLOBAL "..." --rationale "..."`
`aiflow decision propose PLATFORM:php-laravel "Applicare SOLID..." --rationale "..."`
`aiflow decision list`
`aiflow decision approve 1 --ref PLATFORM:php-laravel --by human --evidence "Approvato"`
Gli ID delle decisioni condivise e di progetto sono distinti per registro: usare `--ref` per l'approvazione condivisa.
