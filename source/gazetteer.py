import gzip
import csv
import logging
import unicodedata
from pathlib import Path
from collections import defaultdict
from .config import DATA_DIR

logger = logging.getLogger(__name__)

NAMES_FILE = DATA_DIR / "pleiades_names.csv.gz"
PLACES_FILE = DATA_DIR / "pleiades_places.csv.gz"

def normalize(text):
    """Normalize text by stripping accents and converting to lowercase."""
    if not text: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn').lower().strip()

class PleiadesGazetteer:
    def __init__(self):
        self.name_index = defaultdict(list)
        self.place_metadata = {}
        self.loaded = False
    
    def load(self):
        if self.loaded: return
        
        # Check if files exist
        if not NAMES_FILE.exists() or not PLACES_FILE.exists():
            logger.warning("Pleiades data dumps not found. Offline reconciliation unavailable.")
            return

        logger.info("Loading Pleiades dumps into memory...")
        
        try:
            # Load Places Metadata
            with gzip.open(PLACES_FILE, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Fix PID format (strip /places/)
                    pid = row['id'].replace('/places/', '')
                    
                    self.place_metadata[pid] = {
                        'featureTypes': row.get('featureTypes', '').split(','),
                        'timePeriods': row.get('timePeriods', '').split(','),
                        'bbox': row.get('bbox')
                    }

            # Load Names
            with gzip.open(NAMES_FILE, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Index multiple name fields
                    names_to_index = set()
                    if row.get('nameTransliterated'): names_to_index.add(row['nameTransliterated'])
                    if row.get('title'): names_to_index.add(row['title'])
                    if row.get('nameAttested'): names_to_index.add(row['nameAttested'])
                    
                    # Fix PID format
                    pid = row['pid'].replace('/places/', '').strip('/')
                    
                    entry = {
                        'pid': pid,
                        'precision': row.get('locationPrecision', ''),
                    }
                    
                    for n in names_to_index:
                        if n:
                            norm_n = normalize(n)
                            self.name_index[norm_n].append(entry)
            
            self.loaded = True
            logger.info(f"Gazetteer loaded: {len(self.name_index)} unique names, {len(self.place_metadata)} places.")
            
        except Exception as e:
            logger.error(f"Failed to load Pleiades dumps: {e}")

    def search(self, query):
        if not self.loaded: self.load()
        if not self.loaded: return None # Failed to load
        
        norm_query = normalize(query)
        matches = self.name_index.get(norm_query, [])
        if not matches: return None
        
        # Scoring Algorithm
        scored = []
        for m in matches:
            pid = m['pid']
            meta = self.place_metadata.get(pid, {})
            score = 0
            
            # Precision
            if m['precision'] == 'precise': score += 3
            
            # Feature Types
            ftypes = meta.get('featureTypes', [])
            ftypes_str = ",".join(ftypes)
            if 'settlement' in ftypes_str: score += 2
            if 'deme' in ftypes_str: score += 5 # Boost demes significantly
            if 'city' in ftypes_str: score += 2
            if 'island' in ftypes_str: score += 2
            if 'sanctuary' in ftypes_str: score += 2
            
            # Time Periods (Prefer Classical/Hellenistic/Roman)
            periods = meta.get('timePeriods', [])
            periods_str = ",".join(periods)
            if 'classical' in periods_str: score += 1
            if 'hellenistic' in periods_str: score += 1
            if 'roman' in periods_str: score += 1
            if 'archaic' in periods_str: score += 1
            
            scored.append((score, pid))
        
        # Sort by score desc
        scored.sort(key=lambda x: x[0], reverse=True)
        
        if scored:
            best_pid = scored[0][1]
            return f"https://pleiades.stoa.org/places/{best_pid}"
        
        return None

_gazetteer = None
def get_gazetteer():
    global _gazetteer
    if not _gazetteer:
        _gazetteer = PleiadesGazetteer()
    return _gazetteer
