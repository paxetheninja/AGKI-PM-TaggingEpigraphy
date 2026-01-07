import json
from .data_loader import InputInscription
from .schema import TaggedInscription
from .llm_client import LLMProvider

# --- Task 1: Tagging & Metadata ---
TAGGER_SYSTEM_PROMPT = """You are an expert epigraphist specializing in Ancient Greek inscriptions. 
Your task is to analyze Greek inscriptions and classify them according to a strict hierarchical taxonomy.
You must also identify key entities (persons and places), provenance, and provide a confidence score and textual evidence.

You will be provided with:
1. The Greek text of an inscription.
2. Metadata about the inscription (date, region).
3. A taxonomy structure (JSON).

Your output MUST be valid JSON strictly adhering to this schema. 
Do NOT include any markdown formatting (like ```json), commentary, or extra text outside the JSON object.
{
    "themes": [
        {
            "label": "<Specific category label>",
            "hierarchy": {
                "domain": "<Top level>",
                "subdomain": "<Second level (optional)>",
                "category": "<Third level (optional)>",
                "subcategory": "<Fourth level (optional)>"
            },
            "rationale": "<Specific reasoning for this tag in English>",
            "confidence": <float 0.0-1.0>,
            "quote": "<The exact Greek substring from the text that justifies this tag>"
        }
    ],
    "entities": {
        "persons": [{"name": "<Name>", "role": "<Role>", "uri": "<LGPN URI or similar>"}],
        "places": [{"name": "<Place Name>", "type": "<Type>", "uri": "<Pleiades URI>"}]
    },
    "provenance": [
        { "name": "<Region>", "type": "Region", "uri": "<Pleiades URI>" },
        { "name": "<City>", "type": "Polis", "uri": "<Pleiades URI>" }
    ],
    "completeness": "<'intact' | 'fragmentary' | 'mutilated'>",
    "rationale": "<Comprehensive summary of the analysis and historical context in English>"
}

**Rules:**
- **Evidence:** The 'quote' MUST be an exact string found in the input text.
- **Confidence:** 1.0 for certain matches, 0.5-0.9 for likely interpretations.
- **Taxonomy:** Hierarchy fields MUST match the provided taxonomy exactly. Labels MUST remain in English.
- **Provenance:** Start broad (Region) and go narrow (City/Spot). Use **Pleiades** URIs (https://pleiades.stoa.org) for all places.
- **Entities:**
    - **Persons:** Use **LGPN** (Lexicon of Greek Personal Names) identifiers/URIs (e.g., `http://id.lgpn.ox.ac.uk/id/V1-12345`) whenever possible. Do NOT use Wikidata or Wikipedia URIs for persons unless they are major historical figures (e.g., kings, emperors) where LGPN is less relevant. If the specific LGPN ID is unknown, leave the URI null or provide a search query URL.
    - **Places:** Use **Pleiades** URIs.
"""

# --- Task 2: Translation & Alignment (Language Specific) ---
def get_translator_prompt(language_name: str, language_code: str) -> str:
    return f"""You are an expert philologist and translator of Ancient Greek.
Your task is to provide a fluent translation of an inscription into {language_name}, and create a semantic alignment.

Your output MUST be valid JSON strictly adhering to this schema. 
Do NOT include any markdown formatting (like ```json), commentary, or extra text outside the JSON object.
{{
    "language": "{language_code}",
    "text": "<Fluent {language_name} translation>",
    "alignment": [{{ "greek": "<Greek segment>", "translation": "<{language_name} translation of segment>" }}]
}}

**Rules:**
- **Alignment:** Break the text into logical semantic units (sentences or complete phrases).
- **Exactness:** The `greek` field must be the EXACT substring from the original text (including original newlines/spaces).
- **Completeness:** If you concatenate all `greek` fields, it MUST reconstruct the exact original input text segment provided.
- **Language:** Perform the translation strictly in {language_name}.
"""

def tag_inscription(
    inscription: InputInscription, 
    llm_client: LLMProvider, 
    taxonomy: dict,
    model: str
) -> TaggedInscription:
    """
    Orchestrates the process using three types of LLM calls:
    1. Metadata/Tagging
    2. English Translation (Chunked)
    3. German Translation (Chunked)
    """
    
    # 1. Classification & Entities
    taxonomy_str = json.dumps(taxonomy, indent=2, ensure_ascii=False)
    tagger_user_prompt = f"Inscription Text:\n{inscription.text}\n\nMetadata: {inscription.metadata}\nTaxonomy:\n{taxonomy_str}"
    
    tagging_data = llm_client.generate_json(
        system_prompt=TAGGER_SYSTEM_PROMPT,
        user_prompt=tagger_user_prompt,
        model=model
    )

    # 2. Translation & Alignment (Chunked per language)
    def chunk_text(text: str, max_chars: int = 700) -> list[str]:
        """
        Splits text into chunks of approximately max_chars, 
        breaking at the nearest sentence end ('.') or word end (' ').
        """
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            # If remaining text fits, add it all
            if text_len - start <= max_chars:
                chunks.append(text[start:])
                break
            
            # Target end index
            end = start + max_chars
            
            # Find the best split point within the window [start, end]
            # Prioritize '.' (sentence boundary) over ' ' (word boundary)
            # Search backwards from the target 'end'
            block = text[start:end]
            
            # rfind returns -1 if not found. Indices are relative to 'block', so add 'start'
            last_dot = block.rfind('.')
            last_space = block.rfind(' ')
            
            split_idx = -1
            
            # Try splitting at '.' if it's reasonably far into the chunk (e.g., > 10% of max_chars)
            # to avoid creating tiny chunks if a dot appears right at the start.
            if last_dot != -1 and last_dot > (max_chars * 0.1):
                split_idx = start + last_dot + 1  # Include '.' in the chunk
            elif last_space != -1:
                split_idx = start + last_space + 1 # Include ' ' in the chunk
            else:
                # Fallback: Hard cut if no delimiters found
                split_idx = end
            
            chunks.append(text[start:split_idx])
            start = split_idx
            
        return chunks

    chunks = chunk_text(inscription.text)
    
    final_translations = []
    
    from concurrent.futures import ThreadPoolExecutor, as_completed

    for lang_name, lang_code in [("English", "en"), ("German", "de")]:
        combined_text_parts = [""] * len(chunks)
        combined_alignment_parts = [[] for _ in chunks]
        system_prompt = get_translator_prompt(lang_name, lang_code)
        
        def process_chunk(index, text_segment):
            user_prompt = f"Please translate and align this segment (Part {index+1}/{len(chunks)}) of a Greek inscription:\n\n{text_segment}"
            try:
                data = llm_client.generate_json(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    model=model
                )
                return index, data
            except Exception as e:
                print(f"Error translating {lang_name} chunk {index+1}: {e}")
                return index, None

        # Execute chunks in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_chunk, i, c) for i, c in enumerate(chunks)]
            
            for future in as_completed(futures):
                idx, result = future.result()
                if result:
                    combined_text_parts[idx] = result.get("text", "")
                    combined_alignment_parts[idx] = result.get("alignment", [])

        # Reassemble in order
        final_translations.append({
            "language": lang_code,
            "text": " ".join(combined_text_parts).strip(),
            "alignment": [item for sublist in combined_alignment_parts for item in sublist]
        })

    # 3. Merge Results
    merged_data = {
        "phi_id": inscription.id,
        "themes": tagging_data.get("themes", []),
        "entities": tagging_data.get("entities", {"persons": [], "places": []}),
        "provenance": tagging_data.get("provenance", []),
        "completeness": tagging_data.get("completeness", "fragmentary"),
        "rationale": tagging_data.get("rationale", ""),
        "translations": final_translations,
        "model": model
    }
    
    return TaggedInscription(**merged_data)