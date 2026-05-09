import os
import sys
import asyncio

# 1. Project Root Verification: Ensures the 'cc_empire' package is discoverable
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

async def run_diagnostics():
    print("🧪 EMPIRE DIAGNOSTIC STARTING...\n")
    
    errors = []

    # TEST A: Importing the CNS (Protocols)
    try:
        from cc_empire.core.protocols.identity_vault import IdentityVault
        from cc_empire.core.protocols.nervous_system import NervousSystem
        from cc_empire.core.config import settings
        print("✅ STEP 1: Protocol Import Logic - SUCCESS")
    except ImportError as e:
        errors.append(f"Import Error: {e}")
        print("❌ STEP 1: Protocol Import Logic - FAILED")

    # TEST B: Identity DNA Generation
    try:
        vault = IdentityVault("TEST_MODEL_99")
        dna = vault.lock_identity()
        if dna['model_id'] == "TEST_MODEL_99":
            print("✅ STEP 2: Identity Vault & DNA Burn - SUCCESS")
        else:
            errors.append("DNA mismatch in vault logic.")
    except Exception as e:
        errors.append(f"Vault Error: {e}")
        print("❌ STEP 2: Identity Vault & DNA Burn - FAILED")

    # TEST C: Content Sanitization
    try:
        ns = NervousSystem("LYRA_TEST")
        # We test offline - it should catch the 'robotic' phrase locally
        raw_thought = "As an AI language model, I am feeling great."
        clean_thought = ns.sanitize(raw_thought)
        if "[Identity Protocol Enforced]" in clean_thought:
            print("✅ STEP 3: Nervous System Sanitization - SUCCESS")
        else:
            errors.append("Sanitization failed to catch forbidden phrases.")
    except Exception as e:
        errors.append(f"Nervous System Error: {e}")
        print("❌ STEP 3: Nervous System Sanitization - FAILED")

    # TEST D: Social Loop & Proxy Gate
    try:
        from cc_empire.core.protocols.worker_social import WorkerSocialProtocol
        worker = WorkerSocialProtocol("TEST_MODEL_99")
        # Testing the loop - it should hit the 'Halt' gate because proxies are inactive by default
        result = await worker.execute_social_loop("twitter", "post", {"text": "Hello Hive"})
        if result['status'] == "halt":
            print("✅ STEP 4: Proxy Safety Gate - SUCCESS (Halted as expected)")
        else:
            errors.append(f"Proxy Gate failed to halt unsafe request: {result['status']}")
            print(f"❌ STEP 4: Proxy Safety Gate - FAILED")
    except Exception as e:
        errors.append(f"Social Loop Error: {e}")
        print("❌ STEP 4: Social Loop - FAILED")

    # FINAL REPORT
    print("\n" + "="*30)
    if not errors:
        print("🏆 ALL SYSTEMS NOMINAL. The Empire is ready for Branching.")
    else:
        print(f"🛑 CRITICAL SNAGS DETECTED ({len(errors)}):")
        for err in errors:
            print(f" - {err}")
    print("="*30)

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
