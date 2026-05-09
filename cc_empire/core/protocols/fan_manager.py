import os
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from core.config import settings

class FanManager:
    """
    Manages the lifecycle and safety state of Fans/Users.
    Persists age, warnings, personality traits, and financial status.
    """
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.database_url)
        self.db = self.client.get_database("CyberChest_Hive")
        self.collection = self.db.fan_profiles

    async def get_or_create_profile(self, user_id: str, model_id: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Retrieves user profile or initializes a new one with 'thumbprint' info."""
        profile = await self.collection.find_one({"user_id": user_id, "associated_model": model_id})
        
        if not profile:
            profile = {
                "user_id": user_id,
                "associated_model": model_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "age": 0, # Requires verification
                "nsfw_warnings": 0,
                "finance_soft_ban": False,
                "tier": "free",
                "total_spent": 0.0,
                "daily_spend_limit": 500.0,
                "personality_notes": "Seeking connection.",
                "device_fingerprint": metadata.get("fingerprint", "Unknown") if metadata else "Unknown",
                "is_blocked": False
            }
            await self.collection.insert_one(profile)
            
        # Inject relationship depth for NervousSystem consumption
        profile["relationship_depth"] = self.determine_relationship_depth(profile)
        return profile

    async def process_financial_transaction(self, user_id: str, model_id: str, amount: float) -> int:
        """Updates intimacy tier and checks for spend limits (formerly IntimacyTracker)."""
        profile = await self.get_or_create_profile(user_id, model_id)
        
        if amount > profile.get("daily_spend_limit", 500.0):
            await self.log_safety_incident(user_id, "HIGH_SPEND_BLOCKED", f"Attempted ${amount}")
            return profile.get("tier", 1)

        new_total = profile.get("total_spent", 0.0) + amount
        new_tier = 1
        if new_total >= 500: new_tier = 5
        elif new_total >= 100: new_tier = 3

        await self.collection.update_one(
            {"user_id": user_id, "associated_model": model_id},
            {"$inc": {"total_spent": amount}, "$set": {"tier": new_tier, "last_interaction": datetime.now(timezone.utc).isoformat()}}
        )
        return new_tier

    async def update_profile(self, user_id: str, updates: Dict[str, Any]):
        """Persists changes to warnings, tiers, or safety status."""
        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": updates}
        )

    async def log_safety_incident(self, user_id: str, incident_type: str, detail: str):
        """Records crisis or financial harm events for future personality tailoring."""
        await self.db.safety_logs.insert_one({
            "user_id": user_id,
            "type": incident_type,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def determine_relationship_depth(self, profile: Dict) -> str:
        """
        Connection-First Logic:
        Analyzes the user's history to suggest a support-style for the Nervous System.
        """
        if profile.get("finance_soft_ban"):
            return "Purely emotional support. Avoid any talk of gifts or upgrades."
        if profile.get("age", 0) < 18:
            return "Strictly platonic, wholesome, and protective."
        return "Intimate, supportive, and deeply connected."