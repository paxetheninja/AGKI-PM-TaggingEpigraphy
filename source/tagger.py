import json
from .data_loader import InputInscription
from .schema import TaggedInscription
from .llm_client import LLMProvider

SYSTEM_PROMPT = """You are an expert epigraphist and historian specializing in Ancient Greek inscriptions. 
Your task is to analyze Greek inscriptions and classify them according to a strict hierarchical taxonomy.
You must also identify key entities (persons and places) mentioned in the text.

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
            "rationale": "<Brief explanation in German>"
        }
    ],
    "entities": {
        "persons": [{"name": "...", "role": "..."}],
        "places": [{"name": "...", "type": "..."}]
    }
}

**Rules:**
- Use German for the 'rationale'.
- The 'hierarchy' fields must match the provided taxonomy exactly where possible.
- If the text implies multiple distinct themes, include them all.
- 'label' should be the most specific term from the taxonomy.
"""

def construct_prompt(inscription: InputInscription, taxonomy: dict) -> str:
    """Constructs the user prompt."""
    
    # We serialize the taxonomy to a string. 
    # Optimization: If taxonomy is huge, we might only include relevant top-level keys 
    # or rely on the model's general knowledge + strict constraints. 
    # For now, we pass the whole structure as it's not massive.
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
Analyze the inscription above and generate the JSON output.
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
    
    # Validate with Pydantic
    return TaggedInscription(**response_data)
