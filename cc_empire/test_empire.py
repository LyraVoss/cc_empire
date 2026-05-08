import os
import sys
import asyncio

# 1. Path Verification: Ensures VSCode sees your new architecture
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

async def run_diagnostics():
    print("🧪 EMPIRE DIAGNOSTIC STARTING...\n")
    
    errors = []

    # TEST A: Importing the CNS (Protocols)
    try:
        from core.protocols.identity_vault import IdentityVault
        from core.protocols.nervous_system import NervousSystem
        from core.protocols.worker_social import WorkerSocialProtocol
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
        worker = WorkerSocialProtocol("TEST_MODEL_99")
        # Testing the loop - it should hit the 'Halt' gate because proxies are empty
        result = await worker.execute_social_loop("twitter", "post", {"text": "Hello Hive"})
        if result['status'] == "halt":
            print("✅ STEP 4: Proxy Safety Gate - SUCCESS (Halted as expected)")
        else:
            print(f"⚠️ STEP 4: Proxy Gate result: {result['status']}")
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
