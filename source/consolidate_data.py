import json
from pathlib import Path
from .config import OUTPUT_DIR

DOCS_DATA_PATH = Path("website/assets/js/data.js")

def consolidate_data():
    all_data = []
    files = list(OUTPUT_DIR.glob("*.json"))
    
    print(f"Consolidating {len(files)} JSON files...")
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_data.append(data)
            
    # Wrap in a JS variable assignment
    js_content = f"const PROJECT_DATA = {json.dumps(all_data, ensure_ascii=False, indent=2)};"
    
    DOCS_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(DOCS_DATA_PATH, 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"Data saved to {DOCS_DATA_PATH}")

if __name__ == "__main__":
    consolidate_data()
