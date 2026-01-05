import json
import logging
from pathlib import Path
from tqdm import tqdm

from .config import INPUT_DIR, OUTPUT_DIR, TAXONOMY_DIR, DEFAULT_MODEL_NAME, LOG_LEVEL
from .data_loader import load_inscriptions
from .preprocessing import clean_metadata
from .llm_client import get_llm_client
from .tagger import tag_inscription

# Setup Logging
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_taxonomy():
    taxonomy_path = TAXONOMY_DIR / "taxonomy.json"
    if not taxonomy_path.exists():
        raise FileNotFoundError(f"Taxonomy file not found at {taxonomy_path}")
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    logger.info("Starting AGKI-PM-TaggingEpigraphy Pipeline")
    
    # 1. Load Data
    logger.info(f"Loading inscriptions from {INPUT_DIR}...")
    inscriptions = load_inscriptions(INPUT_DIR)
    logger.info(f"Found {len(inscriptions)} inscriptions.")
    
    if not inscriptions:
        logger.warning("No input files found. Please place JSON files in data/input/")
        return

    # 2. Load Taxonomy
    try:
        taxonomy = load_taxonomy()
        logger.info("Taxonomy loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load taxonomy: {e}")
        return

    # 3. Setup LLM Client
    try:
        llm_client = get_llm_client()
        logger.info(f"LLM Client initialized (Model: {DEFAULT_MODEL_NAME})")
    except Exception as e:
        logger.error(f"Failed to initialize LLM Client: {e}")
        return

    # 4. Processing Loop
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for inscription in tqdm(inscriptions, desc="Tagging Inscriptions"):
        output_file = OUTPUT_DIR / f"{inscription.id}.json"
        
        # Cache check
        if output_file.exists():
            skip_count += 1
            continue
            
        try:
            # Preprocess
            clean_inscription = clean_metadata(inscription)
            
            # Tag
            tagged_result = tag_inscription(
                inscription=clean_inscription,
                llm_client=llm_client,
                taxonomy=taxonomy,
                model=DEFAULT_MODEL_NAME
            )
            
            # Save Output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(tagged_result.model_dump_json(indent=2))
            
            success_count += 1
            
        except Exception as e:
            error_count += 1
            logger.error(f"Error processing ID {inscription.id}: {e}")

    logger.info("Pipeline Complete.")
    logger.info(f"Processed: {success_count}, Skipped: {skip_count}, Failed: {error_count}")

if __name__ == "__main__":
    main()
