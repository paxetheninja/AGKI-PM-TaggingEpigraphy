import re
import unicodedata
from .data_loader import InputInscription

def normalize_greek_text(text: str) -> str:
    """
    Normalizes Greek text for processing.
    - Normalizes unicode (NFC).
    - Removes excessive whitespace.
    - (Optional) Could remove brackets [] indicating restorations if desired for embedding, 
      but for analysis, we might want to keep them or replace them.
    """
    if not text:
        return ""
    
    # Unicode normalization
    text = unicodedata.normalize("NFC", text)
    
    # Replace newlines with spaces
    text = text.replace("\n", " ")
    
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def clean_metadata(inscription: InputInscription) -> InputInscription:
    """
    Cleans and standardizes metadata fields.
    """
    # Example: Ensure date fields are consistent or handle missing values
    # For now, we pass it through, but this is where specific logic would go.
    
    # Clean text
    inscription.text = normalize_greek_text(inscription.text)
    
    return inscription
