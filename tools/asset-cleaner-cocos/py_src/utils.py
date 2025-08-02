# py_src/utils.py - Utility functions for byte conversion

def byte_to_mb_str(byte_size: int) -> str:
    """Converts bytes to a formatted MB string."""
    mb = byte_size / (1024 * 1024)
    return f"{mb:.4f}"

def byte_to_kb_str(byte_size: int) -> str:
    """Converts bytes to a formatted KB string."""
    kb = byte_size / 1024
    return f"{kb:.2f}"