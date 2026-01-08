## Meilensteine
Die Meilensteine definieren kritische Punkte im Projektverlauf, an denen Ergebnisse abgenommen werden müssen, um die nächste Phase freizugeben.
- **M1: Clean Data Corpus (Fällig: 13.12.2025)**
    - _Kriterium:_ Der Datensatz ist vollständig bereinigt, normalisiert und liegt maschinenlesbar vor. Inschriften <1000 Zeichen sind ausgefiltert.
    - _Status:_ In Review.
- **M2: Taxonomie Freeze (Fällig: 27.12.2025)**
    - _Kriterium:_ Das kontrollierte Vokabular und die Hierarchie-Ebenen sind final definiert. Das JSON-Output-Schema ist "locked".    
    - _Status:_ Laufend.
- **M3: Pipeline Ready & Test Run (Fällig: 10.01.2026)**
    - _Kriterium:_ Die LLM-Pipeline läuft stabil, Validierungs-Checks für JSON-Output greifen. Ein erster Batch ist erfolgreich getaggt.
    - _Status:_ Geplant.
- **M4: Prototyp Launch (Fällig: 20.01.2026)**
    - _Kriterium:_ Web-Interface ist live. Nutzer können explorativ durch die Hierarchien zoomen (z. B. von „religiös“ zu „Weihung“) und Filter kombinieren.
    - _Status:_ Geplant.

## Zeitplan
Eine kompakte zeitliche Übersicht basierend auf den Kalenderwochen (KW) und den Fristen der Checkliste.
- **Dezember 2025**
    - **KW 48–49:** Abschluss Datenbereinigung & Ingest **[[WorkPackages |(AP 1)]]**
    - **13.12.: Meilenstein M1**. Beginn Taxonomie-Entwicklung **[[WorkPackages |(AP 2)]]**.
    - **KW 51–52:** Finalisierung Taxonomie & JSON-Schema. Prompt-Entwicklung **[[WorkPackages |(AP 2 & 3)]]**
    - **27.12.:** **Meilenstein M2**.
- **Januar 2026**
    - **KW 01:** Implementierung der Pipeline-Logik, Batch-Processing und technische Tests **[[WorkPackages |(AP 3)]]**.
    - **10.01.:** **Meilenstein M3**.
    - **KW 02:** Backend-API Setup & Beginn Frontend-Entwicklung **[[WorkPackages |(AP 5)]]**. Parallel: Manuelle Validierung Stichproben **[[WorkPackages |(AP 4)]]**
    - **KW 03:** Finalisierung Frontend, UI-Polishing & Deployment.
    - **20.01.:** **Meilenstein M4**.