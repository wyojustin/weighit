import os
from pathlib import Path

def print_project_files():
    """
    Recursively finds all .py files in the current directory,
    skipping virtual environments and cache folders, and prints
    their contents with clear delimiters.
    """
    # The directory where this script is running
    root_dir = Path.cwd()

    # Directories to exclude to avoid huge output dump
    EXCLUDE_DIRS = {
        '.venv', 'venv', 'env', '.git', 
        '__pycache__', '.pytest_cache', 
        'build', 'dist', 'egg-info'
    }

    # Gather files
    py_files = []
    for path in root_dir.rglob('*.py'):
        # Skip if the file is inside an excluded directory
        # path.parts splits the path (e.g., /home/user/project/venv/lib...)
        if not set(path.parts).intersection(EXCLUDE_DIRS):
            # Don't print this script itself
            if path.name != Path(__file__).name:
                py_files.append(path)

    # Sort alphabetically for easier reading
    py_files.sort()

    for file_path in py_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # --- The Formatting ---
            print("\n" + "="*80)
            print(f"# FILE PATH: {file_path.absolute()}")
            print("="*80)
            print(content)
            print("\n")
            
        except Exception as e:
            print(f"# ERROR READING {file_path.name}: {e}")

if __name__ == "__main__":
    print_project_files()
