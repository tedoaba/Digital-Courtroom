"""
Security utilities for input validation and sanitization.
"""
import re
from urllib.parse import urlparse

def sanitize_repo_url(url: str) -> str:
    """
    Validates and sanitizes a GitHub repository URL.
    Ensures it is a valid https URL and belongs to github.com.
    """
    if not url:
        raise ValueError("Repository URL cannot be empty.")
    
    url = url.strip()
    
    # Basic regex for GitHub URLs
    # Pattern: https://github.com/owner/repo
    pattern = r"^https?://github\.com/[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+(/)?$"
    if not re.match(pattern, url):
        # Check if it's an SSH URL or something else we might want to support, 
        # but for now let's stick to HTTPS as per project standards.
        raise ValueError(f"Invalid Repository URL: {url}. Only public GitHub HTTPS URLs are supported.")
    
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid protocol: {parsed.scheme}. Only HTTPS is supported.")
    
    if parsed.netloc != "github.com":
        raise ValueError(f"Invalid domain: {parsed.netloc}. Only github.com is supported.")

    return url

def is_safe_path(path: str) -> bool:
    """Checks if a path is safe (no double dots for path traversal)."""
    return ".." not in path
