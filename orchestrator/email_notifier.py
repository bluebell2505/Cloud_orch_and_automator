# orchestrator/email_notifier.py
# Sends email notifications when AI needs human review

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


def send_failure_email(diagnosis: dict, repo: str, run_id: int, action_taken: str):
    """
    Sends an email notification when the AI needs human review.
    Called by remediation.py instead of Slack.
    """
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print(f"[EMAIL] Skipped — EMAIL_SENDER or EMAIL_PASSWORD not set")
        return

    # Confidence color indicator
    confidence = diagnosis.get('confidence', 0)
    if confidence >= 0.8:
        confidence_label = "HIGH"
    elif confidence >= 0.6:
        confidence_label = "MEDIUM"
    else:
        confidence_label = "LOW"

    subject = f"[CI/CD Alert] Pipeline Failure in {repo} — Human Review Needed"

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #1E4D78; padding: 20px; border-radius: 8px 8px 0 0;">
            <h2 style="color: white; margin: 0;">CI/CD Pipeline Failure Alert</h2>
            <p style="color: #B3D4F0; margin: 5px 0 0 0;">Human Review Required</p>
        </div>

        <div style="background-color: #F5F7FA; padding: 20px; border: 1px solid #DDDDDD;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px; font-weight: bold; color: #555; width: 40%;">Repository</td>
                    <td style="padding: 8px; color: #1E4D78;">{repo}</td>
                </tr>
                <tr style="background: white;">
                    <td style="padding: 8px; font-weight: bold; color: #555;">Run ID</td>
                    <td style="padding: 8px;">{run_id}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; color: #555;">Failure Type</td>
                    <td style="padding: 8px; color: #C0392B; font-weight: bold;">{diagnosis.get('failure_type', 'unknown').upper()}</td>
                </tr>
                <tr style="background: white;">
                    <td style="padding: 8px; font-weight: bold; color: #555;">Root Cause</td>
                    <td style="padding: 8px;">{diagnosis.get('root_cause', 'Unknown')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; color: #555;">Suggested Fix</td>
                    <td style="padding: 8px; color: #27AE60;">{diagnosis.get('suggested_fix', 'Manual review required')}</td>
                </tr>
                <tr style="background: white;">
                    <td style="padding: 8px; font-weight: bold; color: #555;">Affected File</td>
                    <td style="padding: 8px;">{diagnosis.get('affected_file') or 'Not identified'}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; color: #555;">AI Confidence</td>
                    <td style="padding: 8px;">
                        <span style="background: {'#27AE60' if confidence >= 0.8 else '#F39C12' if confidence >= 0.6 else '#C0392B'};
                              color: white; padding: 2px 8px; border-radius: 4px;">
                            {confidence_label} ({confidence:.0%})
                        </span>
                    </td>
                </tr>
                <tr style="background: white;">
                    <td style="padding: 8px; font-weight: bold; color: #555;">Action Taken</td>
                    <td style="padding: 8px;">{action_taken}</td>
                </tr>
            </table>
        </div>

        <div style="background-color: #FFF8E1; padding: 15px; border: 1px solid #F9A825; border-top: none;">
            <p style="margin: 0; color: #7A5200;">
                <strong>Why this email?</strong>
                The AI confidence score was below the auto-fix threshold (65%) or the failure type
                requires human judgment. Please review the pipeline and apply the suggested fix manually.
            </p>
        </div>

        <div style="background-color: #1E4D78; padding: 12px; border-radius: 0 0 8px 8px; text-align: center;">
            <a href="https://github.com/{repo}/actions" 
               style="color: white; text-decoration: none; font-weight: bold;">
                View Pipeline on GitHub →
            </a>
        </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        print(f"[EMAIL] Notification sent to {EMAIL_RECEIVER}")

    except Exception as e:
        print(f"[EMAIL] Failed to send: {e}")
