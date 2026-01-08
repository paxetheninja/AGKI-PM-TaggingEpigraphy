# Output Data Specification

The tagging pipeline generates one JSON file per inscription. The structure follows the Pydantic schema defined in `source/schema.py`.

## JSON Schema

```json
{
  "phi_id": 12345,
  "themes": [
    {
      "label": "Ehrendekret",
      "hierarchy": {
        "domain": "Content",
        "subdomain": "Official and Legal Documents",
        "category": "Decrees",
        "subcategory": "Honorific Decrees"
      },
      "rationale": "Der Text erwähnt die Verleihung eines Kranzes (stephanos).",
      "confidence": 0.95,
      "quote": "στεφανῶσαι χρυσῷ στεφάνῳ"
    }
  ],
  "entities": {
    "persons": [
      {
        "name": "Theemos",
        "role": "Archon",
        "uri": "http://clas-lgpn2.classics.ox.ac.uk/cgi-bin/lgpn_search.cgi?name=Theemos"
      }
    ],
    "places": [
      {
        "name": "Athen",
        "type": "Polis",
        "uri": "https://pleiades.stoa.org/places/579885"
      }
    ]
  },
  "completeness": "fragmentary",
  "region_uri": "https://pleiades.stoa.org/places/579888"
}
```

## Field Definitions

### Root Object
| Field | Type | Description |
|---|---|---|
| `phi_id` | Integer | The unique ID from the PHI corpus. |
| `themes` | Array | List of thematic classifications. |
| `entities` | Object | Container for `persons` and `places` lists. |
| `completeness` | String | 'intact', 'fragmentary', or 'mutilated'. |
| `region_uri` | String | Pleiades URI for the main region of the inscription. |
| `model` | String | The name of the LLM used for generation (e.g. `gpt-4o`, `gemini-1.5-pro`). |

### Theme Object
| Field | Type | Description |
|---|---|---|
| `label` | String | The most specific term from the taxonomy. |
| `hierarchy` | Object | The full path: `domain` > `subdomain` > `category` > `subcategory`. |
| `rationale` | String | A brief natural language explanation (German) for the tag. |
| `confidence` | Float | A score between 0.0 and 1.0 indicating the model's certainty. |
| `quote` | String | The **exact Greek text segment** that serves as evidence for this tag. |

### Entity Objects
**Person:**
*   `name`: Name as it appears or standardized.
*   `role`: Function (e.g., "Archon", "Priest").
*   `uri`: Link to LGPN (Lexicon of Greek Personal Names).

**Place:**
*   `name`: Toponym.
*   `type`: Classification (e.g., "Polis", "Sanctuary").
*   `uri`: Link to Pleiades Gazetteer.