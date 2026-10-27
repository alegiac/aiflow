# Profilo PHP/Laravel

## Ambito e rilevamento
- Attivare quando lo stack PHP/Laravel è dichiarato o rilevato da `composer.json`, `artisan` e struttura del progetto.
- Verificare le versioni effettive PHP, Laravel, database e frontend dai manifest. Laravel 13, Valet, React, Inertia, shadcn e sidebar sono scelte possibili, non requisiti universali.
- Non applicare regole Laravel a un progetto PHP privo del framework.

## Organizzazione del codice
- Applicare SOLID, DRY e KISS nel rispetto delle convenzioni del repository, evitando astrazioni gratuite.
- Controller snelli; collocare la logica in Actions, Services, Jobs o pattern già esistenti, senza imporne uno nuovo.
- Form Request per validazione quando utile; Policy, Gate e middleware per autorizzazione coerente.
- Usare lo stack frontend effettivo e non introdurre React, Inertia, Livewire o altri framework senza approvazione.

## Dipendenze e toolchain
- Verificare `composer.json`, `composer.lock`, versione PHP e strumenti già adottati prima di aggiornare dipendenze.
- Seguire la toolchain esistente (`artisan`, Composer, eventuali Vite e package manager).
- Non introdurre Filament, Docker o altre dipendenze per sola preferenza.

## Testing e qualità
- Usare Pest se già presente, altrimenti il runner del repository; test unitari, feature e integrazione basati sui criteri di accettazione approvati.
- Testare validazione, autorizzazione, code, retry, error handling, database e integrazioni esterne.
- Coverage elevata è un obiettivo, non prova sufficiente di correttezza; riportare risultati realmente eseguiti.

## Sicurezza e dati
- Applicare validazione degli input, autorizzazione server-side, protezione delle credenziali e logging senza segreti.
- Per migration valutare impatto, compatibilità, dati esistenti, rollback e ambienti condivisi.
- Per integrazioni esterne prevedere timeout, retry limitati, idempotenza e deduplica.

## Deployment e operatività
- Verificare configurazioni per ambiente, queue worker, scheduler, cache e osservabilità quando pertinenti.
- Non eseguire migration distruttive, deploy, push o azioni su sistemi remoti senza autorizzazione esplicita.
- Prevedere rollback e gestione degli errori prima di interventi in produzione.

## Interazione con AIFlow
- Durante analitica verificare stack reale, vincoli, versioni e decisioni approvate; non inventare scelte architetturali.
- In `task.md` e `report.md` registrare impatto delle migration, test eseguiti, risultati e rischi.
- Comporre il profilo con React, shadcn, Tailwind, Shopify REST/GraphQL e MySQL/PostgreSQL solo quando selezionati; le regole complementari si applicano insieme.
- Quando due profili impongono scelte incompatibili, chiedere una decisione umana.

## Riferimenti
- https://laravel.com/docs
- https://www.php.net/manual/en/
