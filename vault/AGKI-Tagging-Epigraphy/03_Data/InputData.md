# Kurzspezifikation (JSON pro Inschrift)

## 1. Grundformat
- **Ein Datensatz = eine Inschrift** als JSON-Objekt.
- Datei/Record enthält **Rohtext** + **Metadaten** + **(optional) Datierung** + **(optional) Segmentierung**.
## 2. Felder (pro Record)
### 2.1 Identifikation
- `id` (int) – eindeutige Inschriften-ID.
### 2.2 Text
- `text` (string) – Rohtext (polytonisches Griechisch), häufig mit Zeilenumbrüchen und epigraphischen Zeichen.
- `sentences` (array[string], optional) – vorsegmentierte Textblöcke.
- `text_joined_sentences` (string, optional) – zusammengeführter Text (typisch: aus `sentences` erzeugt).
### 2.3 Region
- `region_main` (string) – Hauptregion.
- `region_sub` (string) – Subregion.
- `region_main_id` (string, optional) – technische ID zur Hauptregion.
- `region_sub_id` (string, optional) – technische ID zur Subregion.
### 2.4 Metadaten-Kopfzeile
- `metadata` (string) – kompakte Kopfzeile (z. B. Region/Edition, Layout/stoich., Datierungsangabe in Kurzform).
### 2.5 Datierung (kann teilweise fehlen)
- `date_str` (string, optional) – Datierung als Freitext (kann leer sein).
- `date_min` (string|null, optional) – untere Jahresgrenze (häufig als String gespeichert).
- `date_max` (string|null, optional) – obere Jahresgrenze (häufig als String gespeichert).
- `date_circa` (bool|null, optional) – circa-Flag.
## 3. Typische Besonderheiten
- Datierung kann **nur in `metadata`** vorhanden sein, während `date_*`-Felder leer/`null` sind.
- `text` kann epigraphische Zeichen/Ergänzungen/Lücken enthalten; diese sind im Input enthalten.
- Zeilenumbrüche in `text` sind üblich; alternativ kann `text_joined_sentences` bereits „geglättet“ vorliegen.
## 4. Beispiele (schematisch)
### 4.1 Beispiel mit Datierungsfeldern gesetzt (z. B. wie 32.json)

```json
{
  "id": 32,
  "metadata": "…",
  "region_main": "…",
  "region_sub": "…",
  "date_str": "…",
  "date_min": "-449",
  "date_max": "-447",
  "date_circa": false,
  "sentences": ["…", "…"],
  "text_joined_sentences": "…",
  "text": "…"
} ```

### 4.2 Beispiel mit Datierung nur in metadata (z. B. wie 21.json)

```json
{
  "id": 21,
  "metadata": "… 450/49 …",
  "region_main": "…",
  "region_sub": "…",
  "date_str": "",
  "date_min": null,
  "date_max": null,
  "date_circa": null,
  "sentences": ["…"],
  "text_joined_sentences": "…",
  "text": "…"
} ```