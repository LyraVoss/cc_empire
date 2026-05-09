import asyncio
import json
import httpx
from datetime import datetime, timezone
from cc_empire.core.config import settings

# Fix: Absolute import for the new structure
from cc_empire.core.protocols.admin_executive import LyraExecutive

class HiveHeartbeat:
    def __init__(self):
        self.executive = LyraExecutive()
        self.ws_url = getattr(settings, "ws_url", None)
        self.host_url = getattr(settings, "host_url", None) # Public Render URL
        self.is_profitable = False 
        self.heartbeat_interval = 3600 # 1 hour
        self.ping_interval = 600       # 10 minutes

    async def run_audit_cycle(self):
        """Lyra's deep-dive into fleet health."""
        while True:
            # Fix: Use timezone-aware UTC
            now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{now}] 🔍 EXECUTIVE AUDIT STARTING...")
            
            try:
                report = await self.executive.audit_fleet()
                
                # Logic to update profitability flag
                margins = [float(r['status'] == "HEALTHY") for r in report]
                if margins and (sum(margins) / len(margins)) > 0.5: # 50% healthy fleet
                    self.is_profitable = True
                    print("📈 PROFITABILITY REACHED. Empire is stable.")
                else:
                    self.is_profitable = False
                    print("⚠️ FLEET WARNING: Optimization required.")
            except Exception as e:
                print(f"Audit Error: {e}")

            await asyncio.sleep(self.heartbeat_interval)

    async def run_persistence_ping(self):
        """Prevents server spin-down via WebSocket."""
        while True:
            # Ping public URL to keep Render instance awake
            if self.host_url:
                now = datetime.now(timezone.utc).isoformat()
                print(f"[{now}] ⚡ PERSISTENCE PING: Keeping instance alive.")
                try:
                    async with httpx.AsyncClient() as client:
                        # Ping our own health endpoint
                        response = await client.get(f"{self.host_url}/health")
                        if response.status_code == 200:
                            print("✅ Ping Successful.")
                        else:
                            print(f"⚠️ Ping returned status: {response.status_code}")
                except Exception as e:
                    print(f"⚠️ PERSISTENCE PING FAILED: {e}")
            
            await asyncio.sleep(self.ping_interval)

    async def start_heartbeat_system(self):
        """Launches Audit and Persistence loops."""
        print("🚀 CYBER CHEST HEARTBEAT SYSTEM INITIALIZED.")
        await asyncio.gather(
            self.run_audit_cycle(),
            self.run_persistence_ping()
        )

if __name__ == "__main__":
    heartbeat = HiveHeartbeat()
    asyncio.run(heartbeat.start_heartbeat_system())
