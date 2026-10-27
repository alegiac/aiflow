# Profilo PHP/Laravel

Attivare solo se lo stack è dichiarato o rilevato. Versioni PHP/Laravel e frontend si deducono dai manifest e dalla repository: Laravel 13, Valet, React, Inertia, shadcn e sidebar sono preferenze configurabili, non fatti universali.

## Regole
- SOLID, DRY, KISS, clean code e convenzioni del repository, evitando astrazioni gratuite.
- Controller snelli; logica in Actions, Services, Jobs o pattern esistenti, senza imporre un pattern nuovo.
- Form Request per validazione quando utile; autorizzazione con policy e controlli coerenti.
- Database: verificare impatto migration, dati, rollback e ambienti condivisi; no modifiche distruttive implicite.
- Integrazioni: considerare timeout, retry, idempotenza, deduplica, error handling e logging.
- Test con Pest se presente; test di unità, feature e integrazione derivati dai criteri di accettazione approvati; coverage elevata come obiettivo, non come prova sufficiente di correttezza.
- Frontend: usare stack effettivo; Figma come fonte UX se disponibile, altrimenti progettare i flussi e chiedere approvazione prima dell'implementazione significativa.
- Non introdurre Filament, Docker, React o altre dipendenze solo per preferenza, senza verifica e consenso.
