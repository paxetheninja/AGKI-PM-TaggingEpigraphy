# Entity Linking Policy (LGPN, Pleiades)

This file defines how to link extracted entities from the JSON output to external authority resources.

## 1. Scope
- Persons link to LGPN (Lexicon of Greek Personal Names).
- Places link to Pleiades.
- Linking is optional and should not block core tagging.

## 2. Inputs used for linking
- Entity surface form (`name`).
- Local context: `region_main`, `region_sub`, and date range (`date_min`, `date_max`, `date_circa`).
- Optional role/context hints: `persons[].role`, `themes[]`.

## 3. Candidate generation
- Normalize the surface form: strip brackets, normalize spacing, keep diacritics if present.
- Generate candidates from authority search by name and known variants.
- If the corpus already stores region IDs, use them as a coarse geographic filter.

## 4. Scoring and disambiguation
Each candidate receives a score in [0, 1], based on:
- Name match strength (exact > variant > fuzzy).
- Geographic compatibility (region or nearby place).
- Date compatibility (overlapping historical range if provided).
- Role or contextual match (e.g., priestess for cultic contexts).

Disambiguation policy:
- If best score >= 0.80 and margin to next candidate >= 0.10, link automatically.
- If best score is in [0.60, 0.80) or margin < 0.10, mark as ambiguous and keep a single best link with lower confidence.
- If best score < 0.60, do not link.

## 5. Confidence calibration
Calibrate scores on a small gold sample:
- Split a curated set of inscriptions with verified links.
- Fit thresholds to keep precision >= 0.90 for auto-links.
- Track recall separately for reporting.

## 6. Storage in schema
- Store the best match in `persons[].lgpn` or `places[].pleiades`.
- `confidence` is the calibrated score.
- If needed later, add `lgpn_candidates` or `pleiades_candidates` arrays with the same shape.

## 7. Logging and audit
- Record unresolved and ambiguous cases with context for manual review.
- Keep a log of authority queries for reproducibility.
