import json
import random
from pathlib import Path
from .config import INPUT_DIR, OUTPUT_DIR, TAXONOMY_DIR
from .data_loader import load_inscriptions
from .schema import TaggedInscription, Theme, Hierarchy, Entities, PersonEntity, PlaceEntity

def load_taxonomy():
    with open(TAXONOMY_DIR / "taxonomy.json", 'r', encoding='utf-8') as f:
        return json.load(f)

# --- Region Mapping (PHI -> Pleiades URI & Coordinates) ---
REGION_DATA = {
    "Attica": {"uri": "https://pleiades.stoa.org/places/579888", "coords": [38.0, 23.8]},
    "Peloponnese": {"uri": "https://pleiades.stoa.org/places/570599", "coords": [37.5, 22.4]},
    "Boeotia": {"uri": "https://pleiades.stoa.org/places/540677", "coords": [38.3, 23.1]},
    "Thessaly": {"uri": "https://pleiades.stoa.org/places/541136", "coords": [39.5, 22.2]},
    "Epirus": {"uri": "https://pleiades.stoa.org/places/540776", "coords": [39.6, 20.8]},
    "Macedonia": {"uri": "https://pleiades.stoa.org/places/491656", "coords": [40.7, 22.5]},
    "Thrace": {"uri": "https://pleiades.stoa.org/places/501616", "coords": [41.5, 25.5]},
    "Illyria": {"uri": "https://pleiades.stoa.org/places/481865", "coords": [40.5, 19.8]},
    "Crete": {"uri": "https://pleiades.stoa.org/places/589748", "coords": [35.2, 24.9]},
    "Aegean Islands": {"uri": "https://pleiades.stoa.org/places/579885", "coords": [37.0, 25.5]}, # General Aegean center
    "Delos": {"uri": "https://pleiades.stoa.org/places/599588", "coords": [37.39, 25.26]},
    "Asia Minor": {"uri": "https://pleiades.stoa.org/places/638753", "coords": [39.0, 32.0]}, # Asia
    "Caria": {"uri": "https://pleiades.stoa.org/places/638803", "coords": [37.5, 28.0]},
    "Ionia": {"uri": "https://pleiades.stoa.org/places/550597", "coords": [38.5, 27.5]},
    "Sicily": {"uri": "https://pleiades.stoa.org/places/462492", "coords": [37.5, 14.0]},
    "Italy": {"uri": "https://pleiades.stoa.org/places/1052", "coords": [42.0, 12.5]}
}

def get_region_info(region_name):
    """
    Fuzzy match PHI region name to our dataset.
    Returns (uri, coords) or (None, None)
    """
    if not region_name: return None, None
    
    # Try exact match
    if region_name in REGION_DATA:
        return REGION_DATA[region_name]["uri"], REGION_DATA[region_name]["coords"]
    
    # Try substring match
    for key, data in REGION_DATA.items():
        if key in region_name or region_name in key:
            return data["uri"], data["coords"]
            
    return None, None

def get_random_path(taxonomy_subset, current_path=None):
    if current_path is None: current_path = []
    if not isinstance(taxonomy_subset, dict) or not taxonomy_subset: return current_path
    key = random.choice(list(taxonomy_subset.keys()))
    return get_random_path(taxonomy_subset[key], current_path + [key])

def generate_theme_from_path(path, text):
    domain = path[0] if len(path) > 0 else "Unknown"
    subdomain = path[1] if len(path) > 1 else None
    category = path[2] if len(path) > 2 else None
    subcategory = path[3] if len(path) > 3 else None
    label = path[-1]
    
    words = text.split()
    quote = " ".join(words[random.randint(0, max(0,len(words)-10)):][:random.randint(3,10)]) if len(words) > 5 else text

    return Theme(
        label=label,
        hierarchy=Hierarchy(domain=domain, subdomain=subdomain, category=category, subcategory=subcategory),
        rationale=f"Generated rationale for {label}",
        confidence=round(random.uniform(0.6, 1.0), 2),
        quote=quote
    )

def generate_dummy_data(limit=50):
    inscriptions = load_inscriptions(INPUT_DIR, limit=limit)
    taxonomy = load_taxonomy()
    
    print(f"Generating LOD-linked data for {len(inscriptions)} inscriptions...")
    
    for inscription in inscriptions:
        themes = []
        if "Content" in taxonomy:
            themes.append(generate_theme_from_path(["Content"] + get_random_path(taxonomy["Content"]), inscription.text))
        if "Type" in taxonomy and random.random() > 0.3:
            themes.append(generate_theme_from_path(["Type"] + get_random_path(taxonomy["Type"]), inscription.text))

        # Get Region Info
        reg_uri, _ = get_region_info(inscription.region_main)

        # Entities
        persons = [PersonEntity(name="Theemos", role="Archon", uri="http://clas-lgpn2.classics.ox.ac.uk/cgi-bin/lgpn_search.cgi?name=Theemos")]
        places = [PlaceEntity(name="Athen", type="Polis", uri="https://pleiades.stoa.org/places/579885")]

        tagged = TaggedInscription(
            phi_id=inscription.id,
            themes=themes,
            entities=Entities(persons=persons, places=places),
            completeness=random.choice(["intact", "fragmentary"]),
            region_uri=reg_uri
        )
        
        with open(OUTPUT_DIR / f"{inscription.id}.json", 'w', encoding='utf-8') as f:
            f.write(tagged.model_dump_json(indent=2))
            
    print("Data generation complete.")

if __name__ == "__main__":
    generate_dummy_data()