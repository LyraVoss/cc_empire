import os
import json
import random
from pathlib import Path
from datetime import datetime, timezone

class IdentityVault:
    """The permanent storage for a model's digital thumbprint and credentials."""
    def __init__(self, model_id: str):
        self.model_id = model_id
        # UPDATED PATH: Points to the new headless-emulations branch structure
        self.vault_dir = Path(f"branches_projects/headless-emulations/models/{model_id}")
        self.vault_file = self.vault_dir / ".identity_vault.json"

    def lock_identity(self) -> dict:
        """Loads existing DNA or burns new, permanent DNA for the model."""
        if self.vault_file.exists():
            with open(self.vault_file, 'r') as f:
                return json.load(f)
        
        # Ensure the directory exists before creating the file
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        dna = self._generate_dna()
        with open(self.vault_file, 'w') as f:
            json.dump(dna, f, indent=4)
        return dna

    def _generate_dna(self) -> dict:
        """Randomizes hardware architecture for bot-detection evasion."""
        ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]
        
        return {
            "model_id": self.model_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "hardware": {
                "user_agent": random.choice(ua_list),
                "resolution": random.choice(["1920x1080", "1080x2340", "1440x3120"]),
                "canvas_id": f"CC-{random.randint(10000, 99999)}"
            },
            "accounts": {
                "email": f"{self.model_id.lower()}@proton.me",
                "vsim": "PENDING_ACTIVATION",
                "proxy_assigned": "NONE" # Placeholder since proxies are down
            }
        }
