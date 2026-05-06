"""
ZIP Utility for packaging cloned websites.
Provides functionality to create downloadable ZIP archives.
"""

import os
import zipfile
from pathlib import Path
from typing import Optional
import tempfile
import shutil


def create_zip_archive(source_dir: str, output_path: Optional[str] = None) -> str:
    """
    Create a ZIP archive from a directory.

    Args:
        source_dir: Path to directory to zip
        output_path: Optional path for output ZIP file

    Returns:
        Path to created ZIP file
    """
    source_path = Path(source_dir)

    if not source_path.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    if not source_path.is_dir():
        raise NotADirectoryError(f"Source is not a directory: {source_dir}")

    # Generate output path if not provided
    if output_path is None:
        output_path = f"{source_dir}.zip"

    output_path = Path(output_path)

    # Create ZIP file
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_path):
            for file in files:
                file_path = Path(root) / file
                # Calculate relative path for archive
                arcname = file_path.relative_to(source_path.parent)
                zipf.write(file_path, arcname)

    return str(output_path)


def extract_zip_archive(zip_path: str, extract_to: str) -> str:
    """
    Extract a ZIP archive to a directory.

    Args:
        zip_path: Path to ZIP file
        extract_to: Directory to extract to

    Returns:
        Path to extraction directory
    """
    zip_file = Path(zip_path)

    if not zip_file.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    extract_path = Path(extract_to)
    extract_path.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_file, 'r') as zipf:
        zipf.extractall(extract_path)

    return str(extract_path)


def get_directory_size(path: str) -> int:
    """Get total size of directory in bytes."""
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


if __name__ == "__main__":
    # Test the module
    import sys
    if len(sys.argv) > 1:
        source = sys.argv[1]
        zip_path = create_zip_archive(source)
        print(f"Created: {zip_path}")
        print(f"Size: {format_size(os.path.getsize(zip_path))}")
