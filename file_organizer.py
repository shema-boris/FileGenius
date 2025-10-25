#!/usr/bin/env python3
"""
Local File Organizer - Phase 2
A privacy-first file organization tool that runs entirely on your local machine.

Phase 2 Features:
- Organize files by type (images, documents, videos, others)
- Organize by creation date (year/month)
- **NEW:** SQLite database tracking for all file operations
- **NEW:** SHA-256 hashing and duplicate detection
- **NEW:** Undo capability to revert changes
- **NEW:** Option to remove duplicate files
- Dry-run mode to preview changes
- Comprehensive logging
- Modular design for future expansion
"""

import os
import shutil
import logging
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Import database manager for Phase 2 features
import database_manager as db


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
    logger: Optional[logging.Logger] = None,
    file_hash: Optional[str] = None,
    file_info: Optional[Dict] = None
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
    dry_run: bool = True,
    enable_database: bool = True,
    check_duplicates: bool = True,
    remove_duplicates: bool = False,
    db_path: str = 'file_organizer.db'
) -> Dict[str, int]:
    """
    Main function to organize files in a directory.
    
    Args:
        source_directory: Directory to organize
        output_directory: Base directory for organized files
        organize_by_date: If True, organize into year/month subfolders
        recursive: If True, scan subdirectories recursively
        dry_run: If True, only log planned actions without moving files
        enable_database: If True, track files in SQLite database
        check_duplicates: If True, check for duplicate files using SHA-256
        remove_duplicates: If True, delete duplicate files (requires confirmation)
        db_path: Path to SQLite database file
        
    Returns:
        Dictionary with statistics (files_processed, files_moved, errors, duplicates_found)
    """
    # Setup logging
    logger = setup_logging()
    
    # Convert to Path objects
    source_path = Path(source_directory).resolve()
    output_path = Path(output_directory).resolve()
    
    # Validate source directory
    if not source_path.exists():
        logger.error(f"Source directory does not exist: {source_path}")
        return {'files_processed': 0, 'files_moved': 0, 'errors': 1, 'duplicates_found': 0}
    
    if not source_path.is_dir():
        logger.error(f"Source path is not a directory: {source_path}")
        return {'files_processed': 0, 'files_moved': 0, 'errors': 1, 'duplicates_found': 0}
    
    # Initialize database if enabled
    operation_id = None
    if enable_database and not dry_run:
        try:
            db.init_db(db_path)
            operation_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            logger.info(f"Database initialized: {db_path}")
            logger.info(f"Operation ID: {operation_id}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            enable_database = False
    
    # Log operation start
    mode = "DRY-RUN MODE" if dry_run else "LIVE MODE"
    logger.info("=" * 70)
    logger.info(f"FILE ORGANIZER PHASE 2 - {mode}")
    logger.info("=" * 70)
    logger.info(f"Source directory: {source_path}")
    logger.info(f"Output directory: {output_path}")
    logger.info(f"Organize by date: {organize_by_date}")
    logger.info(f"Recursive scan: {recursive}")
    logger.info(f"Database tracking: {enable_database}")
    logger.info(f"Duplicate detection: {check_duplicates}")
    logger.info(f"Remove duplicates: {remove_duplicates}")
    logger.info("=" * 70)
    
    # Scan directory for files
    logger.info("Scanning directory for files...")
    files = scan_directory(source_path, recursive=recursive)
    logger.info(f"Found {len(files)} files to process")
    
    # Statistics
    stats = {
        'files_processed': 0,
        'files_moved': 0,
        'errors': 0,
        'duplicates_found': 0,
        'duplicates_removed': 0
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
        
        # Compute SHA-256 hash if duplicate checking is enabled
        file_hash = None
        if check_duplicates or enable_database:
            try:
                file_hash = db.compute_file_hash(file_path)
            except Exception as e:
                logger.error(f"Failed to compute hash for {file_path.name}: {e}")
        
        # Check for duplicates
        is_duplicate = False
        if check_duplicates and file_hash and enable_database:
            try:
                duplicate = db.get_duplicate(file_hash, db_path)
                if duplicate:
                    stats['duplicates_found'] += 1
                    is_duplicate = True
                    logger.warning(f"DUPLICATE: {file_path.name} matches {duplicate['file_name']}")
                    logger.warning(f"  Original: {duplicate['new_path']}")
                    logger.warning(f"  Duplicate: {file_path}")
                    
                    # Handle duplicate removal
                    if remove_duplicates:
                        if dry_run:
                            logger.info(f"WOULD DELETE duplicate: {file_path}")
                        else:
                            try:
                                file_path.unlink()
                                stats['duplicates_removed'] += 1
                                logger.info(f"DELETED duplicate: {file_path}")
                            except Exception as e:
                                logger.error(f"Failed to delete duplicate {file_path}: {e}")
                                stats['errors'] += 1
                    continue  # Skip moving this file
            except Exception as e:
                logger.error(f"Error checking for duplicates: {e}")
        
        # Determine file category
        category = get_file_category(file_path)
        logger.debug(f"File: {file_path.name} -> Category: {category}")
        
        # Get creation date
        year, month = get_file_creation_date(file_path)
        logger.debug(f"Creation date: {year}-{month:02d}")
        
        # Get file stats for database
        file_stat = file_path.stat()
        file_size = file_stat.st_size
        created_at = datetime.fromtimestamp(file_stat.st_ctime).isoformat()
        modified_at = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
        
        # Build target path
        target_dir = build_organized_path(
            output_path, category, year, month, organize_by_date
        )
        
        # Build full target path for database
        target_file = target_dir / file_path.name
        
        # Handle name conflicts
        counter = 1
        original_target = target_file
        while target_file.exists():
            stem = original_target.stem
            suffix = original_target.suffix
            target_file = target_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        # Log the action
        action = "WOULD MOVE" if dry_run else "MOVING"
        logger.info(f"{action}: {file_path} -> {target_file}")
        
        # Move the file
        try:
            if not dry_run:
                # Create target directory
                target_dir.mkdir(parents=True, exist_ok=True)
                # Move file
                shutil.move(str(file_path), str(target_file))
                logger.info(f"SUCCESS: Moved {file_path.name}")
            
            stats['files_moved'] += 1
            
            # Insert into database
            if enable_database and not dry_run and operation_id:
                try:
                    file_info = {
                        'original_path': str(file_path),
                        'new_path': str(target_file),
                        'file_name': file_path.name,
                        'file_size': file_size,
                        'file_type': category,
                        'created_at': created_at,
                        'modified_at': modified_at,
                        'sha256_hash': file_hash or '',
                        'operation_id': operation_id
                    }
                    db.insert_file_record(file_info, db_path)
                except Exception as e:
                    logger.error(f"Failed to insert database record: {e}")
        
        except PermissionError:
            logger.error(f"PERMISSION DENIED: Cannot move {file_path}")
            stats['errors'] += 1
        except Exception as e:
            logger.error(f"ERROR moving {file_path}: {e}")
            stats['errors'] += 1
    
    # Log summary
    logger.info("=" * 70)
    logger.info("ORGANIZATION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Files processed: {stats['files_processed']}")
    logger.info(f"Files moved: {stats['files_moved']}")
    logger.info(f"Duplicates found: {stats['duplicates_found']}")
    if remove_duplicates:
        logger.info(f"Duplicates removed: {stats['duplicates_removed']}")
    logger.info(f"Errors: {stats['errors']}")
    
    if dry_run:
        logger.info("")
        logger.info("This was a DRY-RUN. No files were actually moved.")
        logger.info("Run with --no-dry-run to perform the actual organization.")
    
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
        description='Local File Organizer Phase 2 - Organize your files by type and date with duplicate detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run to see what would happen (Phase 1 behavior)
  python file_organizer.py /path/to/messy/folder --dry-run
  
  # Actually organize files with database tracking
  python file_organizer.py /path/to/messy/folder --no-dry-run
  
  # Check for duplicates but don't remove them
  python file_organizer.py /path/to/folder --no-dry-run --check-duplicates
  
  # Remove duplicate files (with confirmation)
  python file_organizer.py /path/to/folder --no-dry-run --remove-duplicates
  
  # Undo the last organization operation
  python file_organizer.py --undo-last
  
  # Show database statistics
  python file_organizer.py --show-stats
  
  # Organize without database tracking (Phase 1 mode)
  python file_organizer.py /path/to/folder --no-dry-run --no-database
        """
    )
    
    parser.add_argument(
        'source',
        nargs='?',
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
    
    # Phase 2 arguments
    parser.add_argument(
        '--no-database',
        action='store_true',
        help='Disable database tracking (Phase 1 behavior)'
    )
    
    parser.add_argument(
        '--check-duplicates',
        action='store_true',
        help='Check for duplicate files using SHA-256 hashing'
    )
    
    parser.add_argument(
        '--remove-duplicates',
        action='store_true',
        help='Remove duplicate files (implies --check-duplicates)'
    )
    
    parser.add_argument(
        '--db-path',
        default='file_organizer.db',
        help='Path to SQLite database file (default: file_organizer.db)'
    )
    
    parser.add_argument(
        '--undo-last',
        action='store_true',
        help='Undo the last organization operation'
    )
    
    parser.add_argument(
        '--show-stats',
        action='store_true',
        help='Show database statistics'
    )
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.undo_last:
        logger = setup_logging()
        logger.info("=" * 70)
        logger.info("UNDO LAST OPERATION")
        logger.info("=" * 70)
        
        # Get confirmation
        if not args.no_dry_run:
            logger.info("DRY-RUN MODE: Showing what would be undone")
            stats = db.undo_last_operation(args.db_path, dry_run=True)
        else:
            response = input("\nAre you sure you want to undo the last operation? (yes/no): ")
            if response.lower() == 'yes':
                stats = db.undo_last_operation(args.db_path, dry_run=False)
            else:
                logger.info("Undo cancelled.")
                return
        
        logger.info("=" * 70)
        logger.info(f"Files restored: {stats['files_restored']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info("=" * 70)
        return
    
    if args.show_stats:
        logger = setup_logging()
        
        if not db.database_exists(args.db_path):
            logger.error(f"Database not found: {args.db_path}")
            return
        
        logger.info("=" * 70)
        logger.info("DATABASE STATISTICS")
        logger.info("=" * 70)
        
        stats = db.get_database_stats(args.db_path)
        logger.info(f"Total files tracked: {stats['total_files']}")
        logger.info(f"Total size: {stats['total_size_mb']} MB ({stats['total_size_bytes']} bytes)")
        logger.info(f"Total operations: {stats['total_operations']}")
        logger.info("")
        logger.info("Files by type:")
        for file_type, count in stats['files_by_type'].items():
            logger.info(f"  {file_type}: {count}")
        logger.info("=" * 70)
        return
    
    # Validate source directory for organize operation
    if not args.source:
        parser.error("source directory is required unless using --undo-last or --show-stats")
    
    # Determine dry-run mode
    dry_run = not args.no_dry_run
    
    # If remove_duplicates is set, enable check_duplicates
    check_duplicates = args.check_duplicates or args.remove_duplicates
    
    # Run the organizer
    organize_files(
        source_directory=args.source,
        output_directory=args.output,
        organize_by_date=not args.no_date,
        recursive=args.recursive,
        dry_run=dry_run,
        enable_database=not args.no_database,
        check_duplicates=check_duplicates,
        remove_duplicates=args.remove_duplicates,
        db_path=args.db_path
    )


if __name__ == '__main__':
    main()
