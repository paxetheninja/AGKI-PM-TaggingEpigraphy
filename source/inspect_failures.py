import json
from pathlib import Path
from source.config import DATA_DIR

PLEIADES_CACHE_FILE = DATA_DIR / "pleiades_cache.json"

def inspect_failures():
    if not PLEIADES_CACHE_FILE.exists():
        print("No cache file.")
        return

    with open(PLEIADES_CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    failures = [k for k,v in cache.items() if v is None]
    print(f"Total failures: {len(failures)}")
    print("First 20 failed URIs:")
    for uri in failures[:20]:
        print(f"  {uri}")

if __name__ == "__main__":
    inspect_failures()
