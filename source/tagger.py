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
        "places": [{"name": "<Place Name>", "type": "<Type>", "uri": "<Pleiades URI>"}],
        "deities": ["<Deity Name>", "<Deity Name>"]
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
- **Entities**:
    - **Persons:** Use **LGPN** (Lexicon of Greek Personal Names) identifiers/URIs (e.g., `http://id.lgpn.ox.ac.uk/id/V1-12345`) whenever possible. Do NOT use Wikidata or Wikipedia URIs for persons unless they are major historical figures (e.g., kings, emperors) where LGPN is less relevant. If the specific LGPN ID is unknown, leave the URI null or provide a search query URL.
    - **Places:** Use **Pleiades** URIs.
"""

def tag_inscription(
    inscription: InputInscription, 
    llm_client: LLMProvider, 
    taxonomy: dict,
    model: str
) -> TaggedInscription:
    """
    Orchestrates the tagging process using a single LLM call.
    """
    
    # 1. Classification & Entities
    taxonomy_str = json.dumps(taxonomy, indent=2, ensure_ascii=False)
    tagger_user_prompt = f"Inscription Text:\n{inscription.text}\n\nMetadata: {inscription.metadata}\nTaxonomy:\n{taxonomy_str}"
    
    tagging_data = llm_client.generate_json(
        system_prompt=TAGGER_SYSTEM_PROMPT,
        user_prompt=tagger_user_prompt,
        model=model
    )

    # 2. Merge Results
    merged_data = {
        "phi_id": inscription.id,
        "themes": tagging_data.get("themes", []),
        "entities": tagging_data.get("entities", {"persons": [], "places": []}),
        "provenance": tagging_data.get("provenance", []),
        "completeness": tagging_data.get("completeness", "fragmentary"),
        "rationale": tagging_data.get("rationale", ""),
        "model": model
    }
    
    return TaggedInscription(**merged_data)