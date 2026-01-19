"""
Parallel processing version of the tagging pipeline.
Uses concurrent.futures for parallel inscription processing.
"""
import json
import logging
import os
import datetime
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from .config import INPUT_DIR, OUTPUT_DIR, TAXONOMY_DIR, DEFAULT_MODEL_NAME, LOG_LEVEL, LOGS_DIR
from .data_loader import load_inscriptions
from .preprocessing import clean_metadata
from .llm_client import get_llm_client
from .tagger import tag_inscription

# Setup Logging
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = LOGS_DIR / f"pipeline_parallel_{timestamp}.log"

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Thread-safe counters
counter_lock = Lock()
counters = {"success": 0, "skip": 0, "error": 0}


def load_taxonomy():
    taxonomy_path = TAXONOMY_DIR / "taxonomy.json"
    if not taxonomy_path.exists():
        raise FileNotFoundError(f"Taxonomy file not found at {taxonomy_path}")
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def process_single_inscription(inscription, llm_client, taxonomy, model, output_dir):
    """Process a single inscription. Thread-safe."""
    output_file = output_dir / f"{inscription.id}.json"

    # Cache check
    if output_file.exists():
        with counter_lock:
            counters["skip"] += 1
        return {"id": inscription.id, "status": "skipped"}

    try:
        logger.info(f"Processing Inscription ID: {inscription.id}")

        # Preprocess
        clean_inscription = clean_metadata(inscription)

        # Tag
        tagged_result = tag_inscription(
            inscription=clean_inscription,
            llm_client=llm_client,
            taxonomy=taxonomy,
            model=model
        )

        # Save Output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(tagged_result.model_dump_json(indent=2))

        with counter_lock:
            counters["success"] += 1

        logger.info(f"Completed Inscription ID: {inscription.id}")
        return {"id": inscription.id, "status": "success"}

    except Exception as e:
        with counter_lock:
            counters["error"] += 1
        logger.error(f"Error processing ID {inscription.id}: {e}")
        return {"id": inscription.id, "status": "error", "error": str(e)}


def main():
    # Configuration
    max_inscriptions = int(os.getenv("MAX_INSCRIPTIONS", -1))
    max_workers = int(os.getenv("MAX_WORKERS", 5))  # Concurrent workers

    logger.info("=" * 60)
    logger.info("Starting AGKI-PM-TaggingEpigraphy Pipeline (PARALLEL MODE)")
    logger.info(f"Max workers: {max_workers}")
    logger.info(f"Max inscriptions: {max_inscriptions if max_inscriptions > 0 else 'unlimited'}")
    logger.info("=" * 60)

    # 1. Load Data
    logger.info(f"Loading inscriptions from {INPUT_DIR}...")
    inscriptions = load_inscriptions(INPUT_DIR)
    logger.info(f"Found {len(inscriptions)} inscriptions.")

    if not inscriptions:
        logger.warning("No input files found. Please place JSON files in data/input/")
        return

    # Shuffle for random selection if limiting
    random.shuffle(inscriptions)

    # Limit if specified
    if max_inscriptions > 0:
        inscriptions = inscriptions[:max_inscriptions]
        logger.info(f"Limited to {len(inscriptions)} inscriptions")

    # 2. Load Taxonomy
    try:
        taxonomy = load_taxonomy()
        logger.info("Taxonomy loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load taxonomy: {e}")
        return

    # 3. Setup LLM Client (shared across threads - thread-safe)
    try:
        llm_client = get_llm_client()
        logger.info(f"LLM Client initialized (Model: {DEFAULT_MODEL_NAME})")
    except Exception as e:
        logger.error(f"Failed to initialize LLM Client: {e}")
        return

    # 4. Parallel Processing
    logger.info(f"Starting parallel processing with {max_workers} workers...")
    start_time = datetime.datetime.now()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_inscription = {
            executor.submit(
                process_single_inscription,
                inscription,
                llm_client,
                taxonomy,
                DEFAULT_MODEL_NAME,
                OUTPUT_DIR
            ): inscription
            for inscription in inscriptions
        }

        # Process results as they complete
        completed = 0
        total = len(inscriptions)

        for future in as_completed(future_to_inscription):
            completed += 1
            result = future.result()

            # Progress update every 10 inscriptions
            if completed % 10 == 0 or completed == total:
                elapsed = (datetime.datetime.now() - start_time).total_seconds()
                rate = completed / elapsed if elapsed > 0 else 0
                eta = (total - completed) / rate if rate > 0 else 0
                logger.info(
                    f"Progress: {completed}/{total} ({100*completed/total:.1f}%) | "
                    f"Rate: {rate:.2f}/sec | ETA: {eta:.0f}s | "
                    f"Success: {counters['success']}, Errors: {counters['error']}, Skipped: {counters['skip']}"
                )

    # 5. Summary
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info("=" * 60)
    logger.info("Pipeline Complete.")
    logger.info(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    logger.info(f"Processed: {counters['success']}, Skipped: {counters['skip']}, Failed: {counters['error']}")
    logger.info(f"Effective rate: {counters['success'] / duration:.2f} inscriptions/second")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
