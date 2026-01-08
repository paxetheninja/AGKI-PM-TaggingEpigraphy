# Missing Features & Gap Analysis
Based on User Stories (UserStories.md) vs. Current Implementation.

## 1. Search & Filtering (The "Precision" Layer)
**Goal:** enable complex queries beyond simple tag matching.

- [x] **Boolean Logic (AND / OR)**
  - *Current:* Taxonomy filters act as OR.
- [x] **Negative Filtering (NOT)**
  - *Requirement:* Exclude inscriptions tagged as "Funerary".
- [x] **Confidence Threshold Filter**
  - *Requirement:* "Filter out tags with < 80% confidence".
- [x] **Entity Role & Type Search**
  - *Requirement:* Search for "Woman" as "Priestess".
- [x] **Datable vs. Undated Toggle**
  - *Requirement:* Quickly toggle between "Precisely Dated", "Circa", and "Undated".
- [x] **Text Length Filter**
  - *Status:* Implemented in `index.html`.

## 2. Visualization & Exploration (The "Macro" Layer)
**Goal:** Visual analytics for the corpus.

- [x] **Geospatial Map (Leaflet.js)**
  - *Status:* Implemented in `explore.html`.
- [x] **Temporal Histogram**
  - *Status:* Implemented in `explore.html` (50-year bins).
- [x] **Taxonomy Sunburst**
  - *Status:* Implemented in `explore.html` using Plotly.

## 3. Reading & Text Analysis (The "Micro" Layer)
**Goal:** Deep reading support.

- [x] **Entity Highlighting in Greek Text**
  - *Requirement:* Names/Places underlined/highlighted in the main Greek text.
  - *Status:* Implemented via interactive "Evidence Quote" highlighting in the Greek text viewer.
- [x] **Font Size Control**
  - *Status:* Slider implemented in detail pages.

## 4. Data Management (The "Fair" Layer)
**Goal:** Export and Personalization.

- [x] **CSV Export**
  - *Status:* Only JSON export implemented in `index.html`.
- [x] **"My Collection" (Starred Items)**
  - *Status:* Implemented in `explore.html` using LocalStorage.
- [x] **Search History**
  - *Status:* Implemented in `explore.html`.

## 5. Linked Open Data (The "Context" Layer)
**Goal:** External connectivity.

- [x] **LGPN / TM Linking**
  - *Status:* Tagger prompts for URIs; UI links to them.
- [x] **Deity Index**
  - *Status:* Implemented.