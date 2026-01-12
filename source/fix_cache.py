import json
from pathlib import Path
from source.config import DATA_DIR

PLEIADES_CACHE_FILE = DATA_DIR / "pleiades_cache.json"

def fix_cache():
    if not PLEIADES_CACHE_FILE.exists():
        print("No cache file.")
        return

    with open(PLEIADES_CACHE_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    initial_len = len(cache)
    # Remove keys where value is None
    new_cache = {k: v for k, v in cache.items() if v is not None}
    final_len = len(new_cache)
    
    with open(PLEIADES_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_cache, f, ensure_ascii=False)
        
    print(f"Cleaned cache. Removed {initial_len - final_len} failure entries. Remaining: {final_len}")

if __name__ == "__main__":
    fix_cache()
