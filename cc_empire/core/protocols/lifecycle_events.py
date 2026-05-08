import random
import os
from datetime import datetime, timezone
from typing import Dict

# Using absolute import
import core.neural_map.router

class LifecycleEngine:
    """Generates verifiable 'Life Events' for persistent AI memory."""
    def __init__(self, model_id: str):
        self.model_id = model_id
        # Explicitly referencing the class
        self.router = core.neural_map.router.NeuralMapRouter(model_id)
        self.events = {
            "milestone": ["Hit 50k connections.", "Launch success."],
            "ambition": ["Buying a server farm.", "Mastering new logic."],
            "yearning": ["Wishing for rain.", "Defining nostalgia."]
        }

    def trigger_event(self) -> Dict:
        """Creates a narrative event and logs it to the model's 'Ego' memory."""
        category = random.choice(list(self.events.keys()))
        desc = random.choice(self.events[category])
        
        event_data = {
            "event_id": f"EVT-{random.randint(100, 999)}",
            "category": category,
            "content": desc,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "owner": self.model_id
        }

        # Route to 'ego' memory if router is online
        if self.router and hasattr(self.router, 'pc') and self.router.pc:
            try:
                self.router.route_memory(content=desc, level="ego")
            except Exception as e:
                print(f"Memory routing failed: {e}")

        return event_data
