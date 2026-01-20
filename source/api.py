"""
AGKI REST API
FastAPI-based REST API for accessing the AGKI epigraphic corpus.

Run with: uvicorn source.api:app --reload --port 8000
"""

import json
import os
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(
    title="AGKI Epigraphy API",
    description="REST API for accessing AI-tagged Ancient Greek inscriptions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage
DATA_DIR = Path(__file__).parent.parent / "data" / "output"
INSCRIPTIONS_CACHE = {}


# Pydantic models for API responses
class Theme(BaseModel):
    label: str
    hierarchy: dict
    rationale: Optional[str] = None
    confidence: Optional[float] = None
    quote: Optional[str] = None
    is_ambiguous: Optional[bool] = False


class Person(BaseModel):
    name: str
    role: Optional[str] = None
    uri: Optional[str] = None
    confidence: Optional[float] = None


class Place(BaseModel):
    name: str
    type: Optional[str] = None
    uri: Optional[str] = None
    confidence: Optional[float] = None


class Deity(BaseModel):
    name: str
    epithet: Optional[str] = None
    uri: Optional[str] = None
    confidence: Optional[float] = None


class Entities(BaseModel):
    persons: List[Person] = []
    places: List[Place] = []
    deities: List[Deity] = []


class Inscription(BaseModel):
    phi_id: int
    themes: List[Theme] = []
    entities: Entities
    completeness: Optional[str] = None
    provenance: Optional[List[dict]] = []
    rationale: Optional[str] = None
    model: Optional[str] = None
    date_str: Optional[str] = None
    date_min: Optional[float] = None
    date_max: Optional[float] = None


class InscriptionSummary(BaseModel):
    phi_id: int
    theme_count: int
    person_count: int
    place_count: int
    deity_count: int
    completeness: Optional[str] = None
    date_str: Optional[str] = None
    region: Optional[str] = None


class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[InscriptionSummary]


class StatsResponse(BaseModel):
    total_inscriptions: int
    total_persons: int
    total_places: int
    total_deities: int
    total_themes: int
    regions: dict
    date_range: dict


def load_all_inscriptions():
    """Load all inscriptions from JSON files into cache."""
    global INSCRIPTIONS_CACHE

    if INSCRIPTIONS_CACHE:
        return INSCRIPTIONS_CACHE

    if not DATA_DIR.exists():
        return {}

    for json_file in DATA_DIR.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                phi_id = data.get('phi_id')
                if phi_id:
                    INSCRIPTIONS_CACHE[phi_id] = data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {json_file}: {e}")

    return INSCRIPTIONS_CACHE


def get_region_from_provenance(provenance: list) -> Optional[str]:
    """Extract region from provenance data."""
    if not provenance:
        return None
    for p in provenance:
        if p.get('type') == 'Region':
            return p.get('name')
    return provenance[0].get('name') if provenance else None


@app.on_event("startup")
async def startup_event():
    """Load data on startup."""
    load_all_inscriptions()
    print(f"Loaded {len(INSCRIPTIONS_CACHE)} inscriptions")


@app.get("/", tags=["Info"])
async def root():
    """API root - returns basic info."""
    return {
        "name": "AGKI Epigraphy API",
        "version": "1.0.0",
        "endpoints": {
            "inscriptions": "/inscriptions",
            "inscription": "/inscriptions/{phi_id}",
            "search": "/search",
            "stats": "/stats",
            "themes": "/themes",
            "entities": "/entities/{type}"
        }
    }


@app.get("/inscriptions", response_model=SearchResponse, tags=["Inscriptions"])
async def list_inscriptions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    region: Optional[str] = Query(None, description="Filter by region"),
    completeness: Optional[str] = Query(None, description="Filter by completeness"),
    date_min: Optional[int] = Query(None, description="Minimum date (negative for BC)"),
    date_max: Optional[int] = Query(None, description="Maximum date (negative for BC)")
):
    """List all inscriptions with pagination and filters."""
    inscriptions = load_all_inscriptions()

    # Apply filters
    filtered = []
    for phi_id, data in inscriptions.items():
        # Region filter
        if region:
            item_region = get_region_from_provenance(data.get('provenance', []))
            if item_region != region:
                continue

        # Completeness filter
        if completeness and data.get('completeness') != completeness:
            continue

        # Date filters
        if date_min is not None:
            item_date = data.get('date_min')
            if item_date is None or item_date < date_min:
                continue

        if date_max is not None:
            item_date = data.get('date_max')
            if item_date is None or item_date > date_max:
                continue

        # Build summary
        entities = data.get('entities', {})
        filtered.append(InscriptionSummary(
            phi_id=phi_id,
            theme_count=len(data.get('themes', [])),
            person_count=len(entities.get('persons', [])),
            place_count=len(entities.get('places', [])),
            deity_count=len(entities.get('deities', [])),
            completeness=data.get('completeness'),
            date_str=data.get('date_str'),
            region=get_region_from_provenance(data.get('provenance', []))
        ))

    # Sort by PHI ID
    filtered.sort(key=lambda x: x.phi_id)

    # Paginate
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    results = filtered[start:end]

    return SearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=results
    )


@app.get("/inscriptions/{phi_id}", tags=["Inscriptions"])
async def get_inscription(phi_id: int):
    """Get a single inscription by PHI ID."""
    inscriptions = load_all_inscriptions()

    if phi_id not in inscriptions:
        raise HTTPException(status_code=404, detail=f"Inscription {phi_id} not found")

    return inscriptions[phi_id]


@app.get("/search", response_model=SearchResponse, tags=["Search"])
async def search_inscriptions(
    q: Optional[str] = Query(None, description="Search query (searches themes and rationale)"),
    theme: Optional[str] = Query(None, description="Filter by theme label"),
    person: Optional[str] = Query(None, description="Filter by person name"),
    place: Optional[str] = Query(None, description="Filter by place name"),
    deity: Optional[str] = Query(None, description="Filter by deity name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Search inscriptions by various criteria."""
    inscriptions = load_all_inscriptions()

    filtered = []
    for phi_id, data in inscriptions.items():
        # Text search
        if q:
            q_lower = q.lower()
            found = False
            # Search in themes
            for t in data.get('themes', []):
                if q_lower in t.get('label', '').lower():
                    found = True
                    break
                if q_lower in (t.get('rationale') or '').lower():
                    found = True
                    break
            # Search in rationale
            if not found and q_lower in (data.get('rationale') or '').lower():
                found = True
            if not found:
                continue

        # Theme filter
        if theme:
            theme_lower = theme.lower()
            if not any(theme_lower in t.get('label', '').lower() for t in data.get('themes', [])):
                continue

        # Entity filters
        entities = data.get('entities', {})

        if person:
            person_lower = person.lower()
            if not any(person_lower in (p.get('name') or '').lower() for p in entities.get('persons', [])):
                continue

        if place:
            place_lower = place.lower()
            if not any(place_lower in (p.get('name') or '').lower() for p in entities.get('places', [])):
                continue

        if deity:
            deity_lower = deity.lower()
            if not any(deity_lower in (d.get('name') or '').lower() for d in entities.get('deities', [])):
                continue

        # Build summary
        filtered.append(InscriptionSummary(
            phi_id=phi_id,
            theme_count=len(data.get('themes', [])),
            person_count=len(entities.get('persons', [])),
            place_count=len(entities.get('places', [])),
            deity_count=len(entities.get('deities', [])),
            completeness=data.get('completeness'),
            date_str=data.get('date_str'),
            region=get_region_from_provenance(data.get('provenance', []))
        ))

    # Sort and paginate
    filtered.sort(key=lambda x: x.phi_id)
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size

    return SearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=filtered[start:end]
    )


@app.get("/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_stats():
    """Get corpus statistics."""
    inscriptions = load_all_inscriptions()

    persons = set()
    places = set()
    deities = set()
    themes = set()
    regions = {}
    min_date = float('inf')
    max_date = float('-inf')

    for data in inscriptions.values():
        # Collect entities
        entities = data.get('entities', {})
        for p in entities.get('persons', []):
            if p.get('name'):
                persons.add(p['name'])
        for p in entities.get('places', []):
            if p.get('name'):
                places.add(p['name'])
        for d in entities.get('deities', []):
            if d.get('name'):
                deities.add(d['name'])

        # Collect themes
        for t in data.get('themes', []):
            if t.get('label'):
                themes.add(t['label'])

        # Count regions
        region = get_region_from_provenance(data.get('provenance', []))
        if region:
            regions[region] = regions.get(region, 0) + 1

        # Date range
        if data.get('date_min') is not None:
            min_date = min(min_date, data['date_min'])
        if data.get('date_max') is not None:
            max_date = max(max_date, data['date_max'])

    return StatsResponse(
        total_inscriptions=len(inscriptions),
        total_persons=len(persons),
        total_places=len(places),
        total_deities=len(deities),
        total_themes=len(themes),
        regions=regions,
        date_range={
            "min": min_date if min_date != float('inf') else None,
            "max": max_date if max_date != float('-inf') else None
        }
    )


@app.get("/themes", tags=["Taxonomy"])
async def get_themes():
    """Get all unique themes with counts."""
    inscriptions = load_all_inscriptions()

    theme_counts = {}
    theme_hierarchies = {}

    for data in inscriptions.values():
        for t in data.get('themes', []):
            label = t.get('label')
            if label:
                theme_counts[label] = theme_counts.get(label, 0) + 1
                if label not in theme_hierarchies:
                    theme_hierarchies[label] = t.get('hierarchy', {})

    # Sort by count descending
    sorted_themes = sorted(theme_counts.items(), key=lambda x: -x[1])

    return {
        "total": len(sorted_themes),
        "themes": [
            {
                "label": label,
                "count": count,
                "hierarchy": theme_hierarchies.get(label, {})
            }
            for label, count in sorted_themes
        ]
    }


@app.get("/entities/{entity_type}", tags=["Entities"])
async def get_entities(
    entity_type: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200)
):
    """Get all unique entities of a given type (persons, places, deities)."""
    if entity_type not in ['persons', 'places', 'deities']:
        raise HTTPException(
            status_code=400,
            detail="entity_type must be one of: persons, places, deities"
        )

    inscriptions = load_all_inscriptions()

    entity_data = {}  # name -> {count, inscriptions, roles/types}

    for phi_id, data in inscriptions.items():
        entities = data.get('entities', {}).get(entity_type, [])
        for e in entities:
            name = e.get('name')
            if not name:
                continue

            if name not in entity_data:
                entity_data[name] = {
                    'name': name,
                    'count': 0,
                    'inscriptions': [],
                    'attributes': set()
                }

            entity_data[name]['count'] += 1
            entity_data[name]['inscriptions'].append(phi_id)

            # Collect roles/types
            if entity_type == 'persons' and e.get('role'):
                entity_data[name]['attributes'].add(e['role'])
            elif entity_type == 'places' and e.get('type'):
                entity_data[name]['attributes'].add(e['type'])
            elif entity_type == 'deities' and e.get('epithet'):
                entity_data[name]['attributes'].add(e['epithet'])

    # Convert to list and sort
    entity_list = sorted(entity_data.values(), key=lambda x: -x['count'])

    # Convert sets to lists for JSON
    for e in entity_list:
        e['attributes'] = list(e['attributes'])

    # Paginate
    total = len(entity_list)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "entity_type": entity_type,
        "total": total,
        "page": page,
        "page_size": page_size,
        "entities": entity_list[start:end]
    }


@app.get("/regions", tags=["Geography"])
async def get_regions():
    """Get all unique regions with inscription counts."""
    inscriptions = load_all_inscriptions()

    regions = {}
    for data in inscriptions.values():
        region = get_region_from_provenance(data.get('provenance', []))
        if region:
            regions[region] = regions.get(region, 0) + 1

    # Sort by count
    sorted_regions = sorted(regions.items(), key=lambda x: -x[1])

    return {
        "total": len(sorted_regions),
        "regions": [
            {"name": name, "count": count}
            for name, count in sorted_regions
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
