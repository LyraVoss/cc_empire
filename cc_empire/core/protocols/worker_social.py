import os
import time
import random
import asyncio
from datetime import datetime, timezone
from typing import Dict

# Integration: Using the updated absolute paths for our new structure
from core.protocols.identity_vault import IdentityVault
from core.protocols.nervous_system import NervousSystem

class WorkerSocialProtocol:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.vault = IdentityVault(model_id)
        
        # Updated to match our new lock_identity method
        self.dna = self.vault.lock_identity()
        self.ns = NervousSystem(model_id)
        
        # Pulling hardware fingerprint for browser/app headers
        self.hw = self.dna.get("hardware", {})
        self.headers = {
            "User-Agent": self.hw.get("user_agent", "Mozilla/5.0"),
            "Accept-Language": "en-US,en;q=0.9",
            "X-Device-Resolution": self.hw.get("resolution", "1920x1080")
        }

    def simulate_human_delay(self, action_type: str = "default"):
        """Adds randomized jitter to prevent 'superhuman' speed detection."""
        delays = {
            "post": (60, 300),      # 1-5 mins prep time
            "reply": (15, 120),     # 15s to 2m typing simulation
            "scroll": (2, 8),       # Simulating reading
            "default": (5, 20)
        }
        low, high = delays.get(action_type, delays["default"])
        sleep_time = random.uniform(low, high)
        print(f"[{self.model_id}] ⏳ Human-simulated delay: {sleep_time:.2f}s")
        # Note: In an async loop, we'd ideally use await asyncio.sleep
        time.sleep(sleep_time)

    async def execute_social_loop(self, platform: str, task_type: str, content_data: Dict):
        """The main engine for daily worker social interactions."""
        
        # 1. Proxy Safety Gate
        # Since RoyalIP is down, we check if a proxy exists in DNA or .env
        proxy = self.dna.get("accounts", {}).get("proxy_assigned")
        if not proxy or proxy == "NONE":
            if not os.getenv("STICKY_ENDPOINT"):
                return {"status": "halt", "message": "CRITICAL: No proxy credentials available for this worker."}

        # 2. Content Sanitization (using our updated NervousSystem method)
        raw_text = content_data.get("text", "")
        clean_content = self.ns.sanitize(raw_text)
        
        # 3. Execution
        self.simulate_human_delay("scroll" if task_type == "engage" else "post")

        if platform == "twitter":
            return await self._post_to_x(clean_content)
        elif platform == "telegram":
            return await self._message_telegram(clean_content)
        
        return {"status": "error", "message": "Unsupported platform"}

    async def _post_to_x(self, text: str):
        """Logic for posting to X with device persistence."""
        print(f"[{self.model_id}] 🐦 Posting to X using fingerprint: {self.hw.get('canvas_id')}")
        # Logic for Tweepy/Playwright goes here once proxies are restored
        return {"status": "success", "platform": "x", "content": text[:20] + "..."}

    async def _message_telegram(self, text: str):
        """Logic for Telegram interaction."""
        print(f"[{self.model_id}] 💬 Sending Telegram: {text[:20]}...")
        return {"status": "success", "platform": "telegram"}
