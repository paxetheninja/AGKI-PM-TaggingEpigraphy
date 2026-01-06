# Entity Linking Strategy

This document defines how entities extracted from inscriptions are linked to external Linked Open Data (LOD) authorities.

## 1. Places (Pleiades)
We use **Pleiades** (https://pleiades.stoa.org) as the authority for ancient places.

### Strategy
1.  **Region Mapping:** The `region_main` field from PHI is mapped to a Pleiades URI at the dataset level (e.g., "Attica" -> `579888`). This allows for geospatial visualization.
2.  **Extracted Places:** Places mentioned *within* the text (e.g., "The sanctuary of Apollo") are extracted by the LLM.
    *   **Prompting:** The LLM is instructed to provide a Pleiades URI if confident.
    *   **Post-Processing:** A fuzzy matching lookup against a local Pleiades dump can be used to validate or fill missing links.

### URI Format
`https://pleiades.stoa.org/places/{ID}`

## 2. Persons (LGPN)
We use the **Lexicon of Greek Personal Names (LGPN)** as the authority for individuals.

### Strategy
Since linking to a specific individual ID is difficult without detailed prosopography, we generate **Search URIs**. This directs the user to the LGPN search results for that name, facilitating further research.

### URI Format
`http://clas-lgpn2.classics.ox.ac.uk/cgi-bin/lgpn_search.cgi?name={NAME}`

## 3. Implementation Status
*   **Schema:** Updated to include `uri` fields for `PersonEntity` and `PlaceEntity`.
*   **Tagger:** The System Prompt now explicitly requests URIs.
*   **Frontend:** The web interface renders these URIs as clickable `🔗` icons in the detail view.