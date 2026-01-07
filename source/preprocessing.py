import re
import unicodedata
from .data_loader import InputInscription

def normalize_greek_text(text: str) -> str:
    """
    Normalizes Greek text for processing.
    """
    if not text:
        return ""
    
    # Try to fix mojibake (UTF-8 bytes interpreted as Latin-1)
    try:
        # Common pattern: Î¸ (theta) is \xce\xb8 in UTF-8. 
        # If we find many such patterns, it's likely mojibake.
        if "Î" in text or "Ï" in text:
            fixed_text = text.encode('latin1').decode('utf-8')
            text = fixed_text
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

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
    
    # Clean text
    inscription.text = normalize_greek_text(inscription.text)
    
    return inscription
