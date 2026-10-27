## Correzione v1.5.1 — generazione manuale e giornata già chiusa

`aiflow digest` stampa il riepilogo del progetto corrente, generando i file HTML e testo. Opzioni: `--date YYYY-MM-DD`, `--format html` (stampa il percorso HTML), `--send` (invio SMTP), `--force-send` (reinvia anche se già inviato). Il digest viene generato anche se `aiflow day end` trova una giornata già chiusa. L'invio non configurato o fallito non impedisce la creazione dei file.

# AIFlow v1.5.0 — Daily Digest per progetto

Quando esegui `aiflow day end --summary "..." --next "..."`, AIFlow genera automaticamente **un report per il progetto corrente** e prova a inviarlo via SMTP. Ogni progetto produce una propria email, non un digest globale. L'invio è predefinito; `--no-digest` salva comunque il report ma salta l'email.

Il report include tempo effettivamente tracciato, Epic e Task creati/aggiornati/chiusi/aperti, decisioni, approvazioni, checkpoint e cronologia degli eventi registrati. Le metriche sono basate sui dati locali e non inventano tempi o risultati non registrati. La durata delle attività attraversate dalla mezzanotte viene conteggiata solo per la parte ricadente nella data richiesta.

## SMTP

Configura nel tuo ambiente protetto `AIFLOW_SMTP_HOST`, `AIFLOW_SMTP_USER`, `AIFLOW_SMTP_PASSWORD`, `AIFLOW_MAIL_TO`; facoltativi `AIFLOW_SMTP_PORT` (default 465), `AIFLOW_MAIL_FROM`, `AIFLOW_DIGEST_TIMEZONE` (default Europe/Rome). Non mettere password in Git o in `.aiflow/`.

I report sono salvati sotto `.aiflow/state/digest/YYYY-MM-DD.html` e `.txt`; `.json` conserva lo stato di invio. Un errore SMTP **non blocca** la chiusura della giornata; viene mostrato un avviso. Un report già inviato non viene reinviato dalla stessa operazione. Se l'invio è fallito, è possibile riprovare chiamando la funzione digest da un contesto Python oppure con una successiva chiusura effettiva della giornata. Il report viene comunque salvato.

**Nota:** il vecchio `tools/daily_digest.py` è uno strumento separato per il riepilogo multi-progetto e non è il meccanismo di invio automatico di `day end`.

---

# Riepilogo quotidiano multi-progetto

La scansione cerca `.aiflow/state/aiflow.sqlite3` sotto `~/Development`, legge gli eventi del giorno nel fuso Europe/Rome e produce un riepilogo. I progetti fuori da quella cartella richiedono `--projects-root`. Non legge dati da GitHub: i database sono locali.

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
