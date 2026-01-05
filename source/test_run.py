import json
import logging
from pathlib import Path
from .config import INPUT_DIR, OUTPUT_DIR, TAXONOMY_DIR, DEFAULT_MODEL_NAME
from .data_loader import load_inscription
from .preprocessing import clean_metadata
from .llm_client import get_llm_client
from .tagger import tag_inscription

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Single Inscription Test Run")
    
    test_file = INPUT_DIR / "test_inscription.json"
    if not test_file.exists():
        logger.error(f"Test file not found: {test_file}")
        return

    # 1. Load Data
    logger.info(f"Loading test inscription from {test_file}...")
    inscription = load_inscription(test_file)
    
    # 2. Load Taxonomy
    taxonomy_path = TAXONOMY_DIR / "taxonomy.json"
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        taxonomy = json.load(f)

    # 3. Setup LLM Client
    llm_client = get_llm_client()
    
    # 4. Process
    try:
        # Preprocess
        clean_inscription = clean_metadata(inscription)
        
        # Tag
        logger.info("Sending request to LLM...")
        tagged_result = tag_inscription(
            inscription=clean_inscription,
            llm_client=llm_client,
            taxonomy=taxonomy,
            model=DEFAULT_MODEL_NAME
        )
        
        # 5. Output Results
        print("\n--- Tagging Result ---\n")
        print(tagged_result.model_dump_json(indent=2))
        
        # Save to file
        output_file = OUTPUT_DIR / "test_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(tagged_result.model_dump_json(indent=2))
        logger.info(f"Result saved to {output_file}")

    except Exception as e:
        logger.error(f"Error processing test inscription: {e}")

if __name__ == "__main__":
    main()
