#!/usr/bin/env python3
"""
SANDBOX LAUNCHER
================
Launches Cyber Chest in sandbox mode for validation testing.
- No data recording
- All systems pass health checks
- Validates Lyra initialization, thumbprint, and autonomous model generation
- Safe to run before live deployment

Usage:
    python sandbox_launcher.py
    
After successful sandbox launch:
    - Verify Lyra's self-check output
    - Verify thumbprint initialization
    - Verify Twitter construction (if enabled)
    - Call /factory/shipyard/launch to generate first autonomous model
    - Kill instance and deploy to cloud environment
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Set up system paths for module discovery
ROOT_DIR = Path(__file__).parents[2]
BRANCH_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(BRANCH_DIR))

# Set sandbox environment
os.environ["ENVIRONMENT"] = "sandbox"
os.environ["DEBUG"] = "true"
os.environ["RECORDING_ENABLED"] = "false"

from core.config import settings

from src.logger import setup_logging
from src.health import HealthCheck
from src.identity.thumbprint_engine import IdentityVault
from src.brain.ai_generator import BrainEngine
from src.voice.vocal_cords import VocalCords

logger = setup_logging(app_name="sandbox", debug=True)

class SandboxValidator:
    """Comprehensive sandbox validation suite."""
    
    def __init__(self):
        self.results = {}
        self.all_passed = True
    
    async def validate_all(self) -> dict:
        """Run all sandbox validation checks."""
        logger.info("=" * 80)
        logger.info("🏗️  SANDBOX VALIDATION SUITE")
        logger.info("=" * 80)
        
        # 1. Health checks
        logger.info("\n[1/5] Running health checks...")
        health_check = HealthCheck()
        health_result = await health_check.run_all_checks()
        self.results["health_checks"] = health_result
        self.all_passed = self.all_passed and health_result["all_passed"]
        
        # 2. Identity/Thumbprint validation
        logger.info("\n[2/5] Validating identity vault and thumbprint...")
        try:
            vault = IdentityVault("lyra_0")
            dna = vault.lock_dna()
            fingerprint = vault.get_fingerprint()
            vault_health = vault.health_check()
            
            logger.info(f"✓ Thumbprint: {fingerprint}")
            logger.info(f"✓ DNA locked: {vault.path}")
            logger.info(f"✓ Vault health: {vault_health}")
            
            self.results["identity"] = {
                "status": "valid",
                "fingerprint": fingerprint,
                "dna_path": str(vault.path),
                "health": vault_health
            }
        except Exception as e:
            logger.error(f"✗ Identity validation failed: {e}")
            self.results["identity"] = {"status": "failed", "error": str(e)}
            self.all_passed = False
        
        # 3. Brain engine validation
        logger.info("\n[3/5] Validating brain engine...")
        try:
            brain = BrainEngine("lyra_0")
            brain_health = brain.health_check()
            logger.info(f"✓ Brain initialized: {brain_health}")
            self.results["brain"] = brain_health
        except Exception as e:
            logger.error(f"✗ Brain validation failed: {e}")
            self.results["brain"] = {"status": "failed", "error": str(e)}
            self.all_passed = False
        
        # 4. Voice system validation
        logger.info("\n[4/5] Validating voice system...")
        try:
            voice = VocalCords("lyra_0")
            voice_health = voice.health_check()
            logger.info(f"✓ Voice system initialized: {voice_health}")
            self.results["voice"] = voice_health
        except Exception as e:
            logger.error(f"✗ Voice validation failed: {e}")
            self.results["voice"] = {"status": "failed", "error": str(e)}
            self.all_passed = False
        
        # 5. Sandbox configuration validation
        logger.info("\n[5/5] Validating sandbox configuration...")
        try:
            sandbox_checks = {
                "recording_disabled": os.getenv("RECORDING_ENABLED", "false").lower() == "false",
                "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
                "environment": os.getenv("ENVIRONMENT", "unknown")
            }
            
            if sandbox_checks["recording_disabled"]:
                logger.info("✓ Data recording is disabled")
            else:
                logger.warning("⚠️  Data recording is enabled - disable before launch")
                self.all_passed = False
            
            logger.info(f"✓ Sandbox config: {sandbox_checks}")
            self.results["sandbox_config"] = sandbox_checks
        except Exception as e:
            logger.error(f"✗ Sandbox config validation failed: {e}")
            self.results["sandbox_config"] = {"status": "failed", "error": str(e)}
            self.all_passed = False
        
        # Summary
        logger.info("\n" + "=" * 80)
        if self.all_passed:
            logger.info("✅ SANDBOX VALIDATION PASSED - READY FOR LAUNCH")
        else:
            logger.error("❌ SANDBOX VALIDATION FAILED - ADDRESS ERRORS ABOVE")
        logger.info("=" * 80)
        
        return {
            "all_passed": self.all_passed,
            "results": self.results
        }

async def main():
    """Run sandbox validator and start server."""
    validator = SandboxValidator()
    validation_result = await validator.validate_all()
    
    if not validation_result["all_passed"]:
        logger.error("\n❌ Sandbox validation failed. Fix errors and retry.")
        sys.exit(1)
    
    logger.info("\n" + "=" * 80)
    logger.info("🚀 STARTING CYBER CHEST IN SANDBOX MODE")
    logger.info("=" * 80)
    logger.info("Next steps:")
    logger.info("  1. POST to /factory/shipyard/launch?model_name='Nova_1' to generate first model")
    logger.info("  2. Verify model DNS and configuration")
    logger.info("  3. Kill this instance: Ctrl+C")
    logger.info("  4. Deploy to cloud environment")
    logger.info("=" * 80 + "\n")
    
    # Start the FastAPI app
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )

if __name__ == "__main__":
    asyncio.run(main())
