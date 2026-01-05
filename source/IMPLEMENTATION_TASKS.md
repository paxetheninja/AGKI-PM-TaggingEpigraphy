# Implementation Task List: AGKI-PM-TaggingEpigraphy

This document outlines the technical tasks required to implement the automated tagging pipeline for Greek epigraphic inscriptions using LLMs.

## Phase 1: Environment & Project Structure
- [ ] **Initialize Python Project**
    - [ ] Create `requirements.txt` / `pyproject.toml`.
    - [ ] Set up virtual environment.
    - [ ] Configure linting/formatting (Ruff/Black).
- [ ] **Directory Setup**
    - [ ] Ensure `data/input`, `data/output`, `data/taxonomy` directories exist.
    - [ ] Create `source/config.py` for project-wide settings (paths, API keys).

## Phase 2: Data Ingestion & Preprocessing
- [ ] **Data Loader Module**
    - [ ] Implement function to read raw PHI-JSON files.
    - [ ] Create Pydantic models for `InputInscription` to validate incoming data.
- [ ] **Preprocessing Module**
    - [ ] Implement text normalization (handling polytonic Greek, brackets).
    - [ ] Implement metadata cleaning (date standardization, region formatting).
    - [ ] Unit tests for normalization logic.

## Phase 3: Taxonomy & Schema Management
- [ ] **Taxonomy Definition**
    - [ ] Create a machine-readable taxonomy file (e.g., `taxonomy.json` or `.yaml`) reflecting the "Domain > Subdomain > Category" structure.
    - [ ] Implement `TaxonomyLoader` class to parse and validate the taxonomy structure.
- [ ] **Output Schema**
    - [ ] Define Pydantic models for the target output:
        - `Hierarchy` (Domain, Category, etc.)
        - `Theme` (Label, Rationale, Hierarchy)
        - `Entity` (Person, Place)
        - `TaggedInscription` (Root object)

## Phase 4: LLM Integration (The Tagger)
- [ ] **LLM Client**
    - [ ] Set up abstract interface for LLM providers.
    - [ ] Implement concrete client (e.g., for OpenAI, Gemini, or local models).
    - [ ] Implement rate limiting and retry logic.
- [ ] **Prompt Engineering**
    - [ ] Design system prompt with role definition.
    - [ ] Create dynamic prompt builder that injects:
        - Inscription Text & Metadata.
        - Relevant Taxonomy context.
        - JSON Output constraints (One-shot/Few-shot examples).
- [ ] **Parsing & Repair**
    - [ ] Implement JSON parser for LLM responses.
    - [ ] Add "Retry on Schema Error" logic (if the LLM produces invalid JSON).

## Phase 5: Pipeline Orchestration
- [ ] **Main Pipeline Script**
    - [ ] Create `main.py` or `cli.py`.
    - [ ] Implement batch processing (process entire folder).
    - [ ] Implement caching (don't re-process already tagged IDs).
    - [ ] Add logging (progress bars, error logs).

## Phase 6: Validation & Quality Assurance
- [ ] **Structural Validation**
    - [ ] Ensure every output file matches the defined JSON schema.
- [ ] **Semantic Validation (Manual/Gold Standard)**
    - [ ] Create a script to generate a comparison report (CSV/HTML) between LLM output and Human Ground Truth (if available).

## Phase 7: Documentation & Deployment
- [ ] **Developer Guide**
    - [ ] Update `README.md` with usage instructions.
- [ ] **Demo / Visualization (Optional)**
    - [ ] Create a simple script to generate a report summarizing the distribution of tags.
