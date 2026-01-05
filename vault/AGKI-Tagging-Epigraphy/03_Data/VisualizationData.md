# Visualization Data Specification

This file defines which data the application needs to drive visualizations and exploration views. The sources are:
- Input records: [[InputData]]
- Output tags: [[OutputData]]
- Taxonomy structure: [[Taxonomie]]
- Mapping rules:[[TaxonomieSchemaMapping]]

## 1. Base record data (detail view)
Each inscription in the UI needs:
- `phi_id`
- `text` or `text_joined_sentences`
- `region_main`, `region_sub`
- `date_str`, `date_min`, `date_max`, `date_circa`
- `themes[]` (labels + hierarchy + rationale)
- `entities.persons[]`, `entities.places[]`, `entities.deities[]`

## 2. Taxonomy tree counts (sunburst, treemap)
Aggregate counts at every taxonomy node across all inscriptions.

Output shape:
```json
{
  "facet": "Content",
  "tree": {
    "label": "Content",
    "count": 12345,
    "children": [
      {
        "label": "Religious and Dedicatory Texts",
        "count": 2345,
        "children": [
          {
            "label": "Curses and Magic",
            "count": 210,
            "children": [
              { "label": "Curse Tablets (Defixiones)", "count": 80 }
            ]
          }
        ]
      }
    ]
  }
}
```

## 3. Time series (histogram, timeline)
Counts over time buckets. Use `date_min`/`date_max` when present; otherwise parse `date_str` if possible.

Output shape:
```json
{
  "bucket": "century",
  "series": [
    { "label": "5th c. BC", "count": 412 },
    { "label": "4th c. BC", "count": 689 }
  ]
}
```

## 4. Geospatial density (map)
Counts by region and, if available, by linked place coordinates.
- Primary: `region_main`, `region_sub`.
- Optional: Pleiades coordinates from `entities.places[].pleiades`.

Output shape:
```json
{
  "regions": [
    { "region_main": "Attica (IG I-III)", "count": 2310 },
    { "region_main": "Aegean Islands, incl. Crete (IG XI-[XIII])", "count": 1440 }
  ],
  "places": [
    { "pleiades_id": "579885", "name": "Delos", "lat": 37.396, "lon": 25.268, "count": 88 }
  ]
}
```

## 5. Co-occurrence matrix (tags together)
Counts for pairs of taxonomy paths within the same inscription.

Output shape:
```json
{
  "pairs": [
    { "a": "Content > Administrative Records and Lists", "b": "Type > Material (Substance) > Stone", "count": 120 }
  ]
}
```

## 6. Entity network (prosopography)
Edges between people (and optionally places) co-mentioned in the same inscription.

Output shape:
```json
{
  "nodes": [
    { "id": "person:Gergos", "label": "Gergos", "type": "person" }
  ],
  "edges": [
    { "source": "person:Gergos", "target": "place:Delos", "weight": 3, "phi_ids": [62838, 12345] }
  ]
}
```

## 7. Filters and facets (search UI)
Provide fast filter lists and counts.
- Region list with counts.
- Time buckets with counts.
- Taxonomy nodes with counts.
- Entity types with counts (persons, places, deities).
- Text length buckets (from `text` length).

## 8. Notes on computation
- Aggregations can be precomputed during the tagging pipeline or computed on demand.
- All path labels must match taxonomy labels exactly.
- If confidence scores are added later, add parallel distributions (e.g., count by confidence bucket).
