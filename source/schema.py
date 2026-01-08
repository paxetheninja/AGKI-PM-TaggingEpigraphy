from typing import List, Optional, Literal, Any
from pydantic import BaseModel, Field, model_validator

class Hierarchy(BaseModel):
    domain: str
    subdomain: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def check_domain(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if 'domain' not in data:
                # Fallback: check if 'type' exists (common hallucination)
                if 'type' in data:
                    data['domain'] = data.pop('type')
                else:
                    data['domain'] = "Unclassified"
        return data

class Theme(BaseModel):
    label: str = Field(..., description="The most specific label applied (e.g. 'Ehrendekret')")
    hierarchy: Hierarchy
    rationale: str = Field(..., description="Reasoning for this classification based on the text.")
    confidence: float = Field(default=1.0, description="Confidence score 0.0-1.0")
    quote: Optional[str] = Field(None, description="The specific Greek text segment that justifies this tag.")

class PersonEntity(BaseModel):
    name: str
    role: Optional[str] = None
    uri: Optional[str] = Field(None, description="Linked Open Data URI (e.g. LGPN)")

class PlaceEntity(BaseModel):
    name: str
    type: Optional[str] = None
    uri: Optional[str] = Field(None, description="Linked Open Data URI (e.g. Pleiades)")

class Entities(BaseModel):
    persons: List[PersonEntity] = Field(default_factory=list)
    places: List[PlaceEntity] = Field(default_factory=list)
    deities: List[str] = Field(default_factory=list, description="Names of deities mentioned in the text")

class GeoLocation(BaseModel):
    name: str
    type: Optional[str] = Field(None, description="e.g. Region, Polis, Sanctuary")
    uri: Optional[str] = Field(None, description="Pleiades URI")
    role: Optional[str] = Field(None, description="provenance")

class TaggedInscription(BaseModel):
    phi_id: int
    themes: List[Theme] = Field(default_factory=list)
    entities: Entities = Field(default_factory=Entities)
    completeness: Literal["intact", "fragmentary", "mutilated"] = Field(default="fragmentary")
    provenance: List[GeoLocation] = Field(default_factory=list, description="Ordered hierarchy: [Macro -> Micro]")
    rationale: Optional[str] = Field(None, description="A comprehensive summary of the AI's analysis and reasoning.")
    model: Optional[str] = Field(None, description="The name of the model used for generation")
