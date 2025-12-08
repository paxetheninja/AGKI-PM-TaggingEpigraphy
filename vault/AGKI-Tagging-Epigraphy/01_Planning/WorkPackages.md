## Projektstrukurplan (PSP)
Der PSP zerlegt das Gesamtprojekt in fünf logische Arbeitspakete (AP), die den Fluss von der Datenakquise bis zur Benutzeroberfläche abbilden.
- **AP 1: Datenbasis & Pre-Processing**
    - Akquise und Filterung der PHI-Daten.
    - Linguistische Normalisierung und Segmentierung.
- **AP 2: Taxonomie-Entwicklung & Schema-Design**
    - Entwicklung des begrifflichen Modells (Top-down & Bottom-up).
    - Technische Definition des Output-Formats.
- **AP 3: LLM-Pipeline & Annotation**
    - Prompt Engineering und Kontext-Optimierung.
    - Technische Implementierung des Massen-Taggings.
- **AP 4: Validierung & Iteration**
    - Manuelle Experten Überprüfung.
    - Abgleich und Nachschärfung der Pipeline.
- **AP 5: Infrastruktur & Exploration (Frontend)**
    - Backendentwicklung, Datenbank und Abfragesystem.
    - Entwicklung des Web-Prototypen zur Visualisierung.
## Bewertung der Pakete

| **Arbeitspaket (AP)** | **Task**          | **Beschreibung**                                                                                    | **Aufwand** |
| --------------------- | ----------------- | --------------------------------------------------------------------------------------------------- | ----------- |
| **AP 1: Daten**       | _Data Ingest_     | Import der PHI-JSON-Dateien; Filtern auf Datensätze > 1000 Zeichen & Zielregionen/Zeiten.           | Low         |
|                       | _Bereinigung_     | Normalisierung polytonisches Griechisch; Behandlung von Zeilenumbrüchen/Klammern; Tokenisierung.    | Medium      |
| **AP 2: Taxonomie**   | _Domain Modeling_ | Erstellung der Top-down Kategorien (z. B. „ökonomisch“) nach altertumswissenschaftlichen Standards. | High        |
|                       | _LLM-Discovery_   | Bottom-up Analyse eines Subkorpus durch LLM zur Identifikation von Subkategorien.                   | Medium      |
|                       | _Schema Def._     | Finalisierung des JSON-Schemas für Hierarchien (Domain > Subdomain...) und Entitäten.               | Medium      |
| **AP 3: Pipeline**    | _Prompting_       | Entwicklung systematischer Prompts mit Few-Shot Beispielen (analog Bsp. ID 62838).                  | High        |
|                       | _Implementation_  | Skripting der API-Calls (Batching), Error-Handling (JSON-Validierung) und Logging.                  | High        |
|                       | _Batch Run_       | Durchführung der automatischen Verschlagwortung für das gesamte Korpus.                             | Low         |
| **AP 4: Validierung** | _Manual Tagging_  | Erstellung eines „Gold Standards“: Annotation eines stratifizierten Samples durch Fachexperten.     | High        |
|                       | _Evaluation_      | Berechnung von Metriken (Precision/Recall) und Analyse von Konfusionsmustern.                       | Medium      |
|                       | _Refinement_      | Anpassung der Prompts oder Post-Processing Regeln basierend auf Fehleranalyse.                      | Medium      |
| **AP 5: Frontend**    | _Backend API_     | Bereitstellung der angereicherten JSON-Daten (suchbar nach Hierarchie-Pfaden).                      | Medium      |
|                       | _UI Dev_          | Bau des Interfaces: Facettierte Suche, Detailansicht (Text + Tags), Visualisierung.                 | Medium      |
