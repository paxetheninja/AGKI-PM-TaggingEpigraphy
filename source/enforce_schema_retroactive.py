"""
Retroactively enforces taxonomy compliance on existing output files.
Reads each JSON file in data/output/, applies the new pruning logic, and saves it back if changes are made.
"""
import json
import logging
from pathlib import Path
from tqdm import tqdm

from source.config import OUTPUT_DIR, TAXONOMY_DIR
from source.taxonomy_utils import enforce_taxonomy_compliance, load_taxonomy

# Define path
TAXONOMY_PATH = TAXONOMY_DIR / "taxonomy.json"

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Loading taxonomy...")
    try:
        taxonomy = load_taxonomy(TAXONOMY_PATH)
    except Exception as e:
        logger.error(f"Failed to load taxonomy: {e}")
        return

    logger.info(f"Scanning {OUTPUT_DIR}...")
    files = list(OUTPUT_DIR.glob("*.json"))
    
    if not files:
        logger.info("No files found to process.")
        return

    modified_count = 0
    total_corrections = 0
    
    # Use tqdm for progress bar
    for file_path in tqdm(files, desc="Enforcing Schema"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Apply enforcement
            # We only care about the 'themes' part for taxonomy compliance
            if "themes" in data:
                original_themes = json.dumps(data["themes"], sort_keys=True)
                
                # Run the enforcement
                corrected_data, corrections = enforce_taxonomy_compliance(data, taxonomy)
                
                # Check if changes actually happened (enforce_taxonomy_compliance modifies in-place, but returns tuple)
                new_themes = json.dumps(corrected_data["themes"], sort_keys=True)
                
                if corrections:
                    modified_count += 1
                    total_corrections += len(corrections)
                    
                    # Log corrections (compactly)
                    # tqdm.write(f"Fixed {file_path.name}: {len(corrections)} corrections")
                    
                    # Save back to file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(corrected_data, f, indent=2, ensure_ascii=False)
                        
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")

    logger.info("=" * 40)
    logger.info(f"Processing Complete.")
    logger.info(f"Files Modified: {modified_count}/{len(files)}")
    logger.info(f"Total Corrections Applied: {total_corrections}")
    logger.info("=" * 40)

if __name__ == "__main__":
    main()
