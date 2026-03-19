# orchestrator/remediation.py
# Decides and executes the fix based on AI diagnosis

import os
import requests
from dotenv import load_dotenv
from github_client import retrigger_pipeline, open_fix_pr

load_dotenv()

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")


def notify_human_on_slack(diagnosis: dict, repo: str):
    """Send a Slack message when AI is unsure or fix type is notify_human."""
    if not SLACK_WEBHOOK_URL:
        print(f"[SLACK] Would notify human: {diagnosis['root_cause']}")
        return

    message = {
        "text": f"🚨 *CI/CD Failure — Human Review Needed*\n"
                f"*Repo:* {repo}\n"
                f"*Failure Type:* {diagnosis['failure_type']}\n"
                f"*Root Cause:* {diagnosis['root_cause']}\n"
                f"*Suggested Fix:* {diagnosis['suggested_fix']}\n"
                f"*AI Confidence:* {diagnosis['confidence']:.0%}"
    }
    requests.post(SLACK_WEBHOOK_URL, json=message)


def execute_fix(diagnosis: dict, repo: str, run_id: int) -> dict:
    """
    Main remediation function called by orchestrator.
    Decides what action to take based on AI diagnosis.
    """
    fix_type = diagnosis.get("fix_type", "unknown")
    confidence = diagnosis.get("confidence", 0.0)

    # If AI is not confident enough, always notify human
    if confidence < CONFIDENCE_THRESHOLD:
        notify_human_on_slack(diagnosis, repo)
        return {
            "action": "notified_human",
            "reason": f"low_confidence ({confidence:.0%})"
        }

    if fix_type == "retry":
        success = retrigger_pipeline(repo, run_id)
        return {
            "action": "retried",
            "success": success
        }

    elif fix_type == "patch_dependency":
        affected_file = diagnosis.get("affected_file", "requirements.txt")
        suggested_fix = diagnosis.get("suggested_fix", "")
        pr_url = open_fix_pr(
            repo=repo,
            filename=f"pipeline-samples/python-app/{affected_file}",
            old_content="",
            new_content=suggested_fix,
            fix_description=f"Fix dependency issue: {suggested_fix}"
        )
        return {
            "action": "pr_opened",
            "pr_url": pr_url
        }

    elif fix_type == "fix_config":
        notify_human_on_slack(diagnosis, repo)
        return {
            "action": "notified_human",
            "reason": "config_fix_requires_review"
        }

    elif fix_type == "notify_human":
        notify_human_on_slack(diagnosis, repo)
        return {
            "action": "notified_human",
            "reason": "fix_type_is_notify_human"
        }

    else:
        notify_human_on_slack(diagnosis, repo)
        return {
            "action": "unknown",
            "reason": f"unhandled fix_type: {fix_type}"
        }
