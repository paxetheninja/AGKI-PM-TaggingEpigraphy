import json
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel

class ValidationMetrics(BaseModel):
    total_samples: int = 0
    exact_matches: int = 0
    partial_matches: int = 0
    mismatches: int = 0

def load_json(path: Path) -> Dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

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
    # Example usage
    import sys
    # These paths would need to be configured
    PRED_DIR = Path("data/output")
    TRUTH_DIR = Path("data/ground_truth") 
    
    if TRUTH_DIR.exists():
        results = run_validation(PRED_DIR, TRUTH_DIR)
        print("Validation Results:")
        print(results.model_dump_json(indent=2))
    else:
        print(f"Ground truth directory {TRUTH_DIR} not found.")
