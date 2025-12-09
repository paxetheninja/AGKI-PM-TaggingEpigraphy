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
          "category": "string",
          "subcategory": "string"
        },
        "rationale": "string"
      }
    ],
    "entities": {
      "persons": [
        {
          "name": "string",
          "role": "string"
        }
      ],
      "places": [
        {
          "name": "string",
          "type": "string"
        }
      ]
    }
  }
}
```
This describes the JSON schema of the output. Firstly it always has a phi_id. It also must have atleast one theme, with a label, shortly describing whats the theme in words, with a hierachy, domain, subdomain, category and subcategory which must be part of the described [[Taxonomie]]. 
In entities identified persons or places might get recorded if any were found.
