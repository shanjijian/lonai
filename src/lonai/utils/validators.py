"""Validation functions."""

import os
import re
from pathlib import Path
from typing import Optional, Tuple


def validate_api_keys() -> Tuple[bool, Optional[str]]:
    """Validate that required API keys are present.
    
    Checks for:
    1. TAVILY_API_KEY (always required for search)
    2. At least one valid agent configuration (Anthropic, OpenAI, or Custom)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    error_messages = []
    
    # 1. Check Search Key
    if not os.environ.get("TAVILY_API_KEY"):
         error_messages.append("Missing TAVILY_API_KEY for search functionality.")

    # 2. Check Agent Provider Keys
    # We check if *any* valid combination exists or if the specific one selected in settings is valid.
    # Since we don't have access to settings here easily without circular imports, 
    # we'll do a loose check: ensure at least one known key is present.
    
    has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))
    has_google = bool(os.environ.get("GOOGLE_API_KEY"))
    has_agent_key = bool(os.environ.get("AGENT_API_KEY"))
    
    # If using custom provider, base url might be enough, but let's assume we need at least one key
    # or the user knows what they are doing. 
    # To be safe, warn if NO keys are found at all.
    
    if not (has_anthropic or has_openai or has_google or has_agent_key):
        error_messages.append(
            "Missing Agent API config. Please set one of:\n"
            "  - ANTHROPIC_API_KEY\n"
            "  - OPENAI_API_KEY\n"
            "  - GOOGLE_API_KEY\n"
            "  - AGENT_API_KEY (generic)"
        )

    if error_messages:
        return False, "\n".join(error_messages)
    
    return True, None


def validate_path(path: Path, must_exist: bool = False, create: bool = False) -> bool:
    """Validate a file path.
    
    Args:
        path: Path to validate
        must_exist: Whether the path must already exist
        create: Whether to create the path if it doesn't exist
        
    Returns:
        True if valid, False otherwise
    """
    try:
        path = Path(path)
        
        if must_exist and not path.exists():
            return False
        
        if create and not path.exists():
            if path.suffix:  # It's a file
                path.parent.mkdir(parents=True, exist_ok=True)
            else:  # It's a directory
                path.mkdir(parents=True, exist_ok=True)
        
        return True
        
    except Exception:
        return False


def validate_query(query: str, min_length: int = 3, max_length: int = 500) -> Tuple[bool, Optional[str]]:
    """Validate a research query.
    
    Args:
        query: Query string to validate
        min_length: Minimum query length
        max_length: Maximum query length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    query = query.strip()
    
    if len(query) < min_length:
        return False, f"Query too short (minimum {min_length} characters)"
    
    if len(query) > max_length:
        return False, f"Query too long (maximum {max_length} characters)"
    
    return True, None


def sanitize_filename(filename: str, max_length: int = 50) -> str:
    """Sanitize a string to be used as a filename.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Trim to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    return sanitized or "unnamed"
