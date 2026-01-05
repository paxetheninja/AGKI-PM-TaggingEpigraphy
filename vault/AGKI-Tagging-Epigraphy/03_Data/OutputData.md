```
{
  "output_schema": {
    "phi_id": "integer",
    "themes": [
      {
        "label": "string",
        "hierarchy": {
          "domain": "string",
          "subdomain": "string",
          "category": "string | null",
          "subcategory": "string | null"
        },
        "rationale": "string"
      }
    ],
    "entities": {
      "persons": [
        {
          "name": "string",
          "role": "string | null",
          "lgpn": {
            "id": "string",
            "name": "string | null",
            "uri": "string | null",
            "confidence": "number | null"
          }
        }
      ],
      "places": [
        {
          "name": "string",
          "type": "string | null",
          "pleiades": {
            "id": "string",
            "name": "string | null",
            "uri": "string | null",
            "confidence": "number | null"
          }
        }
      ],
      "deities": [
        {
          "name": "string",
          "epithet": "string | null",
          "role": "string | null"
        }
      ]
    }
  }
}
```
This describes the JSON output schema. `phi_id` is required. It must have at least one theme, with a label and a hierarchy that maps to the taxonomy in `vault/AGKI-Tagging-Epigraphy/03_Data/Taxonomie.md` (see `vault/AGKI-Tagging-Epigraphy/03_Data/TaxonomieSchemaMapping.md`). `category` and `subcategory` can be `null` for shallow paths.
Entities are optional. If present, `persons`, `places`, and `deities` hold extracted items.

Linked data integration notes:
- `persons[].lgpn` stores the best LGPN match for a person; `confidence` is a numeric score from the linker.
- `places[].pleiades` stores the best Pleiades match for a place; `uri` can point to the canonical resource.
- If you later want multiple candidates, add `lgpn_candidates` or `pleiades_candidates` as arrays of the same shape.
