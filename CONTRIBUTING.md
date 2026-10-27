# Contributing to AIFlow

Grazie per voler contribuire ad AIFlow. **La via più semplice per iniziare è aggiungere un profilo tecnologico in Markdown**, senza modificare il motore Python.

## Profili cercati

Python/Django e FastAPI, TypeScript/Node.js e NestJS, Go, Java/Spring Boot, C#/.NET, Rust, Ruby on Rails, Flutter/Dart, Kotlin/Android, Swift/iOS, Vue/Nuxt, React/Next.js, e altri stack reali. Sono esempi, non un elenco chiuso.

## Come contribuire

1. Apri una Issue con titolo `Profile: <stack>` e descrivi framework, versioni e convenzioni. Controlla che non esista già un profilo o una PR equivalente.
2. Fai fork e crea un branch `profile/<nome>`.
3. Copia `profiles/TEMPLATE/PROFILE.md` in `profiles/<slug>/PROFILE.md` (es. `profiles/python-django/PROFILE.md`). Non modificare il template.
4. Compila **tutte** le sezioni con regole verificabili e specifiche dello stack. Evita preferenze personali presentate come standard obbligatori.
5. Aggiungi fonti ufficiali, esempi di comandi e indicazioni su versioni e condizioni di applicazione.
6. Esegui `python3 tools/validate_profiles.py` e `python3 -m unittest discover -s tests -v`.
7. Apri una PR usando il template, descrivendo cosa hai verificato e cosa resta da testare.

## Criteri di accettazione

- Una directory `profiles/<slug>` con `PROFILE.md` in UTF-8; slug minuscolo, numeri e trattini.
- Sezioni presenti: Ambito e rilevamento; Organizzazione del codice; Dipendenze e toolchain; Testing e qualità; Sicurezza e dati; Deployment e operatività; Interazione con AIFlow; Riferimenti.
- I comandi indicati devono essere pertinenti e riproducibili, senza credenziali o segreti.
- Il profilo deve spiegare come riconoscere il framework da manifest o struttura, non supporre che sia sempre presente.
- Nessuna operazione distruttiva, commit, push o deploy automatico senza consenso.
- SOLID, DRY e altre regole generali non vanno duplicate come obblighi universali dello stack. Le decisioni GLOBAL e PLATFORM approvate hanno un ciclo di vita distinto dai profili pubblici.
- Linguaggio chiaro, esempi tecnici, nessun testo promozionale.

## Differenza tra profilo e decisione di piattaforma

**Profilo:** guida versionata nel repository, revisionata tramite PR, con raccomandazioni contestuali e comandi dello stack. **Decisione PLATFORM:** scelta interna approvata da un operatore, valida per i progetti di quella piattaforma nell'installazione locale. Il merge di un profilo non approva decisioni e non modifica progetti esistenti.

## Sicurezza delle contribuzioni

Non allegare token, password, endpoint privati o dati clienti. Non chiedere agli agenti di aggirare autorizzazioni. Le PR vengono revisionate dai maintainer prima del merge; nessun contributor ha automaticamente accesso di scrittura.

## Manutenzione

Indica le versioni dello stack; apri PR di aggiornamento quando cambiano API, toolchain o pratiche ufficiali. Per modifiche al motore, apri prima una Issue con motivazione, migrazione e test.
