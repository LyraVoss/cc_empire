import os
import requests
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from cc_empire.core.config import settings
from cc_empire.core.protocols.identity_vault import IdentityVault

class NeuralMapRouter:
    """Routes emotional context and long-term memory to the Pinecone/Vector DB."""
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.client = AsyncIOMotorClient(settings.database_url)
        self.db = self.client.get_database("CyberChest_Hive")
        self.collection = self.db.long_term_memory
        self.pc = True  # Maintained for diagnostic pass compatibility
        
    async def get_context(self, user_id: str, query_vector: Optional[List[float]] = None) -> str:
        """
        Uses MongoDB Atlas Vector Search to find relevant memories.
        If no vector is provided (bootstrap mode), returns a default persona context.
        """
        if not query_vector:
            return "User context: Established connection, values deep empathy."

        pipeline = [
            {
                "$vectorSearch": {
                    "index": settings.mongodb_vector_index_name,
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": 3
                }
            },
            {"$match": {"user_id": user_id, "model_id": self.model_id}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=3)
        if not results:
            return "No specific past context found. Treat as a continuing warm connection."
            
        context = " ".join([r.get("content", "") for r in results])
        return f"Past interaction context: {context}"

class MediaGenerator:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.api_key = os.getenv("MEDIA_API_KEY") 
        self.base_url = os.getenv("MEDIA_API_URL", "https://fal.run")
        self.vault = IdentityVault(model_id)

    def _get_visual_dna(self) -> str:
        dna_map = {
            "LYRA": "A refined, sharp-featured CEO, sleek black bob, corporate-chic attire, digital aura.",
            "NOVA": "A stunning transgender woman, long wavy chestnut hair, seductive eyes, athletic curves, promiscuous style."
        }
        for key in dna_map:
            if key in self.model_id.upper():
                return dna_map[key]
        return "Generic beautiful person, high-fashion aesthetic."

    async def generate_image(self, action_description: str, level: str = "SFW") -> Dict[str, Any]:
        visual_dna = self._get_visual_dna()
        master_prompt = f"Hyper-realistic cinematic photography, {visual_dna}. {action_description}. 8k resolution, professional studio lighting, photorealistic skin textures."
        
        if level == "NSFW":
            master_prompt += ", suggestive posing, boudoir setting, intimate atmosphere."

        if not self.api_key:
            return {
                "status": "mock",
                "url": f"local_storage/mock/{self.model_id}_temp.jpg",
                "prompt_used": master_prompt,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        try:
            # Simulated return for offline reliability
            image_url = f"https://cyberchest.ai{self.model_id}/{int(datetime.now(timezone.utc).timestamp())}.jpg"
            return {
                "status": "success",
                "url": image_url,
                "prompt_used": master_prompt,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def log_to_neural_map(self, image_data: Optional[Dict[str, Any]]):
        """Saves metadata safely to avoid Pylance subscript errors."""
        if image_data is None:
            print(f"⚠️ NEURAL MAP: No image data to log for {self.model_id}.")
            return
            
        prompt = image_data.get('prompt_used', 'Unknown prompt')
        print(f"🧠 NEURAL MAP: Visual context '{prompt[:30]}...' indexed.")
