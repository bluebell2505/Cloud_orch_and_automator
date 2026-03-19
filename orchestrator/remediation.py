# # orchestrator/remediation.py
# # Decides and executes the fix based on AI diagnosis

# import os
# import requests
# from dotenv import load_dotenv
# from github_client import retrigger_pipeline, open_fix_pr

# load_dotenv()

# CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))
# SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")


# def notify_human(diagnosis: dict, repo: str, run_id: int, action: str):
#     """Send email notification when human review is needed."""
#     try:
#         import sys, os
#         sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
#         from email_notifier import send_failure_email
#         send_failure_email(diagnosis, repo, run_id, action)
#     except Exception as e:
#         print(f"[EMAIL] Error: {e}")

# def execute_fix(diagnosis: dict, repo: str, run_id: int) -> dict:
#     """
#     Main remediation function called by orchestrator.
#     Decides what action to take based on AI diagnosis.
#     """
#     fix_type = diagnosis.get("fix_type", "unknown")
#     confidence = diagnosis.get("confidence", 0.0)

#     # If AI is not confident enough, always notify human
#     if confidence < CONFIDENCE_THRESHOLD:
#         notify_human_on_slack(diagnosis, repo)
#         return {
#             "action": "notified_human",
#             "reason": f"low_confidence ({confidence:.0%})"
#         }

#     if fix_type == "retry":
#         success = retrigger_pipeline(repo, run_id)
#         return {
#             "action": "retried",
#             "success": success
#         }

#     elif fix_type == "patch_dependency":
#         affected_file = diagnosis.get("affected_file", "requirements.txt")
#         suggested_fix = diagnosis.get("suggested_fix", "")
#         pr_url = open_fix_pr(
#             repo=repo,
#             filename=f"pipeline-samples/python-app/{affected_file}",
#             old_content="",
#             new_content=suggested_fix,
#             fix_description=f"Fix dependency issue: {suggested_fix}"
#         )
#         return {
#             "action": "pr_opened",
#             "pr_url": pr_url
#         }

#     elif fix_type == "fix_config":
#         notify_human_on_slack(diagnosis, repo)
#         return {
#             "action": "notified_human",
#             "reason": "config_fix_requires_review"
#         }

#     elif fix_type == "notify_human":
#         notify_human_on_slack(diagnosis, repo)
#         return {
#             "action": "notified_human",
#             "reason": "fix_type_is_notify_human"
#         }

#     else:
#         notify_human_on_slack(diagnosis, repo)
#         return {
#             "action": "unknown",
#             "reason": f"unhandled fix_type: {fix_type}"
#         }

# orchestrator/remediation.py
# Decides and executes the fix based on AI diagnosis
#-------------------------------------------------------------
# import os
# import sys
# from dotenv import load_dotenv

# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# from github_client import retrigger_pipeline, open_fix_pr
# from email_notifier import send_failure_email

# load_dotenv()

# CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))


# def notify_human(diagnosis: dict, repo: str, run_id: int, action: str) -> None:
#     """Send email notification when human review is needed."""
#     try:
#         send_failure_email(diagnosis, repo, run_id, action)
#     except Exception as e:
#         print(f"[EMAIL] Error: {e}")


# def execute_fix(diagnosis: dict, repo: str, run_id: int, branch: str = "main") -> dict:
#     """
#     Main remediation function called by orchestrator.
#     Decides what action to take based on AI diagnosis.
#     """
#     fix_type   = diagnosis.get("fix_type", "unknown")
#     confidence = diagnosis.get("confidence", 0.0)

#     print(f"\n🔧 Remediation Engine activated...")
#     print(f"   Fix type   : {fix_type}")
#     print(f"   Confidence : {confidence}")

#     # --- Safety gate: confidence too low → always notify human ---
#     if confidence < CONFIDENCE_THRESHOLD:
#         print(f"   ⚠️  Confidence too low ({confidence:.0%}) — notifying human")
#         notify_human(diagnosis, repo, run_id, f"No auto-fix — confidence {confidence:.0%} below threshold")
#         return {
#             "action": "notified_human",
#             "reason": f"low_confidence ({confidence:.0%})"
#         }

#     # --- Route by fix type ---

#     if fix_type == "retry":
#         success = retrigger_pipeline(repo, run_id)
#         print(f"   🔄 Pipeline retrigger: {'success' if success else 'failed'}")
#         return {
#             "action": "retried",
#             "success": success
#         }

#     elif fix_type == "patch_dependency":
#         affected_file = diagnosis.get("affected_file", "requirements.txt")
#         suggested_fix = diagnosis.get("suggested_fix", "")
#         # Always use full path for python app
#         full_path = f"pipeline-samples/python-app/{affected_file}" if "/" not in affected_file else affected_file
#         pr_url = open_fix_pr(
#             repo=repo,
#             branch=branch,
#             filename=full_path,
#             fix_description=suggested_fix
#         )

#     elif fix_type == "open_pr":
#         affected_file = diagnosis.get("affected_file", "unknown")
#         suggested_fix = diagnosis.get("suggested_fix", "")
#         pr_url = open_fix_pr(
#             repo=repo,
#             branch=branch,
#             filename=affected_file,
#             fix_description=suggested_fix
#         )
#         print(f"   📬 Fix PR opened: {pr_url}")
#         return {
#             "action": "pr_opened",
#             "pr_url": pr_url
#         }

#     elif fix_type in ["fix_config", "notify_human"]:
#         print(f"   📧 Notifying human via email...")
#         notify_human(diagnosis, repo, run_id, f"Manual fix required — fix_type: {fix_type}")
#         return {
#             "action": "notified_human",
#             "reason": fix_type
#         }

#     else:
#         print(f"   ❓ Unknown fix type — notifying human")
#         notify_human(diagnosis, repo, run_id, f"Unknown fix type: {fix_type}")
#         return {
#             "action": "unknown",
#             "reason": f"unhandled fix_type: {fix_type}"
#         }

#----------------------------------------

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from github_client import retrigger_pipeline, open_fix_pr
from email_notifier import send_failure_email

load_dotenv()

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))


def notify_human(diagnosis: dict, repo: str, run_id: int, reason: str) -> None:
    try:
        send_failure_email(diagnosis, repo, run_id, reason)
    except Exception as e:
        print(f"[EMAIL] Error: {e}")


def execute_fix(diagnosis: dict, repo: str, run_id: int, branch: str = "master") -> dict:
    fix_type = diagnosis.get("fix_type", "unknown")
    confidence = diagnosis.get("confidence", 0.0)

    print(f"\n🔧 Remediation Engine activated...")
    print(f"   Fix type   : {fix_type}")
    print(f"   Confidence : {confidence}")

    if confidence < CONFIDENCE_THRESHOLD:
        print(f"   ⚠️  Confidence too low — notifying human")
        notify_human(diagnosis, repo, run_id, f"Low confidence: {confidence:.0%}")
        return {"action": "notified_human", "reason": f"low_confidence ({confidence:.0%})"}

    if fix_type == "retry":
        success = retrigger_pipeline(repo, run_id)
        print(f"   🔄 Pipeline retrigger: {'success' if success else 'failed'}")
        return {"action": "retried", "success": success}

    elif fix_type in ["patch_dependency", "open_pr"]:
        affected_file = diagnosis.get("affected_file", "requirements.txt")
        suggested_fix = diagnosis.get("suggested_fix", "")
        full_path = f"pipeline-samples/python-app/{affected_file}" if "/" not in affected_file else affected_file
        pr_url = open_fix_pr(
            repo=repo,
            branch=branch,
            filename=full_path,
            fix_description=suggested_fix
        )
        print(f"   📬 Fix PR: {pr_url}")
        return {"action": "pr_opened", "pr_url": pr_url}

    elif fix_type in ["fix_config", "notify_human"]:
        print(f"   📧 Notifying human via email...")
        notify_human(diagnosis, repo, run_id, f"Manual fix required: {fix_type}")
        return {"action": "notified_human", "reason": fix_type}

    else:
        print(f"   ❓ Unknown fix type — notifying human")
        notify_human(diagnosis, repo, run_id, f"Unknown fix type: {fix_type}")
        return {"action": "unknown", "reason": f"unhandled fix_type: {fix_type}"}