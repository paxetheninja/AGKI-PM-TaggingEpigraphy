import random
import json
import logging
from pathlib import Path
from tqdm import tqdm

from .config import INPUT_DIR, OUTPUT_DIR, TAXONOMY_DIR, DEFAULT_MODEL_NAME
from .data_loader import load_inscriptions
from .preprocessing import clean_metadata
from .llm_client import get_llm_client
from .tagger import tag_inscription

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Real API Test Run (10 Random Samples)")

    # 1. Load Data
    logger.info(f"Loading inscriptions from {INPUT_DIR}...")
    all_inscriptions = load_inscriptions(INPUT_DIR)
    
    if not all_inscriptions:
        logger.error("No inscriptions found in input directory.")
        return
    
    # Select 10 random inscriptions
    # Use a fixed seed for reproducibility if needed, but random is fine for a test
    selected_inscriptions = random.sample(all_inscriptions, min(10, len(all_inscriptions)))
    logger.info(f"Selected {len(selected_inscriptions)} inscriptions for testing.")

    # 2. Load Taxonomy
    taxonomy_path = TAXONOMY_DIR / "taxonomy.json"
    if not taxonomy_path.exists():
        logger.error(f"Taxonomy file not found at {taxonomy_path}")
        return
        
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        taxonomy = json.load(f)
    logger.info("Taxonomy loaded.")

    # 3. Setup LLM Client
    try:
        llm_client = get_llm_client()
        logger.info(f"LLM Client initialized. Target Model: {DEFAULT_MODEL_NAME}")
    except Exception as e:
        logger.error(f"Failed to initialize LLM Client: {e}")
        logger.error("Please check your .env file and API keys.")
        return

    # 4. Processing Loop
    success_count = 0
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for inscription in tqdm(selected_inscriptions, desc="Tagging"):
        try:
            # Preprocess
            clean_inscription = clean_metadata(inscription)
            
            # Tag
            # This calls the LLM with the prompt containing the inscription and taxonomy
            tagged_result = tag_inscription(
                inscription=clean_inscription,
                llm_client=llm_client,
                taxonomy=taxonomy,
                model=DEFAULT_MODEL_NAME
            )
            
            # Save Output to Real Output Dir
            output_file = OUTPUT_DIR / f"{inscription.id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(tagged_result.model_dump_json(indent=2))
            
            success_count += 1
            
        except Exception as e:
            logger.error(f"Error processing ID {inscription.id}: {e}")

    logger.info(f"Test Complete. Successfully tagged {success_count}/{len(selected_inscriptions)} inscriptions.")
    logger.info(f"Results saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
