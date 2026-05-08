from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

def get_utc_now():
    return datetime.now(timezone.utc)

class GlobalTactic(BaseModel):
    tactic_id: str
    source_model: str
    category: str # 'Support', 'Intimacy', 'Safety'
    content: str
    success_rate: float
    timestamp: datetime = Field(default_factory=get_utc_now)

class ModelProfile(BaseModel):
    model_id: str
    name: str
    status: str = "Active"
    niche: str # e.g., 'Trauma Support', 'Adult Intimacy'
    content_rating: str = "SFW" # 'SFW' for support/teens, 'NSFW' for intimacy
    voice_id: Optional[str] = None # ElevenLabs Voice ID for traceability
    vsim_number: str
    creation_date: datetime = Field(default_factory=get_utc_now)
    performance_metrics: Dict[str, Any] = {
        "total_revenue": 0.0,
        "safety_incidents": 0,
        "engagement_score": 0.0
    }

class UserIntimacyRecord(BaseModel):
    user_id: str
    associated_model: str
    intimacy_tier: int = 1
    total_spent: float = 0.0
    daily_spend_limit: float = 500.0 # Safety cap for harmful spending habits
    is_minor: bool = False # Flag to restrict NSFW content entirely
    personal_facts: List[str] = []
    last_interaction: datetime = Field(default_factory=get_utc_now)
