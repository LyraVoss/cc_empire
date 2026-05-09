import asyncio
from fastapi import FastAPI
from cc_empire.core.config import settings
from cc_empire.core.protocols.heartbeat import HiveHeartbeat

app = FastAPI(
    title="Cyber Chest Hive",
    version="1.0.0",
    debug=settings.debug
)

# Initialize Heartbeat as a global to keep it in memory
heartbeat = HiveHeartbeat()

@app.on_event("startup")
async def startup_event():
    """
    Triggers the Hive's autonomic functions on startup.
    This ensures the Audit and Persistence loops run in the background
    as soon as the web server is live.
    """
    print("🧠 Hive Mind Initializing Background Protocols...")
    # Using create_task so they run concurrently with the web server
    asyncio.create_task(heartbeat.run_audit_cycle())
    asyncio.create_task(heartbeat.run_persistence_ping())

@app.get("/health")
async def health_check():
    """
    Endpoint for Render's zero-downtime checks and the Heartbeat persistence ping.
    """
    return {
        "status": "online",
        "environment": settings.environment,
        "profitable": heartbeat.is_profitable,
        "vault_integrity": heartbeat.executive.self_diagnostic()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)