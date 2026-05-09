"""
Centralized configuration management for Cyber Chest.
Handles environment loading, validation, and secure defaults.
"""
import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings
from enum import Enum

logger = logging.getLogger(__name__)

class Environment(str, Enum):
    """Deployment environments."""
    SANDBOX = "sandbox"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    """Pydantic settings for environment validation."""
    
    # Core
    environment: Environment = Environment.SANDBOX
    debug: bool = False
    port: int = 8000
    host: str = "0.0.0.0"
    
    # Database
    database_url: str
    
    # WebSocket
    ws_url: str = "ws://localhost:8000/ws"
    ws_url_prod: Optional[str] = None
    
    # API Keys (Stripe)
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    stripe_test_mode: bool = True
    
    # AI & Memory
    openai_api_key: Optional[str] = None
    pinecone_api_key: str
    pinecone_index_name: str = "lyra-memory"
    pinecone_host: str = "https://pinecone.io"
    
    # Voice
    elevenlabs_api_key: str
    elevenlabs_voice_id: str = "21m0d2f4vM7BC8vhJBPp"  # Default: Rachel
    
    # Network
    global_proxy: Optional[str] = None
    
    # CORS (Production whitelist)
    allowed_origins: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins(self) -> list:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == Environment.PRODUCTION
    
    def validate_launch(self) -> dict:
        """Validate all critical settings before launch."""
        errors = []
        warnings = []
        
        # Critical validations
        if not self.database_url:
            errors.append("DATABASE_URL is required")
        if not self.stripe_secret_key:
            warnings.append("Stripe Key missing: Payments will operate in MOCK mode.")
        if not self.openai_api_key:
            warnings.append("OpenAI Key missing: NervousSystem will use fallback logic.")
        
        # Production-specific validations
        if self.is_production:
            if self.debug:
                errors.append("Debug mode cannot be enabled in production")
            if self.stripe_test_mode:
                warnings.append("Stripe is in TEST mode in production environment")
            if self.allowed_origins == "http://localhost:3000":
                warnings.append("Using localhost CORS in production - update ALLOWED_ORIGINS")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

# Singleton instance
try:
    settings = Settings()
    launch_validation = settings.validate_launch()
    
    if not launch_validation["valid"]:
        logger.error(f"Configuration validation failed: {launch_validation['errors']}")
        raise ValueError("Invalid configuration - see errors above")
    
    if launch_validation["warnings"]:
        for warning in launch_validation["warnings"]:
            logger.warning(f"Config warning: {warning}")
            
except Exception as e:
    logger.critical(f"Failed to load configuration: {e}")
    raise
