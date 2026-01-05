# AGKI-PM-TaggingEpigraphy
Tagging Greek Epigraphic Inscriptions with the use of Large Language Models

## Project Overview
This project implements an automated pipeline to semantically tag Ancient Greek inscriptions using Large Language Models (LLMs). It processes JSON data from the PHI corpus, assigns hierarchical thematic tags based on a custom taxonomy, and extracts entities (persons, places).

## Setup & Installation

1.  **Clone the repository**
    ```bash
    git clone <repository_url>
    cd AGKI-PM-TaggingEpigraphy
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**
    *   Copy `.env.example` to `.env`.
    *   Add your API Key (e.g., `OPENAI_API_KEY`).
    ```bash
    cp .env.example .env
    ```

## Usage

1.  **Prepare Input Data**
    *   Place your PHI-JSON files in `data/input/`.

2.  **Run the Tagging Pipeline**
    ```bash
    python -m source.main
    ```
    *   This will process all files in `data/input`, query the LLM, and save the results to `data/output`.

3.  **Check Results**
    *   Output files are saved as JSON in `data/output/`.

## Project Structure
*   `source/`: Python source code.
    *   `main.py`: Pipeline entry point.
    *   `tagger.py`: Core tagging logic and prompt construction.
    *   `llm_client.py`: LLM API interaction.
    *   `schema.py`: Pydantic models for data validation.
    *   `data_loader.py` & `preprocessing.py`: Data handling.
*   `data/`: Data storage.
    *   `taxonomy/`: Contains `taxonomy.json`.
    *   `input/`: Raw JSON inscriptions.
    *   `output/`: Tagged JSON results.

## Documentation
See the `docs/` folder for the project website and `vault/` for detailed internal documentation on the taxonomy and design.