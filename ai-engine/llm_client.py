# ai-engine/llm_client.py
# Responsible for: talking to Ollama (Mistral) and returning parsed responses

import ollama
import json
import os
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "mistral")


def ask_mistral(prompt: str) -> str:
    """
    Sends a prompt to Mistral via Ollama and returns the raw text response.
    
    Args:
        prompt: The full prompt string
    
    Returns:
        Raw response text from Mistral
    """
    response = ollama.chat(
        model=MODEL,
        messages=[{
            'role': 'user',
            'content': prompt
        }],
        options={
            'temperature': 0.1,   # Low = more consistent, less creative
            'top_p': 0.9,
        }
    )
    return response['message']['content']


def parse_json_response(raw_response: str) -> dict:
    """
    Safely parses Mistral's response as JSON.
    Handles cases where model wraps output in markdown or returns a list.
    """
    cleaned = raw_response.strip()
    
    # Strip markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.split('\n')
        cleaned = '\n'.join(lines[1:-1])

    try:
        parsed = json.loads(cleaned)
        # If model returned a list, take the first item
        if isinstance(parsed, list):
            parsed = parsed[0] if parsed else {}
        # Make sure it's a dict
        if not isinstance(parsed, dict):
            raise ValueError("Response is not a dict")
        return parsed
    except Exception as e:
        return {
            "failure_type": "unknown",
            "root_cause": "AI response could not be parsed",
            "suggested_fix": "Manual review required",
            "fix_type": "notify_human",
            "confidence": 0.0,
            "affected_file": None,
            "affected_line": None,
            "parse_error": str(e),
            "raw_response": raw_response
        }
    """
    Safely parses Mistral's response as JSON.
    Handles cases where Mistral wraps output in markdown code blocks.
    
    Args:
        raw_response: Raw text from Mistral
    
    Returns:
        Parsed dict, or error dict if parsing fails
    """
    # Strip markdown code fences if present (```json ... ```)
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split('\n')
        # Remove first line (```json) and last line (```)
        cleaned = '\n'.join(lines[1:-1])

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {
            "failure_type": "unknown",
            "root_cause": "AI response could not be parsed",
            "suggested_fix": "Manual review required",
            "fix_type": "notify_human",
            "confidence": 0.0,
            "affected_file": None,
            "affected_line": None,
            "parse_error": str(e),
            "raw_response": raw_response
        }