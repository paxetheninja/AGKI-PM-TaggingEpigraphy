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

def is_instance_of(wikidata_id, target_qids):
    """Check if a Wikidata item is an instance of one of the target QIDs."""
    if not wikidata_id: return False
    if isinstance(target_qids, str): target_qids = [target_qids]
    
    try:
        url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'AGKI-Reconciliation-Tool/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            entity = data.get("entities", {}).get(wikidata_id, {})
            # P31 is 'instance of'
            claims = entity.get("claims", {}).get("P31", [])
            for claim in claims:
                val = claim.get("mainsnak", {}).get("datavalue", {}).get("value")
                if isinstance(val, dict) and val.get("id") in target_qids:
                    return True
    except Exception:
        pass
    return False

def is_human_in_wikidata(wikidata_id):
    """Check if a Wikidata item is an instance of human (Q5)."""
    return is_instance_of(wikidata_id, ["Q5"])

def is_deity_in_wikidata(wikidata_id):
    """Check if a Wikidata item is a deity or mythological character."""
    # Known exact matches for groups/classes that might lack P31 or be instances of themselves
    if wikidata_id in ["Q373916", "Q66016"]: # Nymph, Muse
        return True

    # Expanded list of QIDs
    # Q178885: deity, Q22989102: Greek deity, Q11688446: Roman deity, Q146083: Egyptian deity
    # Q4271324: mythological character, Q35277: deity (alt), Q48350: mythological character
    # Q2194631: hero, Q215627: Titan, Q9135: Olympian god, Q24322474: deity of ancient Greece
    # Q23015925: demigod of Greco-Roman mythology, Q134556: Greek deity
    # Q182406: Personification, Q1916821: Goddess, Q113302: God, Q50078178: God of Healing
    # Q28061975: class of Greek mythological figures (e.g. Muses)
    deity_qids = [
        "Q178885", "Q22989102", "Q11688446", "Q146083", "Q4271324", "Q35277", 
        "Q48350", "Q2194631", "Q215627", "Q9135", "Q24322474", "Q205985", "Q346660",
        "Q23015925", "Q134556", "Q182406", "Q1916821", "Q113302", "Q50078178", "Q28061975"
    ]
    return is_instance_of(wikidata_id, deity_qids)

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
            "search": query,
            "limit": 7  # Increase limit to find better matches
        }
        url = f"https://www.wikidata.org/w/api.php?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'AGKI-Reconciliation-Tool/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get("search"):
                # Check the first few results for the right type
                for result in data['search']:
                    desc = result.get('description', '').lower()
                    
                    # Heuristic filtering for Persons (Q5)
                    if type_filter == "Q5":
                        # Skip obviously modern persons
                        if any(x in desc for x in ["born", "19", "20", "football", "player", "actor", "politician", "american", "british"]):
                            if not any(x in desc for x in ["ancient", "bc", "bce", "greek", "roman", "strategos", "archon"]):
                                continue # Skip if modern and no ancient keywords
                        
                        if is_human_in_wikidata(result['id']):
                            uri = f"https://www.wikidata.org/wiki/{result['id']}"
                            target_cache[cache_key] = uri
                            return uri
                            
                    # Heuristic for Deities
                    elif type_filter in ["Q35277", "Q178885"]:
                        if is_deity_in_wikidata(result['id']):
                            uri = f"https://www.wikidata.org/wiki/{result['id']}"
                            target_cache[cache_key] = uri
                            return uri
                    else:
                        # For others, assume top rank is OK (or improve logic later)
                        uri = f"https://www.wikidata.org/wiki/{result['id']}"
                        target_cache[cache_key] = uri
                        return uri
    except Exception:
        pass
    
    target_cache[cache_key] = None
    return None

def reconcile_deity(name):
    """Search Wikidata for a deity."""
    # Wikidata Q35277 is 'deity'
    uri = reconcile_wikidata(name, "Q35277")
    if uri: return uri
    
    # Fallback 1: Try splitting epithets (e.g. "Zeus Keraunios" -> "Zeus")
    if " " in name:
        main_name = name.split(" ")[0]
        if len(main_name) > 2:
            uri_fallback = reconcile_wikidata(main_name, "Q35277")
            if uri_fallback:
                CACHE["deities"][name] = uri_fallback # Cache under full name too
                return uri_fallback
    
    # Fallback 2: Try singular form (e.g. "Nymphs" -> "Nymph")
    if name.endswith("s"):
        uri_singular = reconcile_wikidata(name[:-1], "Q35277")
        if uri_singular:
            CACHE["deities"][name] = uri_singular
            return uri_singular

    # Fallback 3: Try appending " (mythology)" for ambiguous names (e.g. "Nike")
    uri_myth = reconcile_wikidata(f"{name} (mythology)", "Q35277")
    if uri_myth:
        CACHE["deities"][name] = uri_myth
        return uri_myth
        
    return None

def reconcile_person(name, role=None):
    """Search Wikidata (Human) first, then fallback to LGPN."""
    if not name or len(name) < 3: return None
    
    cached_uri = CACHE["persons"].get(name)
    # Invalidate old LGPN links in cache
    if cached_uri and "clas-lgpn2.classics.ox.ac.uk" in cached_uri:
        cached_uri = None
        
    if cached_uri: return cached_uri
    
    # 1. Try Wikidata (Q5 - Human)
    wd_uri = reconcile_wikidata(name, "Q5")
    if wd_uri:
        CACHE["persons"][name] = wd_uri
        return wd_uri

    # 2. Fallback to LGPN Search
    search_url = f"https://search.lgpn.ox.ac.uk/browse.html?field=names&sort=nymRef&query={urllib.parse.quote(name)}"
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
    
    # Force retry for deities that were previously not found
    print("Pruning 'None' entries from deity cache to force re-check...")
    CACHE["deities"] = {k: v for k, v in CACHE["deities"].items() if v is not None}
    
    # Explicitly clear specific problematic keys (including with type suffixes) if they exist
    for name in ["Heracles", "Nike", "Nymphs", "Muses", "Tyche", "Demos", "Isis"]:
        keys_to_remove = [k for k in CACHE["deities"] if name in k]
        for k in keys_to_remove:
            del CACHE["deities"][k]

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
