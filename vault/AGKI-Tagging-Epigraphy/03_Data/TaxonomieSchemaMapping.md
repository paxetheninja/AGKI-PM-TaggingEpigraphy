# Taxonomie to Schema Mapping

This file defines how items from `vault/AGKI-Tagging-Epigraphy/03_Data/Taxonomie.md` map into the output schema in `vault/AGKI-Tagging-Epigraphy/03_Data/JSONSchema.md`.

## 1. Facet to domain
- `hierarchy.domain` is the facet name: `Content`, `Type`, or `State`.

## 2. Levels to hierarchy
- `hierarchy.subdomain` = first level under the facet.
- `hierarchy.category` = second level under the facet (use `null` if none).
- `hierarchy.subcategory` = third level under the facet (use `null` if none).

## 3. Type facet (Object vs Material)
Use the two Type headings as the first level:
- `Object Type (Physical Object Form)`
- `Material (Substance)`

Examples:
- Type -> Object Type (Physical Object Form) -> Monumental Stone Objects -> Stele
- Type -> Material (Substance) -> Stone -> Marble

## 4. State facet grouping
Group headers map to subdomain, leaf nodes map to category and subcategory.

Examples:
- State -> Complete / Intact -> Complete (Text fully preserved)
- State -> Reconstruction and Intervention -> Reconstructed -> Multiple Fragments Joined

## 5. Content facet examples
- Content -> Religious and Dedicatory Texts -> Curses and Magic -> Curse Tablets (Defixiones)
- Content -> Administrative Records and Lists -> Inventories

## 6. Normalization rules
- Use the exact label text from `vault/AGKI-Tagging-Epigraphy/03_Data/Taxonomie.md` for subdomain, category, and subcategory.
- `label` in the schema is a short free-text summary and does not need to match taxonomy labels.
