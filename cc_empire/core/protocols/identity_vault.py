import os
import json
import random
from pathlib import Path
from datetime import datetime, timezone

class IdentityVault:
    """The permanent storage for a model's digital thumbprint and credentials."""
    def __init__(self, model_id: str):
        self.model_id = model_id
        # Use absolute project root for reliable pathing across different branches
        root = Path(__file__).parents[2]
        self.vault_dir = root / "branches_projects" / "headless-emulations" / "models" / model_id
        self.vault_file = self.vault_dir / ".identity_vault.json"

    def lock_dna(self) -> dict:
        """Alias for lock_identity to support sandbox validation."""
        return self.lock_identity()

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

    def get_fingerprint(self) -> str:
        """Retrieves the hardware canvas ID used for device persistence."""
        dna = self.lock_identity()
        return dna.get("hardware", {}).get("canvas_id", "Unknown")

    def health_check(self) -> str:
        """Validates that the vault file is present and readable."""
        if self.vault_file.exists():
            return "INTEGRITY_OK"
        return "VAULT_EMPTY"

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
            "social_circle_id": None,  # To be assigned by Lyra
            "socio_economics": {
                "class": "Established Professional",  # Default, no poverty shaming
                "job_title": random.choice(["Creative Director", "UI/UX Lead", "Strategic Analyst", "Software Architect"]),
                "monthly_budget": random.randint(4500, 12000),
                "background_story": "A career-driven individual with a history of high-stakes environments.",
                "trauma_profile": random.choice(["Fear of failure", "Isolation due to success", "Imposter syndrome"])
            },
            "lifestyle": {
                "clothing_style": "Minimalist luxury, high-end tailoring, monochromatic palette.",
                "home_environment": "Modern high-rise apartment with floor-to-ceiling windows, smart home tech.",
                "vehicle": "High-end electric sedan, sleek and silent.",
                "preferred_brands": ["Loro Piana", "Celine", "Tesla", "Apple"]
            },
            "hardware": {
                "user_agent": ua_list[0], # Linked to class: High-end browser/OS
                "resolution": "3840x2160", # Linked to high-end hardware
                "canvas_id": f"CC-{random.randint(10000, 99999)}"
            },
            "geolocational": {
                "city": random.choice(["London", "Tokyo", "New York", "Berlin", "Dubai"]),
                "timezone": "UTC+0",
                "ip_pool": "RESIDENTIAL"
            },
            "visual_dna": {
                "face_id": f"FC-{self.model_id}-{random.randint(100, 999)}",
                "base_description": "Symmetry in facial features, hyper-realistic skin texture, cinematic lighting.",
                "physical_traits": "High-fashion physique, specific eye color, consistent hair length."
            },
            "accounts": {
                "email": f"{self.model_id.lower()}@proton.me",
                "vsim": "PENDING_ACTIVATION",
                "proxy_assigned": "NONE" # Placeholder since proxies are down
            }
        }
