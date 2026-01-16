import json
import time
import urllib.request
import urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import OUTPUT_DIR
from .gazetteer import get_gazetteer

# --- Configuration & Cache ---
RECONCILIATION_CACHE_FILE = Path("data/reconciliation_cache.json")
CACHE = {"places": {}, "deities": {}, "persons": {}}

def load_cache():
    global CACHE
    if RECONCILIATION_CACHE_FILE.exists():
        try:
            with open(RECONCILIATION_CACHE_FILE, 'r', encoding='utf-8') as f:
                CACHE.update(json.load(f))
        except Exception:
            pass

def save_cache():
    with open(RECONCILIATION_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(CACHE, f, indent=2, ensure_ascii=False)

# --- Manual Overrides ---
# Manual list of known Pleiades URIs to avoid bot protection (Anubis) and ensure accuracy
# These take precedence over the Gazetteer and Wikidata
MANUAL_OVERRIDES = {
    "Athens": "https://pleiades.stoa.org/places/579885",
    "Athen": "https://pleiades.stoa.org/places/579885",
    "Rhamnous": "https://pleiades.stoa.org/places/580097", 
    "Akropolis": "https://pleiades.stoa.org/places/579885", # Map to Athens
    "Acropolis": "https://pleiades.stoa.org/places/579885",
    "Sparta": "https://pleiades.stoa.org/places/570685",
    "Korinth": "https://pleiades.stoa.org/places/570182"
}

# --- Reconciliation Logic ---

def get_pleiades_from_wikidata(wikidata_id):
    """Attempt to get Pleiades ID from a Wikidata item."""
    try:
        url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'AGKI-Reconciliation-Tool/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            entity = data.get("entities", {}).get(wikidata_id, {})
            # P1566 is Pleiades ID
            claims = entity.get("claims", {}).get("P1566", [])
            if claims:
                pleiades_id = claims[0].get("mainsnak", {}).get("datavalue", {}).get("value")
                if pleiades_id:
                    return f"https://pleiades.stoa.org/places/{pleiades_id}"
    except Exception:
        pass
    return None

def search_pleiades_offline(name):
    """Search using the local offline gazetteer (dump)."""
    gaz = get_gazetteer()
    return gaz.search(name)

def is_human_in_wikidata(wikidata_id):
    """Check if a Wikidata item is an instance of human (Q5)."""
    try:
        url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'AGKI-Reconciliation-Tool/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            entity = data.get("entities", {}).get(wikidata_id, {})
            # P31 is 'instance of', Q5 is 'human'
            claims = entity.get("claims", {}).get("P31", [])
            for claim in claims:
                target_id = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
                if target_id == "Q5":
                    return True
    except Exception:
        pass
    return False

def reconcile_place(name, place_type=None):
    """Search for a place, primarily via Wikidata which often links to Pleiades, or direct Pleiades search."""
    if not name or len(name) < 3: return None
    
    # 0. Check Manual Overrides
    if name in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[name]
    
    if name in CACHE["places"]: return CACHE["places"][name]

    # 1. Try Offline Gazetteer (Best for Pleiades specific coverage)
    gaz_uri = search_pleiades_offline(name)
    if gaz_uri:
        CACHE["places"][name] = gaz_uri
        return gaz_uri

    # 2. Try Wikidata search
    # Broaden filters: Q618123 (archaeological site), Q515 (city), Q1549593 (ancient city), Q1048835 (historical settlement)
    for qid in ["Q618123", "Q515", "Q1549593", "Q1048835"]:
        wd_uri = reconcile_wikidata(name, qid)
        if wd_uri:
            wikidata_id = wd_uri.split('/')[-1]
            pleiades_uri = get_pleiades_from_wikidata(wikidata_id)
            if pleiades_uri:
                CACHE["places"][name] = pleiades_uri
                return pleiades_uri
            # Keep the first valid Wikidata URI as a fallback
            if "first_wd" not in locals():
                first_wd = wd_uri
    
    # 3. Fallback to Wikidata URI if we found one earlier
    uri = locals().get("first_wd")
    CACHE["places"][name] = uri
    return uri

def reconcile_wikidata(name, type_filter=None):
    """
    Search Wikidata for an entity.
    type_filter: Q35277 (Deity), Q5 (Human), etc. Used for cache keys and basic validation.
    """
    if not name: return None
    
    # Select appropriate cache
    if type_filter == "Q35277":
        target_cache = CACHE["deities"]
    elif type_filter == "Q5":
        target_cache = CACHE["persons"]
    else:
        target_cache = CACHE["places"]

    cache_key = f"{name}_{type_filter}" if type_filter else name
    if cache_key in target_cache: return target_cache[cache_key]

    try:
        query = name
        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "type": "item",
            "search": query
        }
        url = f"https://www.wikidata.org/w/api.php?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'AGKI-Reconciliation-Tool/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get("search"):
                # Check the first few results for the right type
                for result in data['search'][:3]:
                    uri = f"https://www.wikidata.org/wiki/{result['id']}"
                    
                    # If we are looking for a Person (Q5), verify it's human
                    if type_filter == "Q5":
                        if is_human_in_wikidata(result['id']):
                            target_cache[cache_key] = uri
                            return uri
                    else:
                        # For others, assume top rank is OK (or improve logic later)
                        target_cache[cache_key] = uri
                        return uri
    except Exception:
        pass
    
    target_cache[cache_key] = None
    return None

def reconcile_deity(name):
    """Search Wikidata for a deity."""
    # Wikidata Q35277 is 'deity'
    return reconcile_wikidata(name, "Q35277")

def reconcile_person(name, role=None):
    """Search Wikidata (Human) first, then fallback to LGPN."""
    if not name or len(name) < 3: return None
    if name in CACHE["persons"]: return CACHE["persons"][name]
    
    # 1. Try Wikidata (Q5 - Human)
    wd_uri = reconcile_wikidata(name, "Q5")
    if wd_uri:
        CACHE["persons"][name] = wd_uri
        return wd_uri

    # 2. Fallback to LGPN Search
    search_url = f"http://id.lgpn.ox.ac.uk/id/search?name={urllib.parse.quote(name)}"
    CACHE["persons"][name] = search_url
    return search_url

# --- Main Processing ---

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    changed = False
    entities = data.get("entities", {})
    
    # 1. Deities
    for deity in entities.get("deities", []):
        uri = reconcile_deity(deity["name"])
        if uri and uri != deity.get("uri"):
            deity["uri"] = uri
            changed = True
    
    # 2. Places
    for place in entities.get("places", []):
        uri = reconcile_place(place["name"], place.get("type"))
        if uri and uri != place.get("uri"):
            place["uri"] = uri
            changed = True
                
    # 3. Persons
    for person in entities.get("persons", []):
        uri = reconcile_person(person["name"], person.get("role"))
        if uri and uri != person.get("uri"):
            person["uri"] = uri
            changed = True

    # 4. Provenance
    for loc in data.get("provenance", []):
        uri = reconcile_place(loc["name"], loc.get("type"))
        if uri and uri != loc.get("uri"):
            loc["uri"] = uri
            changed = True

    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    return changed

def main():
    load_cache()
    files = list(OUTPUT_DIR.glob("*.json"))
    print(f"Reconciling entities in {len(files)} files...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_file, f): f for f in files}
        count = 0
        for future in as_completed(futures):
            if future.result():
                count += 1
            if (len(futures) - len(futures)) % 50 == 0:
                pass # progress
    
    print(f"Reconciliation complete. Updated {count} files.")
    save_cache()

if __name__ == "__main__":
    main()
