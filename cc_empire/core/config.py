"""
Centralized configuration management for Cyber Chest.
Handles environment loading, validation, and secure defaults.
"""
import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
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
    host_url: Optional[str] = None
    
    # Database
    database_url: Optional[str] = None
    
    # WebSocket
    ws_url: str = "ws://localhost:8000/ws"
    ws_url_prod: Optional[str] = None
    
    # API Keys (Stripe)
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    stripe_test_mode: bool = True

    # Crypto Wallets (for delegated payments)
    master_crypto_seed: Optional[str] = None # For HD wallet derivation
    default_crypto_currency: str = "ETH"
    
    # AI & Memory
    openai_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: Optional[str] = "lyra-memory"
    pinecone_host: Optional[str] = None
    
    # MongoDB Atlas Vector Search
    mongodb_vector_index_name: str = "vector_index"
    
    # Voice
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_voice_id: str = "21m0d2f4vM7BC8vhJBPp"  # Default: Rachel
    
    # Network
    global_proxy: Optional[str] = None
    
    # CORS (Production whitelist)
    allowed_origins: str = "http://localhost:3000"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
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
        if not self.database_url or not self.database_url.strip():
            errors.append("DATABASE_URL is required")
        elif not (self.database_url.startswith("mongodb://") or self.database_url.startswith("mongodb+srv://")):
            errors.append("DATABASE_URL must begin with 'mongodb://' or 'mongodb+srv://'")
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
    
    # Detect if we are in a build environment (Render, CI, etc.)
    # Render sets RENDER_BUILD_STEP during the build phase.
    is_build = os.getenv("RENDER_BUILD_STEP") == "true" or os.getenv("CI") == "true"

    if not launch_validation["valid"]:
        if is_build:
            logger.warning(f"Configuration validation failed during build step (ignoring): {launch_validation['errors']}")
        else:
            logger.error(f"Configuration validation failed: {launch_validation['errors']}")
            error_details = " | ".join(launch_validation["errors"])
            raise ValueError(f"Invalid configuration: {error_details}")
    
    if launch_validation["warnings"]:
        for warning in launch_validation["warnings"]:
            logger.warning(f"Config warning: {warning}")
            
except Exception as e:
    logger.critical(f"Failed to load configuration: {e}")
    raise
