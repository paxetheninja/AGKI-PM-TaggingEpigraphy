import json
import random
from pathlib import Path
from .config import INPUT_DIR, OUTPUT_DUMMY_DIR, TAXONOMY_DIR
from .data_loader import load_inscriptions
from .schema import TaggedInscription, Theme, Hierarchy, Entities, PersonEntity, PlaceEntity, GeoLocation

def load_taxonomy():
    with open(TAXONOMY_DIR / "taxonomy.json", 'r', encoding='utf-8') as f:
        return json.load(f)

# --- Expanded Mock Hierarchy ---
# Key = Region, Value = List of (City, URI, Coords)
HIERARCHY_DATA = {
    "Attica": [
        ("Athen", "https://pleiades.stoa.org/places/579885", [37.97, 23.72]),
        ("Eleusis", "https://pleiades.stoa.org/places/579920", [38.04, 23.54]),
        ("Brauron", "https://pleiades.stoa.org/places/579880", [37.92, 23.99])
    ],
    "Peloponnese": [
        ("Sparta", "https://pleiades.stoa.org/places/570685", [37.07, 22.43]),
        ("Korinth", "https://pleiades.stoa.org/places/570182", [37.90, 22.88]),
        ("Olympia", "https://pleiades.stoa.org/places/570531", [37.63, 21.63])
    ],
    "Boeotia": [
        ("Theben", "https://pleiades.stoa.org/places/541138", [38.32, 23.32]),
        ("Tanagra", "https://pleiades.stoa.org/places/541132", [38.31, 23.53])
    ],
    "Delos": [
        ("Delos (City)", "https://pleiades.stoa.org/places/599588", [37.39, 25.26]),
        ("Sanctuary of Apollo", "https://pleiades.stoa.org/places/599588", [37.40, 25.27])
    ],
    # Fallback for regions with no specific city logic in this dummy script
    "Macedonia": [("Pella", "https://pleiades.stoa.org/places/491687", [40.76, 22.52])],
    "Asia Minor": [("Ephesos", "https://pleiades.stoa.org/places/599612", [37.94, 27.36])],
    "Crete": [("Knossos", "https://pleiades.stoa.org/places/589852", [35.29, 25.16])]
}

REGION_URIS = {
    "Attica": "https://pleiades.stoa.org/places/579888",
    "Peloponnese": "https://pleiades.stoa.org/places/570599",
    "Boeotia": "https://pleiades.stoa.org/places/540677",
    "Thessaly": "https://pleiades.stoa.org/places/541136",
    "Epirus": "https://pleiades.stoa.org/places/540776",
    "Macedonia": "https://pleiades.stoa.org/places/491656",
    "Thrace": "https://pleiades.stoa.org/places/501616",
    "Illyria": "https://pleiades.stoa.org/places/481865",
    "Crete": "https://pleiades.stoa.org/places/589748",
    "Aegean Islands": "https://pleiades.stoa.org/places/579885",
    "Delos": "https://pleiades.stoa.org/places/599588",
    "Asia Minor": "https://pleiades.stoa.org/places/638753"
}

def get_random_provenance(region_name):
    """Generates a hierarchical list: [Region, City?] based on knowledge."""
    prov = []
    
    # 1. Macro Region
    # Try to match PHI region to our keys
    matched_key = None
    for k in REGION_URIS:
        if k in region_name:
            matched_key = k
            break
            
    if matched_key:
        prov.append(GeoLocation(name=matched_key, type="Region", uri=REGION_URIS[matched_key]))
        
        # 2. Subregion/City (Randomly pick one if available for this region)
        if matched_key in HIERARCHY_DATA and random.random() > 0.3:
            city_name, city_uri, _ = random.choice(HIERARCHY_DATA[matched_key])
            prov.append(GeoLocation(name=city_name, type="Polis", uri=city_uri))
    else:
        # Fallback
        prov.append(GeoLocation(name=region_name, type="Region"))
        
    return prov

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
    print(f"Generating hierarchical dummy data for {len(inscriptions)} inscriptions...")
    
    for inscription in inscriptions:
        themes = []
        if "Content" in taxonomy:
            themes.append(generate_theme_from_path(["Content"] + get_random_path(taxonomy["Content"]), inscription.text))
        if "Type" in taxonomy and random.random() > 0.3:
            themes.append(generate_theme_from_path(["Type"] + get_random_path(taxonomy["Type"]), inscription.text))

        persons = [PersonEntity(name="Theemos", role="Archon", uri="http://clas-lgpn2.classics.ox.ac.uk/cgi-bin/lgpn_search.cgi?name=Theemos")]
        places = [PlaceEntity(name="Athen", type="Polis", uri="https://pleiades.stoa.org/places/579885")]

        tagged = TaggedInscription(
            phi_id=inscription.id,
            themes=themes,
            entities=Entities(persons=persons, places=places),
            completeness=random.choice(["intact", "fragmentary"]),
            provenance=get_random_provenance(inscription.region_main),
            model="dummy-generator-v2"
        )
        
        with open(OUTPUT_DUMMY_DIR / f"{inscription.id}.json", 'w', encoding='utf-8') as f:
            f.write(tagged.model_dump_json(indent=2))
            
    print("Generation complete.")

if __name__ == "__main__":
    generate_dummy_data()
