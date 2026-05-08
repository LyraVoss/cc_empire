import os
from datetime import datetime, timezone
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorClient

# Using absolute import from the root of the project
import core.neural_map.router

class LyraExecutive:
    def __init__(self):
        # Database Connection
        self.client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
        self.db = self.client.get_database("CyberChest_Hive")
        
        # Identity & Memory - Referencing the class through the module
        self.admin_id = "LYRA_MODEL_0"
        self.router = core.neural_map.router.NeuralMapRouter(self.admin_id)
        
        # Delayed import to avoid circular dependency
        from core.protocols.nervous_system import NervousSystem
        self.nervous_system = NervousSystem(self.admin_id)
        
    async def audit_fleet(self) -> List[Dict]:
        """Lyra scans the 'model_profiles' collection for profitability."""
        cursor = self.db.model_profiles.find({"status": "Active"})
        active_models = await cursor.to_list(length=100)
        
        health_report = []
        for model in active_models:
            revenue = model.get('performance_metrics', {}).get('total_revenue', 0)
            costs = model.get('performance_metrics', {}).get('api_costs', 0)
            
            margin = (revenue - costs) / revenue if revenue > 0 else 0
            status = "HEALTHY" if margin > 0.3 else "UNDERPERFORMING"
            
            health_report.append({
                "model_name": model.get('name', 'Unknown'),
                "margin": f"{margin:.2%}",
                "status": status
            })
            
        return health_report

    async def initiate_reproduction(self, persona_config: Dict):
        """Lyra spawns a new worker if the hive is healthy."""
        report = await self.audit_fleet()
        if any(r['status'] == "UNDERPERFORMING" for r in report):
            return "Reproduction paused: Existing fleet requires optimization."

        if not persona_config.get('proxy') and not os.getenv("STICKY_ENDPOINT"):
            return "Abort: No proxy credentials available."

        await self.db.audit_logs.insert_one({
            "actor_id": self.admin_id,
            "action": f"SPAWNED_{persona_config.get('name', 'Worker')}",
            "timestamp": datetime.now(timezone.utc)
        })
        
        return f"Successfully deployed {persona_config.get('name')}."

    def self_diagnostic(self):
        """Checks connection to the Neural Map."""
        # Type check to satisfy Pylance
        if self.router and hasattr(self.router, 'pc'):
            return "Memory Online" if self.router.pc else "Memory Offline"
        return "Router Not Initialized"
