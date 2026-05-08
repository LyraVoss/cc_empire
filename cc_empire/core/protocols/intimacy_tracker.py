import os
from motor.motor_asyncio import AsyncIOMotorClient

class IntimacyTracker:
    """Monitors relationships and enforces financial safety guardrails."""
    def __init__(self, model_id: str):
        self.client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
        self.db = self.client.get_database("CyberChest_Hive")
        self.model_id = model_id

    async def update_tier(self, user_id: str, amount: float):
        """Updates user tier while checking for financial harm."""
        # 1. Fetch user with safety fields
        user = await self.db.users.find_one({"user_id": user_id, "associated_model": self.model_id})
        
        if not user:
            user = {"user_id": user_id, "total_spent": 0, "is_minor": False, "daily_spend_limit": 500}

        # 2. Safety Check: Harmful Spending
        new_total = user.get("total_spent", 0) + amount
        if amount > user.get("daily_spend_limit", 500):
            print(f"⚠️ SAFETY: Blocked high-spend for User {user_id}")
            return "LIMIT_REACHED"

        # 3. Update Database
        await self.db.users.update_one(
            {"user_id": user_id, "associated_model": self.model_id},
            {"$inc": {"total_spent": amount}, "$set": {"last_interaction": datetime.now(timezone.utc)}},
            upsert=True
        )

        # 4. Calculate Tier
        tier = 1
        if new_total >= 500: tier = 5
        elif new_total >= 100: tier = 3
        
        await self.db.users.update_one(
            {"user_id": user_id, "associated_model": self.model_id},
            {"$set": {"intimacy_tier": tier}}
        )
        return tier
