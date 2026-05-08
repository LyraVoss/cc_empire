import os
import asyncio
import websockets
import json
from datetime import datetime, timezone

# Fix: Absolute import for the new structure
from core.protocols.admin_executive import LyraExecutive

class HiveHeartbeat:
    def __init__(self):
        self.executive = LyraExecutive()
        self.ws_url = os.getenv("WS_URL") 
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
            # Only ping if we have a URL and aren't profitable yet (startup mode)
            if self.ws_url and not self.is_profitable:
                now = datetime.now(timezone.utc).isoformat()
                print(f"[{now}] ⚡ PERSISTENCE PING: Keeping Live Memory hot.")
                try:
                    async with websockets.connect(self.ws_url) as websocket:
                        ping_payload = {
                            "type": "heartbeat",
                            "sender": "LYRA_MODEL_0",
                            "timestamp": now,
                            "mode": "startup_persistence"
                        }
                        await websocket.send(json.dumps(ping_payload))
                except Exception as e:
                    print(f"⚠️ WS PING FAILED: {e}. Check your WS_URL in .env.")
            
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
