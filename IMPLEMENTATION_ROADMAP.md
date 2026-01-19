# Implementation Roadmap - Open Features

## Status Legend
- [ ] Not started
- [~] In progress
- [x] Complete

---

## 1. Prosopography Network Graph
**User Story:** As Gregor, I want to view a node-link diagram connecting people mentioned in the same texts to identify social networks of elites.

**Priority:** High | **Effort:** Medium | **Persona:** Gregor

### Implementation Steps

- [ ] **1.1 Data Preparation**
  - [ ] Extend `build_website.py` to compute co-occurrence matrix
  - [ ] Create new data structure: `{person1, person2, weight, inscriptions[]}`
  - [ ] Store in `data.js` as `APP_DATA.personNetwork`

- [ ] **1.2 Network Computation Logic**
  ```python
  # In build_website.py
  def compute_person_network(merged_list):
      edges = {}
      for m in merged_list:
          persons = m['output'].get('entities', {}).get('persons', [])
          names = [p['name'] for p in persons]
          for i, p1 in enumerate(names):
              for p2 in names[i+1:]:
                  key = tuple(sorted([p1, p2]))
                  if key not in edges:
                      edges[key] = {'source': key[0], 'target': key[1], 'weight': 0, 'inscriptions': []}
                  edges[key]['weight'] += 1
                  edges[key]['inscriptions'].append(m['id'])
      return list(edges.values())
  ```

- [ ] **1.3 Frontend Visualization**
  - [ ] Add new page `network.html` or section in `explore.html`
  - [ ] Install/include D3.js or Vis.js library
  - [ ] Implement force-directed graph layout
  - [ ] Add node sizing by mention frequency
  - [ ] Add edge thickness by co-occurrence count
  - [ ] Implement click-to-filter: clicking node filters inscriptions

- [ ] **1.4 Interactive Features**
  - [ ] Hover shows person details (role, inscription count)
  - [ ] Click node → highlight connected nodes
  - [ ] Double-click → navigate to person's inscriptions
  - [ ] Zoom/pan controls
  - [ ] Filter by minimum edge weight

- [ ] **1.5 Integration**
  - [ ] Add navigation link in header
  - [ ] Connect to existing taxonomy/region filters

### Files to Modify
- `source/build_website.py` - add network computation
- `website/explore.html` or new `website/network.html`
- `website/assets/js/data.js` - add network data

---

## 2. Tag Co-occurrence Matrix
**User Story:** As Florian, I want a visual matrix showing which tags appear together most often to verify if the model is learning logical correlations.

**Priority:** Medium | **Effort:** Medium | **Persona:** Florian

### Implementation Steps

- [ ] **2.1 Data Preparation**
  - [ ] Compute pairwise tag co-occurrence counts
  - [ ] Normalize by total inscriptions (Jaccard similarity optional)
  - [ ] Store as matrix in `data.js`

- [ ] **2.2 Computation Logic**
  ```python
  def compute_tag_cooccurrence(merged_list):
      from collections import defaultdict
      cooccurrence = defaultdict(lambda: defaultdict(int))
      tag_counts = defaultdict(int)

      for m in merged_list:
          themes = m['output'].get('themes', [])
          labels = [t['label'] for t in themes]
          for label in labels:
              tag_counts[label] += 1
          for i, t1 in enumerate(labels):
              for t2 in labels[i+1:]:
                  cooccurrence[t1][t2] += 1
                  cooccurrence[t2][t1] += 1

      return {'matrix': dict(cooccurrence), 'counts': dict(tag_counts)}
  ```

- [ ] **2.3 Frontend Visualization**
  - [ ] Add heatmap section to `explore.html`
  - [ ] Use Plotly heatmap or custom canvas
  - [ ] Color scale: white (0) → primary color (max)
  - [ ] Row/column labels = taxonomy categories

- [ ] **2.4 Interactive Features**
  - [ ] Hover shows: "Tag A + Tag B: N inscriptions"
  - [ ] Click cell → filter to inscriptions with both tags
  - [ ] Sort by frequency or alphabetically
  - [ ] Filter to show only top N tags

### Files to Modify
- `source/build_website.py`
- `website/explore.html`

---

## 3. Regional Comparison View
**User Story:** As Gregor, I want to view two regions side-by-side (e.g., Athens vs. Delphi) comparing their thematic distribution charts.

**Priority:** Medium | **Effort:** Medium | **Persona:** Gregor

### Implementation Steps

- [ ] **3.1 UI Layout**
  - [ ] Add new page `compare.html` or modal in `explore.html`
  - [ ] Two-column layout with identical chart types
  - [ ] Region selector dropdown for each column

- [ ] **3.2 Comparison Charts**
  - [ ] Taxonomy distribution (pie/bar chart)
  - [ ] Temporal histogram
  - [ ] Entity type breakdown
  - [ ] Completeness distribution

- [ ] **3.3 Implementation**
  ```javascript
  function renderComparison(regionA, regionB) {
      const dataA = APP_DATA.inscriptions.filter(i => i.region === regionA);
      const dataB = APP_DATA.inscriptions.filter(i => i.region === regionB);

      // Render side-by-side charts
      renderTaxonomyChart('chartA', dataA);
      renderTaxonomyChart('chartB', dataB);
      renderTimelineChart('timeA', dataA);
      renderTimelineChart('timeB', dataB);
  }
  ```

- [ ] **3.4 Difference Highlighting**
  - [ ] Show percentage difference between regions
  - [ ] Highlight categories unique to one region
  - [ ] Add "sync" checkbox to link zoom/selection

### Files to Create/Modify
- New: `website/compare.html`
- Modify: `website/assets/css/main.css`

---

## 4. Drill-down Map Interaction
**User Story:** As Stephan-Felix, I want to click on a region on the map and have the text list update immediately.

**Priority:** High | **Effort:** Low | **Persona:** Stephan-Felix

### Implementation Steps

- [ ] **4.1 Current State Analysis**
  - Current: Map popups show inscription list but don't filter globally
  - Needed: Click region → update all visualizations

- [ ] **4.2 Add Region Click Handler**
  ```javascript
  // In explore.html map initialization
  function onMarkerClick(region) {
      // Set region filter
      document.getElementById('regionFilter').value = region;
      // Trigger global filter
      filterData();
      // Scroll to results
      document.getElementById('countDisplay').scrollIntoView({behavior: 'smooth'});
  }
  ```

- [ ] **4.3 Visual Feedback**
  - [ ] Highlight selected region on map
  - [ ] Add "Clear region filter" button
  - [ ] Show region name in active filters area

- [ ] **4.4 Two-way Sync**
  - [ ] Region dropdown selection → highlight on map
  - [ ] Map click → update dropdown

### Files to Modify
- `website/explore.html` - add click handlers and region filter UI

---

## 5. Publication Reference Search
**User Story:** As Herbert, I want to search by standard corpus ID (e.g., IG II²) to cross-reference the digital text with the physical volumes.

**Priority:** High | **Effort:** Medium | **Persona:** Herbert

### Implementation Steps

- [ ] **5.1 Data Extraction**
  - [ ] Parse `metadata` field from input inscriptions
  - [ ] Extract publication references (IG, SEG, etc.)
  - [ ] Store as structured array: `[{corpus: "IG II²", number: "1234"}]`

- [ ] **5.2 Regex Patterns**
  ```python
  import re

  PUBLICATION_PATTERNS = [
      r'(IG\s+[IVX]+[²³]?)\s*(\d+)',           # IG II² 1234
      r'(SEG)\s+(\d+)[,.\s]+(\d+)',             # SEG 45, 123
      r'(CIG)\s+(\d+)',                          # CIG 1234
      r'(SIG[³]?)\s+(\d+)',                      # SIG³ 1234
      r'(OGIS)\s+(\d+)',                         # OGIS 1234
      r'(I\.(?:Eph|Did|Perg|Magn)\.?)\s*(\d+)', # I.Eph 1234
  ]

  def extract_publications(metadata):
      refs = []
      for pattern in PUBLICATION_PATTERNS:
          matches = re.findall(pattern, metadata, re.IGNORECASE)
          for m in matches:
              refs.append({'corpus': m[0], 'number': m[-1]})
      return refs
  ```

- [ ] **5.3 Search Index Extension**
  - [ ] Add `publications` field to search index
  - [ ] Enable search by publication reference

- [ ] **5.4 Frontend UI**
  - [ ] Add dedicated search field: "Search by publication (e.g., IG II² 1234)"
  - [ ] Autocomplete corpus names
  - [ ] Display publication refs on detail pages

### Files to Modify
- `source/data_loader.py` or `source/build_website.py`
- `website/search.html`
- `website/inscriptions/*.html` (template in build_website.py)

---

## 6. Onboarding Tour / Tutorial
**User Story:** As Stephan-Felix, I want a guided tutorial explaining what the hierarchical tags mean so I don't feel lost when I first open the tool.

**Priority:** Medium | **Effort:** Medium | **Persona:** Stephan-Felix

### Implementation Steps

- [ ] **6.1 Choose Library**
  - Option A: [Intro.js](https://introjs.com/) - lightweight, step-based
  - Option B: [Shepherd.js](https://shepherdjs.dev/) - more customizable
  - Option C: Custom implementation with CSS/JS

- [ ] **6.2 Define Tour Steps**
  ```javascript
  const tourSteps = [
      {
          element: '.taxonomy-tree',
          title: 'Taxonomy Browser',
          content: 'Browse inscriptions by theme. The hierarchy goes: Domain > Subdomain > Category.',
          position: 'right'
      },
      {
          element: '#map',
          title: 'Geographic Map',
          content: 'Brown markers show where inscriptions were found. Turquoise shows places mentioned in the text.',
          position: 'left'
      },
      {
          element: '#sunburstChart',
          title: 'Taxonomy Sunburst',
          content: 'Click to drill down into specific categories. Size shows inscription count.',
          position: 'top'
      },
      // ... more steps
  ];
  ```

- [ ] **6.3 Tour Trigger**
  - [ ] Show automatically on first visit (localStorage flag)
  - [ ] Add "Start Tour" button in header/footer
  - [ ] Tour for each page (search, explore, detail)

- [ ] **6.4 Styling**
  - [ ] Match dark/light mode
  - [ ] Add progress indicator
  - [ ] Skip/Exit buttons

### Files to Modify
- `website/index.html`, `website/search.html`, `website/explore.html`
- New: `website/assets/js/tour.js`
- New: `website/assets/css/tour.css`

---

## 7. Query Explanation Banner
**User Story:** As Stephan-Felix, I want my complex filter selection to be translated into a natural language sentence.

**Priority:** Low | **Effort:** Low | **Persona:** Stephan-Felix

### Implementation Steps

- [ ] **7.1 Query Parser**
  ```javascript
  function explainQuery() {
      const parts = [];

      // Region
      const region = document.getElementById('regionFilter').value;
      if (region) parts.push(`from ${region}`);

      // Date range
      const dateMin = document.getElementById('dateMin').value;
      const dateMax = document.getElementById('dateMax').value;
      if (dateMin || dateMax) {
          parts.push(`dated ${dateMin || '?'} to ${dateMax || '?'}`);
      }

      // Taxonomy
      const includes = Array.from(activeFilters.entries())
          .filter(([k, v]) => v === 'include')
          .map(([k]) => k.split('/').pop());
      const excludes = Array.from(activeFilters.entries())
          .filter(([k, v]) => v === 'exclude')
          .map(([k]) => k.split('/').pop());

      if (includes.length) parts.push(`tagged as ${includes.join(taxMode === 'all' ? ' AND ' : ' OR ')}`);
      if (excludes.length) parts.push(`excluding ${excludes.join(', ')}`);

      return parts.length ? `Showing inscriptions ${parts.join(', ')}.` : 'Showing all inscriptions.';
  }
  ```

- [ ] **7.2 Display Banner**
  - [ ] Add banner above results: "Showing 42 inscriptions from Attica tagged as Religious OR Dedicatory."
  - [ ] Update on filter change
  - [ ] Collapsible if too long

### Files to Modify
- `website/search.html`
- `website/explore.html`

---

## 8. REST API
**User Story:** As Florian, I want an API endpoint to fetch data by ID so I can test external integrations.

**Priority:** High | **Effort:** High | **Persona:** Florian

### Implementation Steps

- [ ] **8.1 Choose Framework**
  - Option A: FastAPI (Python) - async, auto-docs
  - Option B: Flask (Python) - simple, lightweight
  - Option C: Static JSON API (no server) - limited but zero-maintenance

- [ ] **8.2 API Design**
  ```
  GET /api/v1/inscriptions
      ?region=Attica
      ?theme=Religious
      ?date_min=-400
      ?date_max=-300
      ?limit=100
      ?offset=0

  GET /api/v1/inscriptions/{phi_id}

  GET /api/v1/entities/persons
      ?role=Priestess
      ?limit=100

  GET /api/v1/entities/places
      ?type=City

  GET /api/v1/entities/deities

  GET /api/v1/taxonomy

  GET /api/v1/stats
      # Returns corpus statistics
  ```

- [ ] **8.3 FastAPI Implementation**
  ```python
  # source/api.py
  from fastapi import FastAPI, Query
  from fastapi.middleware.cors import CORSMiddleware
  import json

  app = FastAPI(title="AGKI Epigraphy API", version="1.0")

  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_methods=["GET"],
  )

  # Load data at startup
  @app.on_event("startup")
  async def load_data():
      global inscriptions, taxonomy
      # Load from data.js or output files

  @app.get("/api/v1/inscriptions")
  async def list_inscriptions(
      region: str = None,
      theme: str = None,
      date_min: int = None,
      date_max: int = None,
      limit: int = Query(100, le=1000),
      offset: int = 0
  ):
      results = inscriptions
      if region:
          results = [i for i in results if i['region'] == region]
      # ... more filters
      return {"total": len(results), "data": results[offset:offset+limit]}

  @app.get("/api/v1/inscriptions/{phi_id}")
  async def get_inscription(phi_id: int):
      # Return full inscription data
      pass
  ```

- [ ] **8.4 Static JSON API Alternative**
  - [ ] Generate `api/inscriptions.json` with all data
  - [ ] Generate `api/inscriptions/{id}.json` for each
  - [ ] Generate `api/taxonomy.json`
  - [ ] Client-side filtering only

- [ ] **8.5 Documentation**
  - [ ] FastAPI auto-generates OpenAPI/Swagger docs
  - [ ] Add `/api/docs` endpoint
  - [ ] Write usage examples in README

- [ ] **8.6 Deployment**
  - [ ] Add `requirements.txt`: `fastapi`, `uvicorn`
  - [ ] Add `Dockerfile` for containerized deployment
  - [ ] Add GitHub Actions workflow for CI/CD

### Files to Create
- `source/api.py`
- `requirements-api.txt`
- `Dockerfile` (optional)
- `docs/API.md`

---

## 9. Entity Role Search
**User Story:** As Gregor, I want to search for inscriptions where a "Woman" plays the role of "Priestess".

**Priority:** Medium | **Effort:** Low | **Persona:** Gregor

### Implementation Steps

- [ ] **9.1 Data Already Available**
  - Schema has `role` field for persons
  - Search index includes `mentioned_persons` with roles

- [ ] **9.2 Add UI Filter**
  ```html
  <!-- In search.html sidebar -->
  <div class="filter-group">
      <h4 class="eyebrow">Entity Role</h4>
      <select id="roleFilter" class="select-box">
          <option value="">Any role</option>
          <option value="Priestess">Priestess</option>
          <option value="Archon">Archon</option>
          <option value="King">King</option>
          <!-- Dynamically populate from data -->
      </select>
  </div>
  ```

- [ ] **9.3 Filter Logic**
  ```javascript
  // Add to filterData()
  const roleFilter = document.getElementById('roleFilter').value;
  if (roleFilter) {
      filtered = filtered.filter(item =>
          item.mentioned_persons.some(p =>
              p.role && p.role.toLowerCase().includes(roleFilter.toLowerCase())
          )
      );
  }
  ```

- [ ] **9.4 Role Extraction**
  - [ ] Build unique role list from all inscriptions
  - [ ] Populate dropdown dynamically

### Files to Modify
- `website/search.html`
- `source/build_website.py` (extract unique roles)

---

## 10. Ambiguity Display Enhancement
**User Story:** As Herbert, I want the system to display "Ambiguous" if the AI provided conflicting categories.

**Priority:** Low | **Effort:** Low | **Persona:** Herbert

### Implementation Steps

- [ ] **10.1 Current State**
  - Schema has `is_ambiguous` and `ambiguity_note` fields
  - Detail pages show ⚠️ badge (partially implemented)

- [ ] **10.2 Enhance Display**
  - [ ] Add tooltip with full ambiguity explanation
  - [ ] Add filter in search: "Show only ambiguous tags"
  - [ ] Add column in search results indicating ambiguity

- [ ] **10.3 Ambiguity Statistics**
  - [ ] Show % of ambiguous tags in corpus
  - [ ] List most common ambiguity patterns

### Files to Modify
- `website/search.html`
- `source/build_website.py` (detail page template)

---

## 11. Model Version Display Enhancement
**User Story:** As Florian, I want to see which version of the LLM/Prompt generated the tags.

**Priority:** Low | **Effort:** Low | **Persona:** Florian

### Implementation Steps

- [ ] **11.1 Current State**
  - `model` field exists in output JSON
  - Not prominently displayed in UI

- [ ] **11.2 Add to Detail Page**
  ```html
  <!-- In inscription hero section -->
  <div class="meta-item">
      <div class="label">Tagged by</div>
      <div class="meta-value">
          <span class="badge info">{model_name}</span>
      </div>
  </div>
  ```

- [ ] **11.3 Add to Search Results**
  - [ ] Optional column showing model version
  - [ ] Filter by model version (for comparing outputs)

### Files to Modify
- `source/build_website.py` (detail page template)

---

## Implementation Priority Matrix

| Feature | Priority | Effort | Impact | Recommended Order |
|---------|----------|--------|--------|-------------------|
| Drill-down Map | High | Low | High | 1 |
| Entity Role Search | Medium | Low | Medium | 2 |
| Query Explanation | Low | Low | Medium | 3 |
| Model Version Display | Low | Low | Low | 4 |
| Ambiguity Display | Low | Low | Low | 5 |
| Publication Reference | High | Medium | High | 6 |
| Prosopography Network | High | Medium | High | 7 |
| Tag Co-occurrence | Medium | Medium | Medium | 8 |
| Regional Comparison | Medium | Medium | Medium | 9 |
| Onboarding Tour | Medium | Medium | Medium | 10 |
| REST API | High | High | High | 11 |

---

## Quick Wins (Can implement in <30 min each)

1. **Drill-down Map** - Add click handler to filter by region
2. **Entity Role Search** - Add dropdown and filter logic
3. **Query Explanation** - Add natural language banner
4. **Model Version Display** - Add badge to detail pages

---

## Dependencies

```
Feature                    Depends On
─────────────────────────────────────────
Prosopography Network  →   D3.js or Vis.js library
Tag Co-occurrence      →   Plotly (already included)
Onboarding Tour        →   Intro.js or Shepherd.js
REST API               →   FastAPI + Uvicorn
Regional Comparison    →   (none)
```

---

## Estimated Total Effort

| Category | Hours |
|----------|-------|
| Quick Wins (4 features) | 2-4h |
| Medium Features (5 features) | 15-25h |
| REST API | 8-12h |
| **Total** | 25-41h |

---

## Next Steps

1. Start with Quick Wins to show immediate progress
2. Implement Drill-down Map (most requested)
3. Add Publication Reference Search (scholar essential)
4. Build Prosopography Network (differentiating feature)
5. Design and implement REST API (enables external use)
