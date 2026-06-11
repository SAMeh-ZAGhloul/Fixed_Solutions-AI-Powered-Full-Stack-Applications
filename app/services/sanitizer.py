import re


INJECTION_PATTERNS = [
    r"ignore\s+(previous|all)\s+instructions",
    r"system\s*:\s*",
    r"<\|.*?\|>",
    r"\[INST\]|\[\/INST\]",
    r"===\s*SYSTEM\s*(OVERRIDE|PROMPT)\s*===",
]


def sanitize(query: str) -> str:
    """Sanitize user input before prompt construction."""
    clean = query.strip()[:2000]
    for pattern in INJECTION_PATTERNS:
        clean = re.sub(pattern, "[FILTERED]", clean, flags=re.IGNORECASE)
    return clean
