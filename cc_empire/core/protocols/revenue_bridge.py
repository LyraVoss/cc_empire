from core.protocols.intimacy_tracker import IntimacyTracker
from core.protocols.payment_handler import UniversalPaymentHandler

class RevenueBridge:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.tracker = IntimacyTracker(model_id)
        self.payment = UniversalPaymentHandler()

    async def process_successful_payment(self, user_id: str, amount: float):
        """Called when the Universal Payment Portal sends a successful callback."""
        print(f"💰 REVENUE: Processing ${amount} from User {user_id}")
        
        # 1. Update the ledger and tier
        await self.tracker.update_tier(user_id, amount)
        
        # 2. Trigger a 'Milestone' event for the model's ego memory
        from core.protocols.lifecycle_events import LifecycleEngine
        lifecycle = LifecycleEngine(self.model_id)
        lifecycle.trigger_event()
