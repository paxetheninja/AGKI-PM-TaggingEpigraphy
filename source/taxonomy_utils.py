"""
Taxonomy utilities for flattening and validating taxonomy hierarchies.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

logger = logging.getLogger(__name__)


def flatten_taxonomy(taxonomy: dict) -> Tuple[List[str], Set[str]]:
    """
    Flattens a nested taxonomy into explicit paths and a set of valid labels.

    Args:
        taxonomy: Nested taxonomy dict from taxonomy.json

    Returns:
        Tuple of:
        - List of formatted path strings for the prompt
        - Set of all valid (domain, subdomain, category, subcategory) tuples
    """
    paths = []
    valid_tuples: Set[Tuple[str, Optional[str], Optional[str], Optional[str]]] = set()

    for domain, subdomains in taxonomy.items():
        if not isinstance(subdomains, dict) or not subdomains:
            # Domain with no subdomains
            paths.append(f"• {domain} > [NO SUBDOMAIN]")
            valid_tuples.add((domain, None, None, None))
            continue

        for subdomain, categories in subdomains.items():
            if not isinstance(categories, dict) or not categories:
                # Subdomain with no categories
                paths.append(f"• {domain} > {subdomain} > [NO CATEGORY]")
                valid_tuples.add((domain, subdomain, None, None))
                continue

            for category, subcategories in categories.items():
                if not isinstance(subcategories, dict) or not subcategories:
                    # Category with no subcategories - this is valid, subcategory must be null
                    paths.append(f"• {domain} > {subdomain} > {category}")
                    valid_tuples.add((domain, subdomain, category, None))
                else:
                    # Category has subcategories
                    for subcategory, sub_sub in subcategories.items():
                        if not isinstance(sub_sub, dict) or not sub_sub:
                            paths.append(f"• {domain} > {subdomain} > {category} > {subcategory}")
                            valid_tuples.add((domain, subdomain, category, subcategory))
                        else:
                            # Handle 5th level (rare, but exists in taxonomy)
                            for sub_sub_cat in sub_sub.keys():
                                paths.append(f"• {domain} > {subdomain} > {category} > {subcategory} > {sub_sub_cat}")
                                # Still store as 4-tuple, using deepest meaningful level
                                valid_tuples.add((domain, subdomain, category, subcategory))

    return paths, valid_tuples


def format_taxonomy_for_prompt(taxonomy: dict) -> str:
    """
    Formats the taxonomy as an explicit list of valid paths for the LLM prompt.

    Args:
        taxonomy: Nested taxonomy dict

    Returns:
        Formatted string listing all valid taxonomy paths
    """
    paths, _ = flatten_taxonomy(taxonomy)

    header = """VALID TAXONOMY PATHS - USE ONLY THESE EXACT COMBINATIONS:
═══════════════════════════════════════════════════════════════════════════════
You MUST use ONLY the paths listed below. Do NOT invent new categories or subcategories.
If a path ends without a subcategory, set "subcategory": null in your JSON.

Format: domain > subdomain > category > subcategory (if exists)
═══════════════════════════════════════════════════════════════════════════════

"""
    return header + "\n".join(paths)


def validate_theme_hierarchy(
    theme: dict,
    valid_tuples: Set[Tuple[str, Optional[str], Optional[str], Optional[str]]]
) -> Tuple[bool, str]:
    """
    Validates a single theme's hierarchy against valid taxonomy paths.

    Args:
        theme: Theme dict with 'hierarchy' field
        valid_tuples: Set of valid (domain, subdomain, category, subcategory) tuples

    Returns:
        Tuple of (is_valid, error_message)
    """
    hierarchy = theme.get("hierarchy", {})
    label = theme.get("label", "Unknown")

    domain = hierarchy.get("domain")
    subdomain = hierarchy.get("subdomain")
    category = hierarchy.get("category")
    subcategory = hierarchy.get("subcategory")

    # Normalize None values
    subdomain = subdomain if subdomain else None
    category = category if category else None
    subcategory = subcategory if subcategory else None

    theme_tuple = (domain, subdomain, category, subcategory)

    if theme_tuple in valid_tuples:
        return True, ""

    # Check for hallucinated subcategory
    base_tuple = (domain, subdomain, category, None)
    if base_tuple in valid_tuples and subcategory is not None:
        return False, f"Theme '{label}': Hallucinated subcategory '{subcategory}' - this category has no subcategories"

    # Check for invalid category
    for valid in valid_tuples:
        if valid[0] == domain and valid[1] == subdomain:
            if category and category not in [v[2] for v in valid_tuples if v[0] == domain and v[1] == subdomain]:
                return False, f"Theme '{label}': Invalid category '{category}' under {domain} > {subdomain}"

    # Check for invalid subdomain
    for valid in valid_tuples:
        if valid[0] == domain:
            if subdomain and subdomain not in [v[1] for v in valid_tuples if v[0] == domain]:
                return False, f"Theme '{label}': Invalid subdomain '{subdomain}' under {domain}"

    # Check for invalid domain
    valid_domains = {v[0] for v in valid_tuples}
    if domain not in valid_domains:
        return False, f"Theme '{label}': Invalid domain '{domain}'"

    return False, f"Theme '{label}': Invalid hierarchy path {domain} > {subdomain} > {category} > {subcategory}"


def validate_taxonomy_compliance(
    tagged_data: dict,
    taxonomy: dict
) -> Tuple[bool, List[str]]:
    """
    Validates all themes in a tagged inscription against the taxonomy.

    Args:
        tagged_data: The full tagged inscription dict
        taxonomy: The taxonomy dict

    Returns:
        Tuple of (all_valid, list_of_errors)
    """
    _, valid_tuples = flatten_taxonomy(taxonomy)
    errors = []

    themes = tagged_data.get("themes", [])

    for theme in themes:
        is_valid, error = validate_theme_hierarchy(theme, valid_tuples)
        if not is_valid:
            errors.append(error)

    return len(errors) == 0, errors


def enforce_taxonomy_compliance(
    tagged_data: dict,
    taxonomy: dict
) -> Tuple[dict, List[str]]:
    """
    Strictly enforces taxonomy compliance by pruning invalid levels or removing invalid themes.
    
    Logic:
    1. Check if full path (domain, subdomain, category, subcategory) is valid.
    2. If not, try pruning 'subcategory'.
    3. If still not valid, try pruning 'category'.
    4. If still not valid, try pruning 'subdomain'.
    5. If still not valid, REMOVE the theme entirely.

    Args:
        tagged_data: The full tagged inscription dict
        taxonomy: The taxonomy dict

    Returns:
        Tuple of (corrected_data, list_of_corrections_made)
    """
    _, valid_tuples = flatten_taxonomy(taxonomy)
    corrections = []
    valid_themes = []

    themes = tagged_data.get("themes", [])

    for theme in themes:
        hierarchy = theme.get("hierarchy", {})
        label = theme.get("label", "Unknown")

        # Extract current path
        d = hierarchy.get("domain")
        sd = hierarchy.get("subdomain")
        c = hierarchy.get("category")
        sc = hierarchy.get("subcategory")
        
        # Normalize to None if empty string or None
        d = d if d else None
        sd = sd if sd else None
        c = c if c else None
        sc = sc if sc else None

        # 1. Check exact match
        if (d, sd, c, sc) in valid_tuples:
            valid_themes.append(theme)
            continue

        # 2. Try pruning subcategory
        if (d, sd, c, None) in valid_tuples:
            corrections.append(f"Theme '{label}': Pruned invalid subcategory '{sc}' -> kept category '{c}'")
            hierarchy["subcategory"] = None
            theme["hierarchy"] = hierarchy
            valid_themes.append(theme)
            continue

        # 3. Try pruning category
        if (d, sd, None, None) in valid_tuples:
            corrections.append(f"Theme '{label}': Pruned invalid category '{c}' -> kept subdomain '{sd}'")
            hierarchy["subcategory"] = None
            hierarchy["category"] = None
            theme["hierarchy"] = hierarchy
            valid_themes.append(theme)
            continue
            
        # 4. Try pruning subdomain
        if (d, None, None, None) in valid_tuples:
            corrections.append(f"Theme '{label}': Pruned invalid subdomain '{sd}' -> kept domain '{d}'")
            hierarchy["subcategory"] = None
            hierarchy["category"] = None
            hierarchy["subdomain"] = None
            theme["hierarchy"] = hierarchy
            valid_themes.append(theme)
            continue

        # 5. Drop theme if nothing fits
        corrections.append(f"Theme '{label}': REMOVED entire theme. Path {d}>{sd}>{c}>{sc} is invalid.")
    
    tagged_data["themes"] = valid_themes
    return tagged_data, corrections


def load_taxonomy(taxonomy_path: Path) -> dict:
    """Load taxonomy from JSON file."""
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# Quick test
if __name__ == "__main__":
    from .config import TAXONOMY_PATH

    taxonomy = load_taxonomy(TAXONOMY_PATH)
    paths, tuples = flatten_taxonomy(taxonomy)

    print(f"Total valid paths: {len(paths)}")
    print(f"Total valid tuples: {len(tuples)}")
    print("\nSample paths:")
    for p in paths[:20]:
        print(p)
