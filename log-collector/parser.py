# log-collector/parser.py
# Responsible for: taking raw CI log text and extracting only the failure block

def extract_failure_block(raw_log: str, context_lines: int = 15) -> str:
    """
    Scans a raw CI/CD log and extracts lines around the failure point.
    
    Args:
        raw_log: The full raw log text from GitHub Actions
        context_lines: How many lines before/after error to capture
    
    Returns:
        A cleaned string containing only the relevant failure block
    """
    
    # Keywords that signal a failure in CI logs
    FAILURE_KEYWORDS = [
        'ERROR', 'Error', 'FAILED', 'Failed',
        'Exception', 'Traceback', 'exit code 1',
        'ModuleNotFoundError', 'SyntaxError',
        'AssertionError', 'ConnectionError',
        'No module named', 'command not found'
    ]
    
    lines = raw_log.split('\n')
    failure_indices = []
    
    # Find all lines that contain a failure keyword
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in FAILURE_KEYWORDS):
            failure_indices.append(i)
    
    # If no failure found, return last 30 lines as fallback
    if not failure_indices:
        return '\n'.join(lines[-30:])
    
    # Collect lines around each failure point
    collected = set()
    for idx in failure_indices:
        start = max(0, idx - context_lines)
        end = min(len(lines), idx + context_lines)
        for i in range(start, end):
            collected.add(i)
    
    # Return collected lines in order
    result_lines = [lines[i] for i in sorted(collected)]
    return '\n'.join(result_lines)


def clean_log(raw_log: str) -> str:
    """
    Removes timestamps, ANSI color codes, and noise from logs.
    
    Args:
        raw_log: Raw log with potential formatting noise
    
    Returns:
        Clean readable log text
    """
    import re
    
    # Remove ANSI color/format codes (e.g. \033[32m)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    cleaned = ansi_escape.sub('', raw_log)
    
    # Remove GitHub Actions timestamps like "2024-01-15T10:23:45.123Z "
    timestamp_pattern = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z\s')
    cleaned = timestamp_pattern.sub('', cleaned)
    
    # Remove blank lines
    lines = [line for line in cleaned.split('\n') if line.strip()]
    
    return '\n'.join(lines)


def process_log(raw_log: str) -> dict:
    """
    Master function — cleans log then extracts failure block.
    This is what the orchestrator will call.
    
    Returns a dict with both the full cleaned log and failure block.
    """
    cleaned = clean_log(raw_log)
    failure_block = extract_failure_block(cleaned)
    
    return {
        "full_log": cleaned,
        "failure_block": failure_block,
        "total_lines": len(cleaned.split('\n')),
        "failure_lines": len(failure_block.split('\n'))
    }