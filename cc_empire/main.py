import os
import sys
import asyncio
from dotenv import load_dotenv

# Load secrets and set up paths
load_dotenv()
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

async def boot_sequence():
    print("--- CC_EMPIRE INITIALIZING ---")
    from core.protocols.admin_executive import LyraExecutive
    
    lyra = LyraExecutive()
    print("CEO Lyra Online. Auditing fleet...")
    
    # Simple test of the logic
    try:
        report = await lyra.audit_fleet()
        print(f"Fleet Status: {len(report)} models active.")
    except Exception as e:
        print(f"Boot Error: {e}")

if __name__ == "__main__":
    asyncio.run(boot_sequence())
