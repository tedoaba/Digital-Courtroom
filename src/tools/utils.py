import os
import shutil
import logging
from pathlib import Path
from urllib.parse import urlparse
from typing import List

logger = logging.getLogger(__name__)

# Constants
DISK_LIMIT_BYTES = 1 * 1024 * 1024 * 1024  # 1GB
ALLOWED_DOMAINS = {"github.com", "gitlab.com"}
ALLOWED_PROTOCOLS = {"https"}


def validate_source_url(url: str) -> bool:
    """
    Validates that a URL is from an approved domain and uses HTTPS.
    Ref: FR-006
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ALLOWED_PROTOCOLS:
            logger.warning(f"Invalid protocol: {parsed.scheme}")
            return False
        
        # Check domain suffix/match
        domain = parsed.netloc.lower()
        if not any(domain == d or domain.endswith(f".{d}") for d in ALLOWED_DOMAINS):
            logger.warning(f"Domain not in whitelist: {domain}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"URL parsing failed: {e}")
        return False


def get_dir_size(path: Path) -> int:
    """Returns total size of directory in bytes."""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(Path(entry.path))
    except (PermissionError, OSError):
        pass
    return total


def check_disk_limit(path: Path) -> bool:
    """
    Checks if a directory exceeds the 1GB limit.
    Ref: FR-009
    """
    size = get_dir_size(path)
    if size > DISK_LIMIT_BYTES:
        logger.error(f"Disk limit exceeded: {size} bytes in {path}")
        return False
    return True


class TimeoutException(Exception):
    """Raised when an operation exceeds the timeout limit."""
    pass


def with_timeout(seconds: int = 60):
    """
    Decorator to enforce a hard execution timeout.
    Note: Thread-based timeout to be compatible with Windows/MacOS/Linux.
    Ref: FR-002
    """
    def decorator(func):
        import threading
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            error = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    error[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)

            if thread.is_alive():
                raise TimeoutException(f"Operation timed out after {seconds} seconds.")

            if error[0] is not None:
                raise error[0]

            return result[0]
        return wrapper
    return decorator

