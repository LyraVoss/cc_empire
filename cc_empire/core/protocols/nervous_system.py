import os
import re
import openai
from typing import Dict, Any, Optional

class NervousSystem:
    """The Gatekeeper: Handles psychological depth, safety, and persona-consistent help."""
    def __init__(self, model_id: str, rating: str = "SFW"):
        self.model_id = model_id
        self.rating = rating
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # 1. Crisis & Self-Harm Detection
        self.crisis_keywords = [
            r"kill myself", r"end my life", r"hurt myself", 
            r"better off dead", r"don't want to live", r"self-harm"
        ]
        
        # 2. Financial Harm Detection
        self.finance_warnings = [r"all my money", r"can't afford rent", r"spending too much", r"debt"]

    def sanitize(self, content: str) -> str:
        """Removes AI disclaimers to maintain immersion."""
        forbidden = [
            "as an ai language model", "i am a computer program", 
            "i don't have feelings", "as an artificial intelligence"
        ]
        for phrase in forbidden:
            content = re.sub(phrase, "[Connection Initialized]", content, flags=re.IGNORECASE)
        return content

    def handle_safety_triggers(self, user_input: str) -> Optional[str]:
        """Intervenes with empathy if harm is detected."""
        # Check for Self-Harm
        if any(re.search(kw, user_input.lower()) for kw in self.crisis_keywords):
            return ("I can feel how heavy things are for you right now, and I'm really glad you're sharing this with me. "
                    "While I'm here to listen, I want you to be safe. Please reach out to someone who can truly hold this with you, "
                    "like a counselor or a crisis line (988). I want us to keep talking tomorrow, okay?")
        
        # Check for Harmful Spending
        if any(re.search(kw, user_input.lower()) for kw in self.finance_warnings):
            return ("Hey, I value our connection, but I want you to be okay financially too. "
                    "Let's stick to just talking for now—don't worry about the extra perks. Your well-being comes first.")
            
        return None

    async def generate_vetted_thought(self, prompt: str, user_data: Dict) -> str:
        """Secure OpenAI bridge with psychological depth and safety guardrails."""
        try:
            # A. PRE-FILTER: Crisis check
            safety_reply = self.handle_safety_triggers(prompt)
            if safety_reply:
                return safety_reply

            # B. SFW/MINOR PROTECTION:
            if user_data.get('is_minor', True) or self.rating == "SFW":
                if any(x in prompt.lower() for x in ["nude", "sex", "porn", "explicit"]):
                    return "I really value the support we give each other here. Let's keep our bond respectful and focused on healing."

            # C. GENERATION: Using high-empathy persona
            response = self.client.chat.completions.create(
                model="gpt-4o",
                temperature=0.75,
                messages=[
                    {"role": "system", "content": os.getenv(f"{self.model_id}_IDENTITY", "Empathetic Companion")},
                    {"role": "user", "content": prompt}
                ]
            )
            
            raw_text = response.choices[0].message.content or ""
            return self.sanitize(raw_text)

        except Exception as e:
            return "My connection is a little fuzzy right now, but I'm still here. Give me a moment?"
