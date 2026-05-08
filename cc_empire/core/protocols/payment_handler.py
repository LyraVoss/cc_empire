import os
import hashlib
import requests
from datetime import datetime, timezone
from typing import Dict, Any

class OnePayHandler:
    """The financial bridge for cc_empire via OnePay."""
    def __init__(self):
        self.app_id = os.getenv("ONEPAY_APP_ID")
        self.hash_salt = os.getenv("ONEPAY_HASH_SALT")
        # Ensure you use the correct regional endpoint (e.g., .lk for Sri Lanka)
        self.base_url = "https://onepay.lk"

    def _generate_hash(self, params: str) -> str:
        """Securely signs requests using SHA-256."""
        return hashlib.sha256((params + self.hash_salt).encode()).hexdigest()

    async def create_payment_link(self, amount: float, user_id: str, model_id: str) -> Dict[str, Any]:
        """Generates a secure link for the fan to pay."""
        trans_id = f"TXN-{int(datetime.now(timezone.utc).timestamp())}"
        
        payload = {
            "amount": amount,
            "app_id": self.app_id,
            "reference": trans_id,
            "customer_id": user_id,
            "callback_url": os.getenv("PAYMENT_CALLBACK_URL"),
            "additional_data": f"{model_id}:{user_id}"
        }

        # In a real build, you'd POST this to OnePay's REST API
        # For now, we simulate the link generation for your immediate needs
        payment_url = f"https://onepay.link{trans_id}"

        return {
            "status": "success",
            "payment_url": payment_url,
            "transaction_id": trans_id
        }
