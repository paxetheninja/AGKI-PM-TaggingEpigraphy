# Implementation Task List: AGKI-PM-TaggingEpigraphy

This document outlines the technical tasks required to implement the automated tagging pipeline for Greek epigraphic inscriptions using LLMs.

## Phase 1: Environment & Project Structure
- [x] **Initialize Python Project**
    - [x] Create `requirements.txt` / `pyproject.toml`.
    - [x] Set up virtual environment.
    - [x] Configure linting/formatting (Ruff/Black).
- [x] **Directory Setup**
    - [x] Ensure `data/input`, `data/output`, `data/taxonomy` directories exist.
    - [x] Create `source/config.py` for project-wide settings (paths, API keys).

## Phase 2: Data Ingestion & Preprocessing
- [x] **Data Loader Module**
    - [x] Implement function to read raw PHI-JSON files.
    - [x] Create Pydantic models for `InputInscription` to validate incoming data.
- [x] **Preprocessing Module**
    - [x] Implement text normalization (handling polytonic Greek, brackets).
    - [x] Implement metadata cleaning (date standardization, region formatting).
    - [x] Unit tests for normalization logic.

## Phase 3: Taxonomy & Schema Management
- [x] **Taxonomy Definition**
    - [x] Create a machine-readable taxonomy file (e.g., `taxonomy.json` or `.yaml`) reflecting the "Domain > Subdomain > Category" structure.
    - [x] Implement `TaxonomyLoader` class to parse and validate the taxonomy structure.
- [x] **Output Schema**
    - [x] Define Pydantic models for the target output:
        - `Hierarchy` (Domain, Category, etc.)
        - `Theme` (Label, Rationale, Hierarchy)
        - `Entity` (Person, Place)
        - `TaggedInscription` (Root object)

## Phase 4: LLM Integration (The Tagger)
- [x] **LLM Client**
    - [x] Set up abstract interface for LLM providers.
    - [x] Implement concrete client (e.g., for OpenAI, Gemini, or local models).
    - [x] Implement rate limiting and retry logic.
- [x] **Prompt Engineering**
    - [x] Design system prompt with role definition.
    - [x] Create dynamic prompt builder that injects:
        - Inscription Text & Metadata.
        - Relevant Taxonomy context.
        - JSON Output constraints (One-shot/Few-shot examples).
- [x] **Parsing & Repair**
    - [x] Implement JSON parser for LLM responses.
    - [x] Add "Retry on Schema Error" logic (if the LLM produces invalid JSON).

## Phase 5: Pipeline Orchestration
- [x] **Main Pipeline Script**
    - [x] Create `main.py` or `cli.py`.
    - [x] Implement batch processing (process entire folder).
    - [x] Implement caching (don't re-process already tagged IDs).
    - [x] Add logging (progress bars, error logs).

## Phase 6: Documentation & Deployment
- [x] **Developer Guide**
    - [x] Update `README.md` with usage instructions.
- [x] **Demo / Visualization**
    - [x] Create a comprehensive web dashboard (Search, Explore, Indices) to visualize the corpus.