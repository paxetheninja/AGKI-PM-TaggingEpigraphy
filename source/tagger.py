import json
import logging
from .data_loader import InputInscription
from .schema import TaggedInscription
from .llm_client import LLMProvider

logger = logging.getLogger(__name__)

# --- Pass 1: The Proposer (Experimental, Broad) ---
PROPOSER_SYSTEM_PROMPT = """You are an enthusiastic and experimental epigraphist.
Your task is to analyze Ancient Greek inscriptions and propose ALL POSSIBLE thematic tags and entities found in the text.

**Goal:** Be broad and inclusive. If a theme *might* apply based on a keyword or context, include it. Do not worry about strict certainty yet.

You will be provided with:
1. The Greek text.
2. Metadata.
3. A taxonomy.

**Output Requirements:**
- Return strict JSON.
- **Do NOT** assign confidence scores.
- **Entities:** Extract names as strings. Do NOT look for URIs.
- **Themes:** Find as many relevant tags as possible from the taxonomy.
- **Evidence:** Always provide the Greek `quote`.
- **Language Rule:** Labels, roles, and types MUST be in **English**. The `rationale` and `quote` fields MUST be in **Greek** (corresponding to the inscription text).

JSON Structure:
{
    "themes": [
        {
            "label": "<Label>",
            "hierarchy": { "domain": "...", "subdomain": "...", "category": "...", "subcategory": "..." },
            "rationale": "<Why this tag fits>",
            "quote": "<Greek text>"
        }
    ],
    "entities": {
        "persons": [{"name": "<Name>", "role": "<Role>"}],
        "places": [{"name": "<Place Name String Only>", "type": "<Type>"}],
        "deities": [{"name": "<Name>"}]
    },
    "provenance": [
        { "name": "<Region/City Name>", "type": "Region" }
    ],
    "completeness": "<'intact' | 'fragmentary' | 'mutilated'>",
    "rationale": "<General analysis>"
}
"""

# --- Pass 2: The Judge (Strict, Verification) ---
JUDGE_SYSTEM_PROMPT = """You are a strict Senior Epigraphic Editor.
Your task is to review the "Proposed Analysis" provided by a junior scholar for an Ancient Greek inscription.

**Your Goal:**
1. **Verify** each proposed theme against the Greek text.
2. **Assign Confidence:** 
   - 1.0 (Certain/Explicit)
   - 0.8 (Highly Likely)
   - 0.5 (Plausible/Debatable)
   - 0.0 (Reject/Hallucination)
3. **Refine:** Correct any misclassifications in the hierarchy or roles.
4. **Completeness:** MUST be one of: "intact", "fragmentary", "mutilated".
5. **Language Check:** Ensure labels and roles are in **English**. Ensure `rationale` and `quote` are in **Greek**.

**Input:**
- Original Text & Metadata.
- Junior Scholar's Proposed JSON.

**Output:**
Return the Final Validated JSON with confidence scores added for ALL proposed items.
**Do NOT** add URIs to entities.

JSON Structure:
{
    "themes": [
        {
            "label": "...",
            "hierarchy": { ... },
            "rationale": "...",
            "quote": "...",
            "confidence": <float 0.0-1.0>,
            "is_ambiguous": <bool>,
            "ambiguity_note": "<Optional note>"
        }
    ],
    "entities": {
        "persons": [{"name": "...", "role": "...", "confidence": <float>}],
        "places": [{"name": "...", "type": "...", "confidence": <float>}],
        "deities": [{"name": "...", "confidence": <float>}]
    },
    "provenance": [ ... ],
    "completeness": "<'intact' | 'fragmentary' | 'mutilated'>",
    "rationale": "..."
}
"""

def tag_inscription(
    inscription: InputInscription, 
    llm_client: LLMProvider, 
    taxonomy: dict,
    model: str
) -> TaggedInscription:
    """
    Two-Pass Tagging Process:
    1. Proposer: Generates candidate tags (Recall-focused).
    2. Judge: Validates and scores tags (Precision-focused).
    """
    
    taxonomy_str = json.dumps(taxonomy, indent=2, ensure_ascii=False)
    
    # --- Pass 1: Proposer ---
    logger.info(f"ID {inscription.id}: Starting Proposer phase (Tagging)...")
    proposer_prompt = f"""
    Inscription Text:
{inscription.text}
    
    Metadata: {inscription.metadata}
    
    Taxonomy:
{taxonomy_str}
    """
    
    try:
        proposed_data = llm_client.generate_json(
            system_prompt=PROPOSER_SYSTEM_PROMPT,
            user_prompt=proposer_prompt,
            model=model
        )
    except Exception as e:
        # Fallback if Proposer fails
        logger.error(f"ID {inscription.id}: Proposer failed: {e}")
        return TaggedInscription(phi_id=inscription.id)

    # --- Pass 2: Judge ---
    logger.info(f"ID {inscription.id}: Starting Judge phase (Reviewing)...")
    proposed_json_str = json.dumps(proposed_data, indent=2, ensure_ascii=False)
    
    judge_prompt = f"""
    Original Text:
{inscription.text}
    
    Proposed Analysis to Review:
{proposed_json_str}
    """
    
    final_data = llm_client.generate_json(
        system_prompt=JUDGE_SYSTEM_PROMPT,
        user_prompt=judge_prompt,
        model=model
    )

    # Merge Metadata (Date is not handled by LLM)
    merged_data = {
        "phi_id": inscription.id,
        "themes": final_data.get("themes", []),
        "entities": final_data.get("entities", {"persons": [], "places": [], "deities": []}),
        "provenance": final_data.get("provenance", []),
        "completeness": final_data.get("completeness", "fragmentary"),
        "rationale": final_data.get("rationale", ""),
        "model": f"{model} (Proposer+Judge)",
        
        # Propagate Date Metadata
        "date_str": inscription.date_str,
        "date_min": inscription.date_min,
        "date_max": inscription.date_max,
        "date_circa": inscription.date_circa
    }
    
    return TaggedInscription(**merged_data)
