import json
import logging
from .data_loader import InputInscription
from .schema import TaggedInscription
from .llm_client import LLMProvider
from .taxonomy_utils import format_taxonomy_for_prompt, validate_taxonomy_compliance, enforce_taxonomy_compliance

logger = logging.getLogger(__name__)

# --- Pass 1: The Proposer (Experimental, Broad) ---
PROPOSER_SYSTEM_PROMPT = """You are an enthusiastic and experimental epigraphist.
Your task is to analyze Ancient Greek inscriptions and propose ALL POSSIBLE thematic tags and entities found in the text.

═══════════════════════════════════════════════════════════════════════════════
CRITICAL REQUIREMENT #1 - LANGUAGE (MANDATORY):
═══════════════════════════════════════════════════════════════════════════════
1. ALL entity names (persons, places, deities) MUST be in ENGLISH/LATINIZED form.
2. ALL rationale fields MUST be written in ENGLISH.
3. ALL roles, types, and labels MUST be in ENGLISH.
4. ONLY the "quote" field should contain Greek text.

EXAMPLES of correct transliteration:
- Ἀθῆναι → "Athens" (NOT "Αθήνα" or "Ἀθῆναι")
- Πειραιεύς → "Piraeus" (NOT "Πειραιε ς")
- Ἀντωνῖνος → "Antoninus" (NOT "ντωνε νου")
- Ἀθηνᾶ → "Athena" (NOT "Αθηνά")
- Τύχη → "Tyche" (NOT "τ χ")
- Ἀντίνοος → "Antinous" (NOT "ντιν ου")
- Ἐλευσίς → "Eleusis" (NOT "λευσε νι")
- Μαραθών → "Marathon" (NOT "Μαραθ νιος")
- Ἁδριανός → "Hadrian" (NOT "δριανο")

If you output Greek characters in entity names or rationales, your response is INVALID.

═══════════════════════════════════════════════════════════════════════════════
CRITICAL REQUIREMENT #2 - TAXONOMY (MANDATORY):
═══════════════════════════════════════════════════════════════════════════════
You will receive an EXPLICIT LIST of valid taxonomy paths below.
- Use ONLY paths from this list. Do NOT invent new categories or subcategories.
- If a path has no subcategory listed, you MUST set "subcategory": null
- The "label" field MUST match the deepest level of your chosen path (category or subcategory)
- NEVER hallucinate subcategories like "Tribute Lists", "Secretaries", or "Aparche" - if they are not in the list, they do not exist.
═══════════════════════════════════════════════════════════════════════════════

**Goal:** Be broad and inclusive. If a theme *might* apply based on a keyword or context, include it. Do not worry about strict certainty yet.

You will be provided with:
1. The Greek text.
2. Metadata.
3. A VALID TAXONOMY PATHS list (use ONLY these exact paths).

**Output Requirements:**
- Return strict JSON.
- **Do NOT** assign confidence scores.
- **Entities:** Extract names in standard ENGLISH/Latinized form (see examples above). Do NOT look for URIs.
- **Themes:** Use ONLY paths from the provided taxonomy list. Set subcategory to null if not in the list.
- **Evidence:** Always provide the Greek `quote` (this is the ONLY field that should contain Greek).

JSON Structure:
{
    "themes": [
        {
            "label": "<Must match category or subcategory from taxonomy>",
            "hierarchy": {
                "domain": "<From taxonomy>",
                "subdomain": "<From taxonomy>",
                "category": "<From taxonomy>",
                "subcategory": "<From taxonomy OR null if none exists>"
            },
            "rationale": "<Why this tag fits - MUST BE IN ENGLISH>",
            "quote": "<Greek text from inscription>"
        }
    ],
    "entities": {
        "persons": [{"name": "<ENGLISH/Latinized Name>", "role": "<Role in English>"}],
        "places": [{"name": "<ENGLISH/Latinized Place Name>", "type": "<Type in English>"}],
        "deities": [{"name": "<ENGLISH/Latinized Deity Name>"}]
    },
    "provenance": [
        { "name": "<ENGLISH Region/City Name>", "type": "Region" }
    ],
    "completeness": "<'intact' | 'fragmentary' | 'mutilated'>",
    "rationale": "<General analysis - MUST BE IN ENGLISH>"
}
"""

# --- Pass 2: The Judge (Strict, Verification) ---
JUDGE_SYSTEM_PROMPT = """You are a strict Senior Epigraphic Editor.
Your task is to review the "Proposed Analysis" provided by a junior scholar for an Ancient Greek inscription.

═══════════════════════════════════════════════════════════════════════════════
CRITICAL LANGUAGE REQUIREMENTS - ENFORCE STRICTLY:
═══════════════════════════════════════════════════════════════════════════════
You MUST correct any Greek text found in the following fields:
- Entity names (persons, places, deities) → Convert to ENGLISH/Latinized form
- Rationale fields → Rewrite entirely in ENGLISH
- Roles and types → Must be in ENGLISH

ONLY the "quote" field should contain Greek text.

CORRECTION EXAMPLES (apply these transformations):
- "Ἀθῆναι" or "Αθήνα" or "θ νας" → "Athens"
- "Πειραιε ς" → "Piraeus"
- "ντωνε νου σεβαστο" → "Antoninus Pius"
- "Αθηνά" → "Athena"
- "τ χ" or "Τύχη" → "Tyche"
- "ντιν ου" → "Antinous"
- "λευσε νι" → "Eleusis"
- "Μαραθ νιος" → "Marathon"
- "δριανο" or "Ἁδριανός" → "Hadrian"
- "Σωτ λης Βακχ λου" → "Soteles son of Bacchylos"

If the junior scholar wrote rationales in Greek, you MUST translate them to English.
If entity names contain Greek characters, you MUST transliterate them to English/Latin.
═══════════════════════════════════════════════════════════════════════════════

**Your Goals:**
1. **LANGUAGE ENFORCEMENT (HIGHEST PRIORITY):**
   - Scan ALL entity names for Greek characters and convert to English/Latinized form
   - Scan ALL rationale fields and rewrite in English if they contain Greek
   - This is NON-NEGOTIABLE. Any Greek in names/rationales = INVALID output.

2. **Verify** each proposed theme against the Greek text.

3. **Assign Confidence:**
   - 1.0 (Certain/Explicit)
   - 0.8 (Highly Likely)
   - 0.5 (Plausible/Debatable)
   - 0.0 (Reject/Hallucination)

4. **Refine:** Correct any misclassifications in the hierarchy or roles.

5. **Completeness:** MUST be one of: "intact", "fragmentary", "mutilated".

**Input:**
- Original Text & Metadata.
- Junior Scholar's Proposed JSON (may contain Greek errors that YOU must fix).

**Output:**
Return the Final Validated JSON with:
- ALL Greek entity names converted to English/Latinized form
- ALL rationales written in English
- Confidence scores added for ALL items
- **Do NOT** add URIs to entities.

JSON Structure:
{
    "themes": [
        {
            "label": "<English label>",
            "hierarchy": { ... },
            "rationale": "<MUST BE IN ENGLISH>",
            "quote": "<Greek text - only field with Greek>",
            "confidence": <float 0.0-1.0>,
            "is_ambiguous": <bool>,
            "ambiguity_note": "<Optional note in English>"
        }
    ],
    "entities": {
        "persons": [{"name": "<ENGLISH/Latinized>", "role": "<English>", "confidence": <float>}],
        "places": [{"name": "<ENGLISH/Latinized>", "type": "<English>", "confidence": <float>}],
        "deities": [{"name": "<ENGLISH/Latinized>", "confidence": <float>}]
    },
    "provenance": [{"name": "<ENGLISH>", "type": "<English>"}],
    "completeness": "<'intact' | 'fragmentary' | 'mutilated'>",
    "rationale": "<General analysis - MUST BE IN ENGLISH>"
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
    3. Post-validation: Corrects hallucinated subcategories.
    """

    # Generate flattened taxonomy for clearer LLM instructions
    taxonomy_paths_str = format_taxonomy_for_prompt(taxonomy)

    # --- Pass 1: Proposer ---
    logger.info(f"ID {inscription.id}: Starting Proposer phase (Tagging)...")
    proposer_prompt = f"""
Inscription Text:
{inscription.text}

Metadata: {inscription.metadata}

{taxonomy_paths_str}
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

    # --- Post-Validation: Taxonomy Compliance ---
    logger.info(f"ID {inscription.id}: Enforcing taxonomy compliance...")

    # Strict enforcement (Prune or Remove)
    final_data, corrections = enforce_taxonomy_compliance(final_data, taxonomy)
    
    if corrections:
        logger.warning(f"ID {inscription.id}: Taxonomy corrections applied:")
        for corr in corrections:
            logger.warning(f"  - {corr}")

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
