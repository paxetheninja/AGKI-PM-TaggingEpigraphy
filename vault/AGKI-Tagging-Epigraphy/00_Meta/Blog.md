### 1. Problemstellung & Ausgangslage
Das Projekt identifiziert eine klassische **Lücke in den Digital Humanities**:
- **Vorhanden:** Große Mengen an digitalisiertem Text (PHI-Korpus) mit _technischen_ Metadaten (Fundort, Datum).
- **Fehlend:** Eine inhaltliche Strukturierung.
- **Konsequenz:** Forschende müssen "Wortsuche" (String Matching) betreiben oder Texte manuell lesen. Komplexere Abfragen (z.B. "Alle juristischen Texte aus Kleinasien im 2. Jh. v. Chr.") sind maschinell derzeit nicht möglich.
- **Ziel:** Schaffung eines "vermittelnden Layers" (Middleware) zwischen dem rohen griechischen Text und der historischen Forschungsfrage.
### 2. Methodik: Der hybride Ansatz
Das methodische Herzstück des Projekts ist die Kombination aus **menschlicher Expertise** und **künstlicher Intelligenz**.
- **Taxonomie-Entwicklung (Hybrid):**
    - _Top-down:_ Nutzung etablierter epigraphischer Standards (Fachwissen).
    - _Bottom-up:_ Nutzung von LLMs zur Erkennung von Mustern in den Daten, die dem menschlichen Auge bei der Masse entgehen könnten.
    - _Vorteil:_ Dies verhindert, dass die Taxonomie "im Elfenbeinturm" entsteht und garantiert, dass sie tatsächlich auf das Korpus anwendbar ist.
        
- **Der LLM-Einsatz (Reflexiv):**
    - LLMs werden nicht als "Black Box" für die Endlösung genutzt, sondern als Werkzeug zur Skalierung.
    - Das Projekt sieht das LLM selbst als Forschungsgegenstand: Es wird explizit gefragt, wie gut diese Modelle historische Kontexte verstehen ("Methodische Reflexion").
- **Validierungs-Strategie:**
- Die technische Konsistenz wird durch automatisierte Schema-Prüfungen sichergestellt. Dies erlaubt eine schnelle Skalierung auf tausende Inschriften.
### 3. Der Technische Workflow (Pipeline)
Der beschriebene Prozess ist logisch stringent und orientiert sich an Best Practices der Datenverarbeitung:
1. **Preprocessing:** Normalisierung (Bereinigung von Fehlern, Vereinheitlichung polytonischer Akzente). Dies ist essenziell, da Inschriftendaten oft "schmutzig" sind (Klammern, Ergänzungen, Beschädigungen).
2. **Annotation (LLM):** Multi-Label-Klassifikation. Eine Inschrift kann gleichzeitig "religiös" und "ökonomisch" sein (wie im Beispiel gezeigt). Die Ausgabe erfolgt im hierarchischen JSON-Format.
3. **Post-Processing & Qualitätssicherung:** Schema-Validierung und Abgleich mit menschlicher Annotation.

### 4. Analyse des Beispiels (Inschrift ID 62838)
Das gewählte Beispiel ist hervorragend geeignet, um die Komplexität zu demonstrieren:
- **Der Text:** Eine Abrechnung aus Delos (207 v. Chr.), die Bauarbeiten, Inventare und Pachten mischt.
- **Die Herausforderung:** Ein einfaches Label "Abrechnung" würde dem Inhalt nicht gerecht.
- **Die Lösung:** Das Output-Schema erlaubt multiple Pfade:
    1. _Bau/Instandhaltung_ (wegen der Handwerker und Materialien).
    2. _Schatzverwaltung_ (wegen der Inventarlisten der Gefäße).
    3. _Immobilien/Pacht_ (wegen der Mieteinnahmen).
- **Entitäten-Erkennung (NER):** Die Extraktion von Personen ("Gergos, Architekt") und Orten ("Delos") macht das Netzwerk der Akteure sichtbar (Social Network Analysis wird möglich).

### 5. Wissenschaftliche Relevanz & Impact
- **FAIR Data Principles:** Durch die Anreicherung mit semantischen Tags und die Ausgabe in standardisiertem JSON werden die Daten _Findable, Accessible, Interoperable_ und _Reusable_.
- **Explorative Forschung:** Das Projekt ermöglicht einen Paradigmenwechsel von der _gezielten Suche_ (ich suche etwas, das ich schon kenne) zur _Exploration_ (ich lasse mir Zusammenhänge anzeigen, die ich noch nicht kannte – z.B. Visualisierung von Themenclustern).
- **Skalierbarkeit:** Das Verfahren ist potenziell auf andere Korpora (lateinische Inschriften, Papyri) übertragbar.
