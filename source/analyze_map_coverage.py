import json
from pathlib import Path
from source.config import OUTPUT_DIR, DATA_DIR

PLEIADES_CACHE_FILE = DATA_DIR / "pleiades_cache.json"

def load_pleiades_cache():
    if PLEIADES_CACHE_FILE.exists():
        with open(PLEIADES_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def analyze():
    cache = load_pleiades_cache()
    files = list(OUTPUT_DIR.glob("*.json"))
    print(f"Total inscriptions: {len(files)}")
    
    with_coords = 0
    missing_coords = 0
    
    unique_coords = set()
    total_resolved_uris = 0
    
    # Load gazetteer if possible, or just skip for this specific cache check
    # We focus on Pleiades cache hits here
    
    for f in files:
        with open(f, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        
        # Check Provenance
        prov = data.get('provenance', [])
        for p in prov:
            uri = p.get('uri')
            if uri and uri in cache and cache[uri]:
                unique_coords.add(tuple(cache[uri]))
                
        # Check Mentions
        entities = data.get('entities', {})
        places = entities.get('places', [])
        for pl in places:
            uri = pl.get('uri')
            if uri and uri in cache and cache[uri]:
                unique_coords.add(tuple(cache[uri]))

    print(f"Total Unique Resolved Coordinate Points (Prov + Men): {len(unique_coords)}")
    print(f"Total Resolved URIs in Cache: {len([k for k,v in cache.items() if v is not None])}")
    print(f"Total URIs in Cache (including failures): {len(cache)}")

if __name__ == "__main__":
    analyze()
