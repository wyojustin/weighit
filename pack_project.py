import os
from pathlib import Path

# --- CONFIGURATION ---
OUTPUT_FILENAME = "full_project_context.txt"
INCLUDED_EXTENSIONS = {".py", ".css"}
EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__", 
    ".pytest_cache", "build", "dist", ".mypy_cache", "egg-info"
}

def main():
    root_dir = Path.cwd()
    output_path = root_dir / OUTPUT_FILENAME
    
    print(f"Scanning: {root_dir}")
    print(f"Looking for: {INCLUDED_EXTENSIONS}")
    
    found_files = []

    # 1. Walk through directory
    for path in root_dir.rglob("*"):
        # Skip directories
        if not path.is_file():
            continue
            
        # Check extension
        if path.suffix not in INCLUDED_EXTENSIONS:
            continue
            
        # Check against excluded folders
        # (e.g. checks if '.venv' is anywhere in the path parts)
        if not set(path.parts).isdisjoint(EXCLUDED_DIRS):
            continue
            
        # Don't include this script itself or the output file
        if path.name == "pack_project.py" or path.name == OUTPUT_FILENAME:
            continue
            
        found_files.append(path)

    # Sort for consistent order
    found_files.sort()

    # 2. Write to single file
    with open(output_path, "w", encoding="utf-8") as outfile:
        for file_path in found_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                
                # Create a clear header
                header = (
                    f"\n{'='*80}\n"
                    f"# FILE PATH: {file_path}\n"
                    f"{'='*80}\n"
                )
                
                outfile.write(header)
                outfile.write(content)
                outfile.write("\n") # Extra newline between files
                
                print(f"Packed: {file_path}")
                
            except Exception as e:
                print(f"FAILED to read {file_path}: {e}")

    print("-" * 40)
    print(f"Success! All files written to: {OUTPUT_FILENAME}")

if __name__ == "__main__":
    main()
