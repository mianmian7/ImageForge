# py_src/file_helper.py - Helper functions for file operations
import os
import json

def get_full_path(file_path: str) -> str:
    """Returns the absolute path of a file."""
    if not os.path.isabs(file_path):
        # In Python, it's often better to resolve paths relative to the current working directory
        # or a specified base directory, rather than the script's location.
        return os.path.abspath(file_path)
    return file_path

def write_file(full_path: str, content: str):
    """Writes content to a file."""
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Success to write file: {full_path}")
    except IOError as e:
        print(f"Error writing file {full_path}: {e}")

def get_object_from_file(full_path: str) -> dict:
    """Reads a JSON file and returns a dictionary."""
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {full_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {full_path}")
        return {}
    except IOError as e:
        print(f"Error reading file {full_path}: {e}")
        return {}

def get_file_string(full_path: str) -> str:
    """Reads a file and returns its content as a string."""
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {full_path}")
        return ""
    except IOError as e:
        print(f"Error reading file {full_path}: {e}")
        return ""