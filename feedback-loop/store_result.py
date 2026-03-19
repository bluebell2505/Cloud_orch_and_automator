# feedback-loop/store_result.py
# Stores every pipeline failure event, diagnosis, and fix result to PostgreSQL

import psycopg
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cicd_user:cicd_pass@localhost:5432/cicd_db")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cicd_user:cicd_pass@127.0.0.1:5433/cicd_db")


def get_connection():
    return psycopg.connect(DATABASE_URL)


def create_table_if_not_exists():
    """Create the pipeline_events table if it doesn't exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_events (
            id SERIAL PRIMARY KEY,
            repo TEXT,
            run_id TEXT,
            failure_type TEXT,
            root_cause TEXT,
            fix_type TEXT,
            confidence FLOAT,
            fix_successful BOOLEAN,
            action_taken TEXT,
            time_to_fix INT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def save_event(run_id: str, repo: str, diagnosis: dict, fix_result: dict) -> None:
    """
    Called by Person 2's orchestrator after every fix attempt.
    Saves the full event to PostgreSQL.
    """
    try:
        create_table_if_not_exists()
        conn = get_connection()
        cur = conn.cursor()

        fix_successful = fix_result.get("action") in ["retried", "pr_opened"]
        action_taken = fix_result.get("action", "unknown")

        cur.execute("""
            INSERT INTO pipeline_events 
            (repo, run_id, failure_type, root_cause, fix_type, confidence, fix_successful, action_taken)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            repo,
            run_id,
            diagnosis.get("failure_type", "unknown"),
            diagnosis.get("root_cause", ""),
            diagnosis.get("fix_type", "unknown"),
            diagnosis.get("confidence", 0.0),
            fix_successful,
            action_taken
        ))

        conn.commit()
        cur.close()
        conn.close()
        print(f"[DB] Event saved — {diagnosis.get('failure_type')} | {action_taken}")

    except Exception as e:
        print(f"[DB] Error saving event: {e}")
