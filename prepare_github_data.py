import os
from pathlib import Path
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Finds all relevant files in the GitHub repository directory, extracts their content,
    and saves the cleaned data to a single JSON file.
    """
    repo_path = Path('data/erigon')
    output_file = Path('github_cleaned.json')
    all_files = []

    if not repo_path.is_dir():
        logger.error(f"GitHub repository directory not found: {repo_path}")
        return

    logger.info(f"Searching for files in '{repo_path}' and its subdirectories...")
    
    # File types to include for Erigon
    file_globs = ["**/*.md", "**/*.txt", "**/*.go", "**/*.sh", "**/*.toml", "**/*.proto"]
    
    # Directories to exclude
    excluded_dirs = [str(repo_path / 'build'), str(repo_path / 'testdata')]

    for g in file_globs:
        for file_path in repo_path.rglob(g):
            if any(Path(file_path).is_relative_to(excluded_dir) for excluded_dir in excluded_dirs):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                all_files.append({
                    'source': str(file_path),
                    'content': content,
                })
            except Exception as e:
                logger.error(f"Could not read file {file_path}: {e}")

    logger.info(f"Total files parsed: {len(all_files)}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_files, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully saved all file contents to {output_file}")
    except Exception as e:
        logger.error(f"Could not write to output file {output_file}: {e}")

if __name__ == '__main__':
    main()
