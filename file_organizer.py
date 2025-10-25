#!/usr/bin/env python3
"""
Local File Organizer - Phase 1
A privacy-first file organization tool that runs entirely on your local machine.

Features:
- Organize files by type (images, documents, videos, others)
- Organize by creation date (year/month)
- Dry-run mode to preview changes
- Comprehensive logging
- Modular design for future expansion
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


# ============================================================================
# CONFIGURATION
# ============================================================================

# File type mappings - easily extensible for future phases
FILE_CATEGORIES = {
    'images': {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', 
        '.ico', '.tiff', '.tif', '.heic', '.heif', '.raw'
    },
    'documents': {
        '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', 
        '.xlsx', '.ppt', '.pptx', '.csv', '.md', '.tex'
    },
    'videos': {
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', 
        '.m4v', '.mpg', '.mpeg', '.3gp'
    },
    'audio': {
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', 
        '.opus', '.aiff'
    },
    'archives': {
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', 
        '.tar.gz', '.tgz'
    },
    'code': {
        '.py', '.js', '.java', '.cpp', '.c', '.h', '.cs', '.php', 
        '.rb', '.go', '.rs', '.swift', '.kt', '.ts', '.html', 
        '.css', '.scss', '.json', '.xml', '.yaml', '.yml'
    },
    'executables': {
        '.exe', '.msi', '.app', '.dmg', '.deb', '.rpm', '.apk'
    }
}

# Default folder for uncategorized files
DEFAULT_CATEGORY = 'others'

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_file: str = 'file_organizer.log', log_level: int = logging.INFO):
    """
    Configure logging to write to both file and console.
    
    Args:
        log_file: Name of the log file
        log_level: Logging level (default: INFO)
    """
    # Create logger
    logger = logging.getLogger('FileOrganizer')
    logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# ============================================================================
# FILE ANALYSIS FUNCTIONS
# ============================================================================

def get_file_category(file_path: Path) -> str:
    """
    Determine the category of a file based on its extension.
    
    Args:
        file_path: Path object of the file
        
    Returns:
        Category name as string (e.g., 'images', 'documents', 'others')
    """
    extension = file_path.suffix.lower()
    
    # Check each category for the extension
    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category
    
    # Return default category if no match found
    return DEFAULT_CATEGORY


def get_file_creation_date(file_path: Path) -> Tuple[int, int]:
    """
    Get the creation date of a file and return year and month.
    
    Args:
        file_path: Path object of the file
        
    Returns:
        Tuple of (year, month) as integers
    """
    try:
        # Try to get creation time (Windows) or change time (Unix)
        if os.name == 'nt':  # Windows
            timestamp = os.path.getctime(file_path)
        else:  # Unix-like systems
            stat = os.stat(file_path)
            # Use birth time if available, otherwise modification time
            timestamp = getattr(stat, 'st_birthtime', stat.st_mtime)
        
        creation_date = datetime.fromtimestamp(timestamp)
        return creation_date.year, creation_date.month
    
    except Exception as e:
        # If we can't get creation date, use current date
        current_date = datetime.now()
        return current_date.year, current_date.month


def scan_directory(directory: Path, recursive: bool = False) -> List[Path]:
    """
    Scan a directory and return a list of all files (excluding directories).
    
    Args:
        directory: Path object of the directory to scan
        recursive: If True, scan subdirectories recursively
        
    Returns:
        List of Path objects for all files found
    """
    files = []
    
    try:
        if recursive:
            # Recursively find all files
            for item in directory.rglob('*'):
                if item.is_file():
                    files.append(item)
        else:
            # Only scan the top-level directory
            for item in directory.iterdir():
                if item.is_file():
                    files.append(item)
    
    except PermissionError as e:
        logging.getLogger('FileOrganizer').error(f"Permission denied: {directory}")
    except Exception as e:
        logging.getLogger('FileOrganizer').error(f"Error scanning directory {directory}: {e}")
    
    return files


# ============================================================================
# FILE ORGANIZATION FUNCTIONS
# ============================================================================

def build_organized_path(
    base_output_dir: Path,
    category: str,
    year: int,
    month: int,
    organize_by_date: bool = True
) -> Path:
    """
    Build the target path for an organized file.
    
    Args:
        base_output_dir: Base directory for organized files
        category: File category (e.g., 'images', 'documents')
        year: Creation year
        month: Creation month
        organize_by_date: If True, organize into year/month subfolders
        
    Returns:
        Path object for the target directory
    """
    if organize_by_date:
        # Create path: organized/category/year/month/
        target_dir = base_output_dir / category / str(year) / f"{month:02d}"
    else:
        # Create path: organized/category/
        target_dir = base_output_dir / category
    
    return target_dir


def move_file(
    source: Path,
    target_dir: Path,
    dry_run: bool = True,
    logger: Optional[logging.Logger] = None
) -> bool:
    """
    Move a file to the target directory, handling name conflicts.
    
    Args:
        source: Source file path
        target_dir: Target directory path
        dry_run: If True, only log the action without moving
        logger: Logger instance for logging actions
        
    Returns:
        True if successful (or would be successful in dry-run), False otherwise
    """
    if logger is None:
        logger = logging.getLogger('FileOrganizer')
    
    try:
        # Create target directory if it doesn't exist (even in dry-run for validation)
        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
        
        # Build target file path
        target_file = target_dir / source.name
        
        # Handle name conflicts by appending a number
        counter = 1
        original_target = target_file
        while target_file.exists():
            stem = original_target.stem
            suffix = original_target.suffix
            target_file = target_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        # Log the action
        action = "WOULD MOVE" if dry_run else "MOVING"
        logger.info(f"{action}: {source} -> {target_file}")
        
        # Perform the move if not in dry-run mode
        if not dry_run:
            shutil.move(str(source), str(target_file))
            logger.info(f"SUCCESS: Moved {source.name}")
        
        return True
    
    except PermissionError:
        logger.error(f"PERMISSION DENIED: Cannot move {source}")
        return False
    except Exception as e:
        logger.error(f"ERROR moving {source}: {e}")
        return False


# ============================================================================
# MAIN ORGANIZATION LOGIC
# ============================================================================

def organize_files(
    source_directory: str,
    output_directory: str = 'organized',
    organize_by_date: bool = True,
    recursive: bool = False,
    dry_run: bool = True
) -> Dict[str, int]:
    """
    Main function to organize files in a directory.
    
    Args:
        source_directory: Directory to organize
        output_directory: Base directory for organized files
        organize_by_date: If True, organize into year/month subfolders
        recursive: If True, scan subdirectories recursively
        dry_run: If True, only log planned actions without moving files
        
    Returns:
        Dictionary with statistics (files_processed, files_moved, errors)
    """
    # Setup logging
    logger = setup_logging()
    
    # Convert to Path objects
    source_path = Path(source_directory).resolve()
    output_path = Path(output_directory).resolve()
    
    # Validate source directory
    if not source_path.exists():
        logger.error(f"Source directory does not exist: {source_path}")
        return {'files_processed': 0, 'files_moved': 0, 'errors': 1}
    
    if not source_path.is_dir():
        logger.error(f"Source path is not a directory: {source_path}")
        return {'files_processed': 0, 'files_moved': 0, 'errors': 1}
    
    # Log operation start
    mode = "DRY-RUN MODE" if dry_run else "LIVE MODE"
    logger.info("=" * 70)
    logger.info(f"FILE ORGANIZER - {mode}")
    logger.info("=" * 70)
    logger.info(f"Source directory: {source_path}")
    logger.info(f"Output directory: {output_path}")
    logger.info(f"Organize by date: {organize_by_date}")
    logger.info(f"Recursive scan: {recursive}")
    logger.info("=" * 70)
    
    # Scan directory for files
    logger.info("Scanning directory for files...")
    files = scan_directory(source_path, recursive=recursive)
    logger.info(f"Found {len(files)} files to process")
    
    # Statistics
    stats = {
        'files_processed': 0,
        'files_moved': 0,
        'errors': 0
    }
    
    # Process each file
    for file_path in files:
        stats['files_processed'] += 1
        
        # Skip if file is in the output directory (avoid moving organized files)
        try:
            if output_path in file_path.parents or file_path.parent == output_path:
                logger.info(f"SKIPPING: {file_path.name} (already in output directory)")
                continue
        except Exception:
            pass
        
        # Determine file category
        category = get_file_category(file_path)
        logger.debug(f"File: {file_path.name} -> Category: {category}")
        
        # Get creation date
        year, month = get_file_creation_date(file_path)
        logger.debug(f"Creation date: {year}-{month:02d}")
        
        # Build target path
        target_dir = build_organized_path(
            output_path, category, year, month, organize_by_date
        )
        
        # Move the file
        success = move_file(file_path, target_dir, dry_run=dry_run, logger=logger)
        
        if success:
            stats['files_moved'] += 1
        else:
            stats['errors'] += 1
    
    # Log summary
    logger.info("=" * 70)
    logger.info("ORGANIZATION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Files processed: {stats['files_processed']}")
    logger.info(f"Files moved: {stats['files_moved']}")
    logger.info(f"Errors: {stats['errors']}")
    
    if dry_run:
        logger.info("")
        logger.info("This was a DRY-RUN. No files were actually moved.")
        logger.info("Run with dry_run=False to perform the actual organization.")
    
    logger.info("=" * 70)
    
    return stats


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

def main():
    """
    Main entry point for command-line usage.
    Demonstrates how to use the file organizer.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Local File Organizer - Organize your files by type and date',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run to see what would happen
  python file_organizer.py /path/to/messy/folder --dry-run
  
  # Actually organize files
  python file_organizer.py /path/to/messy/folder --no-dry-run
  
  # Organize without date subfolders
  python file_organizer.py /path/to/folder --no-dry-run --no-date
  
  # Recursive scan including subdirectories
  python file_organizer.py /path/to/folder --recursive --dry-run
        """
    )
    
    parser.add_argument(
        'source',
        help='Source directory to organize'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='organized',
        help='Output directory for organized files (default: organized)'
    )
    
    parser.add_argument(
        '--no-date',
        action='store_true',
        help='Do not organize files by date (only by category)'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively scan subdirectories'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Preview changes without moving files (default: True)'
    )
    
    parser.add_argument(
        '--no-dry-run',
        action='store_true',
        help='Actually move files (overrides --dry-run)'
    )
    
    args = parser.parse_args()
    
    # Determine dry-run mode
    dry_run = not args.no_dry_run
    
    # Run the organizer
    organize_files(
        source_directory=args.source,
        output_directory=args.output,
        organize_by_date=not args.no_date,
        recursive=args.recursive,
        dry_run=dry_run
    )


if __name__ == '__main__':
    main()
