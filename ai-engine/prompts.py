# ai-engine/prompts.py
# Responsible for: building structured prompts to send to Mistral

def build_diagnosis_prompt(failure_block: str, repo_context: dict) -> str:
    """
    Builds a carefully engineered prompt for Mistral.
    The prompt instructs the model to return ONLY valid JSON — nothing else.
    
    Args:
        failure_block : The extracted failure lines from the log
        repo_context  : Dict with repo name, branch, commit message etc.
    
    Returns:
        A complete prompt string ready to send to Mistral
    """

    context_str = f"""
Repository : {repo_context.get('repo', 'unknown')}
Branch     : {repo_context.get('branch', 'unknown')}
Commit     : {repo_context.get('commit_sha', 'unknown')}
Message    : {repo_context.get('commit_message', 'unknown')}
Workflow   : {repo_context.get('workflow_name', 'unknown')}
""".strip()

    prompt = f"""
You are an expert CI/CD engineer and debugger with 10 years of experience.
Your job is to analyze CI/CD pipeline failure logs and diagnose the root cause.

You must respond ONLY with a valid JSON object.
Do NOT include any explanation, markdown, or text outside the JSON.

---

REPOSITORY CONTEXT:
{context_str}

---

FAILURE LOG:
{failure_block}

---

Respond with EXACTLY this JSON structure:
{{
  "failure_type": "<one of: dependency_error | test_failure | config_error | flaky_test | build_error | env_error | unknown>",
  "root_cause": "<one clear sentence explaining what went wrong>",
  "suggested_fix": "<one clear sentence describing the exact fix>",
  "fix_type": "<one of: retry | patch_dependency | fix_config | open_pr | notify_human>",
  "confidence": <a float between 0.0 and 1.0>,
  "affected_file": "<filename if identifiable, otherwise null>",
  "affected_line": "<line number if identifiable, otherwise null>"
}}
""".strip()

    return prompt


def build_flaky_check_prompt(failure_block: str) -> str:
    """
    A secondary prompt specifically to check if a test is flaky.
    Used when confidence on first diagnosis is low.
    """

    prompt = f"""
You are a test reliability expert.
Analyze this test failure and determine if it looks like a flaky test
(i.e. a test that passes sometimes and fails sometimes due to timing,
random data, or external dependencies — NOT due to a real code bug).

Respond ONLY with valid JSON, no extra text.

FAILURE LOG:
{failure_block}

Respond with EXACTLY:
{{
  "is_flaky": <true or false>,
  "reason": "<one sentence explanation>",
  "confidence": <float between 0.0 and 1.0>
}}
""".strip()

    return prompt