import json
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel, Field

class ValidationMetrics(BaseModel):
    total_samples: int = 0
    valid_structural: int = 0
    invalid_structural: List[str] = Field(default_factory=list)
    exact_matches: int = 0
    partial_matches: int = 0
    mismatches: int = 0

def validate_structure(prediction_dir: Path):
    """Checks if all JSON files in the directory match the TaggedInscription schema."""
    from .schema import TaggedInscription
    invalid_files = []
    files = list(prediction_dir.glob("*.json"))
    
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as f_in:
                data = json.load(f_in)
                TaggedInscription(**data)
        except Exception as e:
            invalid_files.append(f"{f.name}: {str(e)}")
            
    return len(files), invalid_files

def compare_themes(pred_themes: List[Dict], truth_themes: List[Dict]) -> str:
    """
    Simple comparison logic.
    Returns 'exact', 'partial', or 'mismatch'.
    """
    pred_labels = {t['label'] for t in pred_themes}
    truth_labels = {t['label'] for t in truth_themes}
    
    if pred_labels == truth_labels:
        return 'exact'
    elif not pred_labels.isdisjoint(truth_labels):
        return 'partial'
    else:
        return 'mismatch'

def run_validation(prediction_dir: Path, ground_truth_dir: Path) -> ValidationMetrics:
    metrics = ValidationMetrics()
    
    pred_files = list(prediction_dir.glob("*.json"))
    
    for pred_path in pred_files:
        filename = pred_path.name
        truth_path = ground_truth_dir / filename
        
        if not truth_path.exists():
            continue
            
        metrics.total_samples += 1
        
        pred_data = load_json(pred_path)
        truth_data = load_json(truth_path)
        
        # Compare themes
        result = compare_themes(pred_data.get('themes', []), truth_data.get('themes', []))
        
        if result == 'exact':
            metrics.exact_matches += 1
        elif result == 'partial':
            metrics.partial_matches += 1
        else:
            metrics.mismatches += 1
            
    return metrics

if __name__ == "__main__":
    from .config import OUTPUT_DIR
    
    print(f"Running structural validation on {OUTPUT_DIR}...")
    total, invalid = validate_structure(OUTPUT_DIR)
    
    print(f"\nResults:")
    print(f"Total files checked: {total}")
    print(f"Valid files: {total - len(invalid)}")
    print(f"Invalid files: {len(invalid)}")
    
    if invalid:
        print("\nErrors found in:")
        for err in invalid:
            print(f" - {err}")
