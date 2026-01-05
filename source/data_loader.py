import json
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

class InputInscription(BaseModel):
    id: int
    text: str
    metadata: Optional[str] = None
    region_main_id: Optional[str] = None
    region_main: Optional[str] = None
    region_sub_id: Optional[str] = None
    region_sub: Optional[str] = None
    date_str: Optional[str] = None
    date_min: Optional[float] = None
    date_max: Optional[float] = None
    date_circa: Optional[bool] = None

def load_inscription(file_path: Path) -> InputInscription:
    """Loads a single inscription from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return InputInscription(**data)

def load_inscriptions(directory: Path, limit: Optional[int] = None) -> List[InputInscription]:
    """
    Loads all JSON inscriptions from a directory.
    
    Args:
        directory: Path to the directory containing JSON files.
        limit: Optional maximum number of files to load (useful for testing).
    """
    inscriptions = []
    files = list(directory.glob("*.json"))
    
    if limit:
        files = files[:limit]
        
    for file_path in files:
        try:
            inscriptions.append(load_inscription(file_path))
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            
    return inscriptions
