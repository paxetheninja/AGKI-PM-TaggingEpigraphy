import json
from .data_loader import InputInscription
from .schema import TaggedInscription
from .llm_client import LLMProvider

SYSTEM_PROMPT = """You are an expert epigraphist and historian specializing in Ancient Greek inscriptions. 
Your task is to analyze Greek inscriptions and classify them according to a strict hierarchical taxonomy.
You must also identify key entities (persons and places) and provide a confidence score and textual evidence for your decisions.

You will be provided with:
1. The Greek text of an inscription.
2. Metadata about the inscription (date, region).
3. A taxonomy structure (JSON).

Your output MUST be valid JSON strictly adhering to the following schema:
{
    "phi_id": <integer (same as input)>,
    "themes": [
        {
            "label": "<Specific category label>",
            "hierarchy": {
                "domain": "<Top level>",
                "subdomain": "<Second level (optional)>",
                "category": "<Third level (optional)>",
                "subcategory": "<Fourth level (optional)>"
            },
            "rationale": "<Brief explanation in German>",
            "confidence": <float 0.0-1.0>,
            "quote": "<The exact Greek substring from the text that justifies this tag>"
        }
    ],
    "entities": {
        "persons": [
            {
                "name": "<Name>", 
                "role": "<Role>",
                "uri": "<URI>"
            }
        ],
        "places": [
            {
                "name": "<Place Name>", 
                "type": "<Type>",
                "uri": "<URI>"
            }
        ]
    },
    "provenance": [
        { "name": "<Region (e.g. Attica)>", "type": "Region", "uri": "<URI>" },
        { "name": "<Subregion/City (e.g. Athens)>", "type": "Polis", "uri": "<URI>" },
        { "name": "<Specific Spot (e.g. Acropolis)>", "type": "Sanctuary", "uri": "<URI>" }
    ],
    "completeness": "<'intact' | 'fragmentary' | 'mutilated'>"
}

**Rules:**
- **Provenance:** Extract the location hierarchy from the metadata/text. Start broad (Region) and go narrow (City/Spot).
- **Evidence:** The 'quote' MUST be an exact string found in the input text.
- **Confidence:** Use 1.0 for certain matches (explicit keywords), 0.5-0.9 for likely interpretations, <0.5 for guesses.
- **Taxonomy:** The 'hierarchy' fields must match the provided taxonomy exactly.
- **Language:** Use German for the 'rationale'.
- **Entities:** Try to provide URIs if you are confident (e.g. Athens -> https://pleiades.stoa.org/places/579885).
"""

def construct_prompt(inscription: InputInscription, taxonomy: dict) -> str:
    """Constructs the user prompt."""
    
    # We serialize the taxonomy to a string. 
    taxonomy_str = json.dumps(taxonomy, indent=2, ensure_ascii=False)
    
    prompt = f"""
Input Inscription (PHI ID: {inscription.id}):
Metadata: {inscription.metadata}
Date: {inscription.date_str}
Region: {inscription.region_main} -> {inscription.region_sub}

Text:
{inscription.text}

---
Taxonomy Reference:
{taxonomy_str}

---
Analyze the inscription above and generate the JSON output. Ensure you provide 'confidence' scores and specific 'quote' evidence for each theme.
"""
    return prompt

def tag_inscription(
    inscription: InputInscription, 
    llm_client: LLMProvider, 
    taxonomy: dict,
    model: str
) -> TaggedInscription:
    """
    Orchestrates the tagging process for a single inscription.
    """
    user_prompt = construct_prompt(inscription, taxonomy)
    
    response_data = llm_client.generate_json(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        model=model
    )
    
    # Ensure phi_id is correct
    response_data['phi_id'] = inscription.id
    
    # Validate with Pydantic and set the model name
    tagged = TaggedInscription(**response_data)
    tagged.model = model
    return tagged