import json
from pathlib import Path

CACHE_FILE = Path("data/reconciliation_cache.json")
OUTPUT_DIR = Path("data/output")

OLD_BASE = "http://id.lgpn.ox.ac.uk/id/search?name="
NEW_BASE = "http://clas-lgpn2.classics.ox.ac.uk/cgi-bin/lgpn_search.cgi?name="

def fix_url(url):
    if url and isinstance(url, str) and url.startswith(OLD_BASE):
        return url.replace(OLD_BASE, NEW_BASE)
    return url

def main():
    print("Starting LGPN link fix...")
    
    # 1. Fix Cache
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            fixed_count = 0
            if "persons" in cache:
                for name, url in cache["persons"].items():
                    new_url = fix_url(url)
                    if new_url != url:
                        cache["persons"][name] = new_url
                        fixed_count += 1
            
            if fixed_count > 0:
                with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, indent=2, ensure_ascii=False)
                print(f"Fixed {fixed_count} links in cache.")
            else:
                print("No links to fix in cache.")
        except Exception as e:
            print(f"Error processing cache: {e}")

    # 2. Fix Output Files
    if OUTPUT_DIR.exists():
        files = list(OUTPUT_DIR.glob("*.json"))
        fixed_files = 0
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                changed = False
                persons = data.get("entities", {}).get("persons", [])
                for person in persons:
                    url = person.get("uri")
                    new_url = fix_url(url)
                    if new_url != url:
                        person["uri"] = new_url
                        changed = True
                
                if changed:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    fixed_files += 1
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                
        print(f"Fixed links in {fixed_files} output files.")
    else:
        print(f"Output directory not found: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()