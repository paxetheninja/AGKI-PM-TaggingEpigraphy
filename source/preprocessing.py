import re
import unicodedata
from .data_loader import InputInscription

def normalize_greek_text(text: str) -> str:
    """
    Normalizes Greek text for processing.
    """
    if not text:
        return ""

    # Unicode normalization
    text = unicodedata.normalize("NFC", text)
    
    # Collapse multiple spaces but KEEP newlines for alignment precision
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()

def clean_metadata(inscription: InputInscription) -> InputInscription:
    """
    Cleans and standardizes metadata fields.
    """
    # Example: Ensure date fields are consistent or handle missing values
    # For now, we pass it through, but this is where specific logic would go.
    
    # Clean regions (remove corpus citations in parentheses)
    if inscription.region_main:
        inscription.region_main = re.sub(r'\s*\(.*?\)', '', inscription.region_main).strip()
    if inscription.region_sub:
        inscription.region_sub = re.sub(r'\s*\(.*?\)', '', inscription.region_sub).strip()
    
    # Clean text
    inscription.text = normalize_greek_text(inscription.text)
    
    return inscription
