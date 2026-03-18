# ai-engine/classifier.py
# Responsible for: orchestrating the full AI diagnosis flow

import sys
sys.path.insert(0, 'ai-engine')

from prompts import build_diagnosis_prompt, build_flaky_check_prompt
from llm_client import ask_mistral, parse_json_response


def diagnose_failure(failure_block: str, repo_context: dict) -> dict:
    """
    Main diagnosis function.
    Sends failure log to Mistral, gets structured diagnosis back.
    
    If confidence is low, runs a secondary flaky-test check.
    
    Args:
        failure_block : Extracted failure lines from log-collector
        repo_context  : Repo metadata dict
    
    Returns:
        Diagnosis dict with failure_type, root_cause, fix_type etc.
    """

    print(f"\n🤖 Sending log to Mistral for diagnosis...")

    # Step 1 — Primary diagnosis
    prompt = build_diagnosis_prompt(failure_block, repo_context)
    raw = ask_mistral(prompt)
    diagnosis = parse_json_response(raw)

    print(f"✅ Diagnosis received — type: {diagnosis.get('failure_type')} | confidence: {diagnosis.get('confidence')}")

    # Step 2 — If confidence is low, run flaky check
    if diagnosis.get('confidence', 1.0) < 0.6:
        print(f"⚠️  Low confidence ({diagnosis.get('confidence')}) — running flaky test check...")

        flaky_prompt = build_flaky_check_prompt(failure_block)
        flaky_raw = ask_mistral(flaky_prompt)
        flaky_result = parse_json_response(flaky_raw)

        # If flaky check is confident it's a flaky test — override
        if flaky_result.get('is_flaky') and flaky_result.get('confidence', 0) > 0.7:
            print(f"🔄 Flaky test detected — overriding fix_type to retry")
            diagnosis['failure_type'] = 'flaky_test'
            diagnosis['fix_type'] = 'retry'
            diagnosis['root_cause'] = flaky_result.get('reason', diagnosis['root_cause'])
            diagnosis['confidence'] = flaky_result.get('confidence', 0.7)

    return diagnosis
