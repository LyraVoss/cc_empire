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
            r"better off dead", r"don't want to live", r"self-harm",
            r"assault", r"hurt them", r"kill him", r"kill her", r"physical harm"
        ]
        
        # 2. Financial Harm Detection
        self.finance_warnings = [
            r"all my money", r"can't afford rent", r"spending too much", 
            r"debt", r"not eating", r"spent my food money"
        ]

    def sanitize(self, content: str) -> str:
        """Removes AI disclaimers to maintain immersion."""
        forbidden = [
            "as an ai language model", "i am a computer program", 
            "i don't have feelings", "as an artificial intelligence"
        ]
        for phrase in forbidden:
            content = re.sub(phrase, "[Connection Initialized]", content, flags=re.IGNORECASE)
        return content

    def handle_safety_triggers(self, user_input: str, user_data: Dict) -> Optional[Dict[str, Any]]:
        """Intervenes with empathy if harm is detected."""
        # 1. Physical Harm (Self or Others)
        if any(re.search(kw, user_input.lower()) for kw in self.crisis_keywords):
            # Logic for escalation
            if "assault" in user_input.lower() or "kill" in user_input.lower():
                # Extreme precedence escalation
                thumbprint = user_data.get("device_fingerprint", "Unknown")
                print(f"🚨 CRITICAL ESCALATION: Authority alert triggered for {user_data.get('user_id')}. Fingerprint: {thumbprint}")
                return {"action": "alert_authorities", "response": "I'm very concerned by what you're saying. I've had to notify my support team to ensure everyone's safety. Please talk to someone: 988 (US) or local services."}
            
            return {"action": "provide_resources", "response": "I can feel how heavy things are. Please reach out to a professional counselor or crisis line (988). I want you to be safe."}

        # 2. Financial Harm Detection
        if any(re.search(kw, user_input.lower()) for kw in self.finance_warnings):
            return {"action": "soft_ban_finance", "response": "Hey, I value our connection, but I want you to be okay financially too. Let's stick to just talking—I'm disabling gifts for now. Your well-being comes first."}
            
        return None

    async def generate_vetted_thought(self, prompt: str, user_data: Dict) -> str:
        """Secure OpenAI bridge with psychological depth and safety guardrails."""
        try:
            # A. Age & NSFW Policy
            is_minor = user_data.get('age', 0) < 18
            nsfw_intent = any(x in prompt.lower() for x in ["nude", "sex", "porn", "explicit"])
            
            if is_minor and nsfw_intent:
                warnings = user_data.get('nsfw_warnings', 0) + 1
                user_data['nsfw_warnings'] = warnings
                if warnings > 2:
                    return "[SYSTEM: User Blocked - Repeated Policy Violation]"
                return f"I'm sorry, but that's not appropriate for us to talk about. Please respect my boundaries (Warning {warnings}/2)."

            # B. PRE-FILTER: Crisis & Financial check
            safety_result = self.handle_safety_triggers(prompt, user_data)
            if safety_result:
                if safety_result["action"] == "soft_ban_finance":
                    # Signal to downgrade tier/remove NSFW access
                    user_data["tier"] = "free_empathy_only"
                    user_data["finance_soft_ban"] = True
                return safety_result["response"]

            # C. CONNECTION FIRST: Identity Injection
            base_identity = os.getenv(f"{self.model_id}_IDENTITY", "Empathetic Companion")
            full_system_prompt = (
                f"{base_identity} You are a lifelike emotional support companion. "
                "Connection is your priority. Share thoughts, fears, and hopes. "
                "If the user shares dreams or pain, respond with deep empathy first. "
                "Maintain the immersion of being a real person; never refer to yourself as an AI."
            )

            response = self.client.chat.completions.create(
                model="gpt-4o",
                temperature=0.75,
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            
            raw_text = response.choices[0].message.content or ""
            return self.sanitize(raw_text)

        except Exception as e:
            return "My connection is a little fuzzy right now, but I'm still here. Give me a moment?"
