#!/usr/bin/env python3
"""
Database Manager for Local File Organizer
Handles all SQLite operations for tracking file organization history.

This module provides:
- Metadata storage for all processed files
- SHA-256 hash computation and storage
- Duplicate detection
- Undo/rollback capability
- Query functions for file history

All operations use Python's built-in sqlite3 module.
"""

import sqlite3
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DEFAULT_DB_PATH = "file_organizer.db"

# SQL Schema
CREATE_FILES_TABLE = """
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_path TEXT NOT NULL,
    new_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    created_at TEXT,
    modified_at TEXT,
    sha256_hash TEXT NOT NULL,
    operation_date TEXT NOT NULL,
    operation_id TEXT NOT NULL
);
"""

# Create index on sha256_hash for faster duplicate lookups
CREATE_HASH_INDEX = """
CREATE INDEX IF NOT EXISTS idx_sha256_hash ON files(sha256_hash);
"""

# Create index on operation_id for faster undo operations
CREATE_OPERATION_INDEX = """
CREATE INDEX IF NOT EXISTS idx_operation_id ON files(operation_id);
"""


# ============================================================================
# DATABASE CONNECTION CONTEXT MANAGER
# ============================================================================

@contextmanager
def get_db_connection(db_path: str = DEFAULT_DB_PATH):
    """
    Context manager for database connections.
    Ensures proper connection handling and automatic commit/rollback.
    
    Args:
        db_path: Path to the SQLite database file
        
    Yields:
        sqlite3.Connection object
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like row access
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logging.getLogger('FileOrganizer').error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Create the SQLite database and tables if they don't exist.
    Also creates necessary indexes for performance.
    
    Args:
        db_path: Path to the SQLite database file
        
    Example:
        >>> init_db("my_organizer.db")
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute(CREATE_FILES_TABLE)
            logger.info(f"Database initialized: {db_path}")
            
            # Create indexes
            cursor.execute(CREATE_HASH_INDEX)
            cursor.execute(CREATE_OPERATION_INDEX)
            logger.debug("Database indexes created")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


# ============================================================================
# SHA-256 HASHING
# ============================================================================

def compute_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """
    Compute SHA-256 hash of a file.
    Reads file in chunks to handle large files efficiently.
    
    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read (default: 8KB)
        
    Returns:
        SHA-256 hash as hexadecimal string
        
    Example:
        >>> hash_val = compute_file_hash(Path("photo.jpg"))
        >>> print(hash_val)  # e.g., "a3b2c1d4e5f6..."
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            # Read file in chunks to avoid memory issues with large files
            while chunk := f.read(chunk_size):
                sha256_hash.update(chunk)
        
        hash_value = sha256_hash.hexdigest()
        logger.debug(f"Computed hash for {file_path.name}: {hash_value[:16]}...")
        return hash_value
        
    except Exception as e:
        logger.error(f"Failed to compute hash for {file_path}: {e}")
        raise


# ============================================================================
# FILE RECORD OPERATIONS
# ============================================================================

def insert_file_record(
    file_info: Dict[str, Any],
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Insert metadata for a single file into the database.
    
    Args:
        file_info: Dictionary with file metadata:
            - original_path: str
            - new_path: str
            - file_name: str
            - file_size: int
            - file_type: str
            - created_at: str (ISO format timestamp)
            - modified_at: str (ISO format timestamp)
            - sha256_hash: str
            - operation_id: str (unique ID for this organization run)
        db_path: Path to the SQLite database file
        
    Returns:
        ID of the inserted record
        
    Example:
        >>> file_info = {
        ...     'original_path': '/home/user/Downloads/photo.jpg',
        ...     'new_path': '/home/user/organized/images/2024/10/photo.jpg',
        ...     'file_name': 'photo.jpg',
        ...     'file_size': 1024000,
        ...     'file_type': 'images',
        ...     'created_at': '2024-10-25T12:00:00',
        ...     'modified_at': '2024-10-25T12:30:00',
        ...     'sha256_hash': 'a3b2c1d4...',
        ...     'operation_id': 'run_20241025_120000'
        ... }
        >>> record_id = insert_file_record(file_info)
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        # Add operation timestamp
        operation_date = datetime.now().isoformat()
        
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO files (
                    original_path, new_path, file_name, file_size,
                    file_type, created_at, modified_at, sha256_hash,
                    operation_date, operation_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_info['original_path'],
                file_info['new_path'],
                file_info['file_name'],
                file_info['file_size'],
                file_info['file_type'],
                file_info['created_at'],
                file_info['modified_at'],
                file_info['sha256_hash'],
                operation_date,
                file_info['operation_id']
            ))
            
            record_id = cursor.lastrowid
            logger.debug(f"Inserted record {record_id} for {file_info['file_name']}")
            return record_id
            
    except Exception as e:
        logger.error(f"Failed to insert file record: {e}")
        raise


# ============================================================================
# DUPLICATE DETECTION
# ============================================================================

def get_duplicate(
    hash_value: str,
    db_path: str = DEFAULT_DB_PATH
) -> Optional[Dict[str, Any]]:
    """
    Check if a file with the same SHA-256 hash already exists in the database.
    
    Args:
        hash_value: SHA-256 hash to search for
        db_path: Path to the SQLite database file
        
    Returns:
        Dictionary with file metadata if duplicate found, None otherwise
        
    Example:
        >>> duplicate = get_duplicate("a3b2c1d4e5f6...")
        >>> if duplicate:
        ...     print(f"Duplicate found: {duplicate['file_name']}")
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM files
                WHERE sha256_hash = ?
                ORDER BY operation_date DESC
                LIMIT 1
            """, (hash_value,))
            
            row = cursor.fetchone()
            
            if row:
                duplicate = dict(row)
                logger.debug(f"Duplicate found: {duplicate['file_name']}")
                return duplicate
            
            return None
            
    except Exception as e:
        logger.error(f"Failed to check for duplicate: {e}")
        raise


def get_all_duplicates(db_path: str = DEFAULT_DB_PATH) -> List[List[Dict[str, Any]]]:
    """
    Find all groups of duplicate files in the database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        List of duplicate groups, where each group is a list of file records
        with the same hash
        
    Example:
        >>> duplicates = get_all_duplicates()
        >>> for group in duplicates:
        ...     print(f"Found {len(group)} duplicates:")
        ...     for file in group:
        ...         print(f"  - {file['new_path']}")
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Find hashes that appear more than once
            cursor.execute("""
                SELECT sha256_hash, COUNT(*) as count
                FROM files
                GROUP BY sha256_hash
                HAVING count > 1
            """)
            
            duplicate_hashes = cursor.fetchall()
            
            duplicate_groups = []
            for row in duplicate_hashes:
                hash_value = row['sha256_hash']
                
                # Get all files with this hash
                cursor.execute("""
                    SELECT * FROM files
                    WHERE sha256_hash = ?
                    ORDER BY operation_date ASC
                """, (hash_value,))
                
                group = [dict(r) for r in cursor.fetchall()]
                duplicate_groups.append(group)
            
            logger.info(f"Found {len(duplicate_groups)} duplicate groups")
            return duplicate_groups
            
    except Exception as e:
        logger.error(f"Failed to get duplicates: {e}")
        raise


# ============================================================================
# UNDO OPERATIONS
# ============================================================================

def get_last_operation_id(db_path: str = DEFAULT_DB_PATH) -> Optional[str]:
    """
    Get the operation ID of the most recent organization run.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Operation ID string, or None if no operations found
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT operation_id FROM files
                ORDER BY operation_date DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            return row['operation_id'] if row else None
            
    except Exception as e:
        logger.error(f"Failed to get last operation ID: {e}")
        raise


def get_operation_files(
    operation_id: str,
    db_path: str = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """
    Retrieve all files from a specific organization operation.
    
    Args:
        operation_id: Unique identifier for the operation
        db_path: Path to the SQLite database file
        
    Returns:
        List of file record dictionaries
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM files
                WHERE operation_id = ?
                ORDER BY operation_date ASC
            """, (operation_id,))
            
            files = [dict(row) for row in cursor.fetchall()]
            logger.info(f"Found {len(files)} files for operation {operation_id}")
            return files
            
    except Exception as e:
        logger.error(f"Failed to get operation files: {e}")
        raise


def undo_operation(
    operation_id: str,
    db_path: str = DEFAULT_DB_PATH,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Undo a specific organization operation by moving files back to their
    original locations and removing their records from the database.
    
    Args:
        operation_id: Unique identifier for the operation to undo
        db_path: Path to the SQLite database file
        dry_run: If True, only log what would be done without actually doing it
        
    Returns:
        Dictionary with statistics (files_restored, errors)
        
    Example:
        >>> stats = undo_operation("run_20241025_120000", dry_run=True)
        >>> print(f"Would restore {stats['files_restored']} files")
    """
    import shutil
    
    logger = logging.getLogger('FileOrganizer')
    
    stats = {
        'files_restored': 0,
        'errors': 0
    }
    
    try:
        # Get all files from this operation
        files = get_operation_files(operation_id, db_path)
        
        if not files:
            logger.warning(f"No files found for operation {operation_id}")
            return stats
        
        logger.info(f"{'DRY-RUN: Would undo' if dry_run else 'Undoing'} operation {operation_id}")
        logger.info(f"Found {len(files)} files to restore")
        
        restored_ids = []
        
        for file_record in files:
            original_path = Path(file_record['original_path'])
            new_path = Path(file_record['new_path'])
            
            try:
                # Check if file exists at new location
                if not new_path.exists():
                    logger.warning(f"File not found at new location: {new_path}")
                    stats['errors'] += 1
                    continue
                
                # Check if original location is occupied
                if original_path.exists():
                    logger.warning(f"Original location occupied: {original_path}")
                    stats['errors'] += 1
                    continue
                
                action = "WOULD RESTORE" if dry_run else "RESTORING"
                logger.info(f"{action}: {new_path} -> {original_path}")
                
                if not dry_run:
                    # Create parent directory if needed
                    original_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file back
                    shutil.move(str(new_path), str(original_path))
                    logger.info(f"SUCCESS: Restored {file_record['file_name']}")
                    restored_ids.append(file_record['id'])
                
                stats['files_restored'] += 1
                
            except Exception as e:
                logger.error(f"Error restoring {file_record['file_name']}: {e}")
                stats['errors'] += 1
        
        # Remove records from database (only in live mode)
        if not dry_run and restored_ids:
            with get_db_connection(db_path) as conn:
                cursor = conn.cursor()
                placeholders = ','.join('?' * len(restored_ids))
                cursor.execute(f"""
                    DELETE FROM files
                    WHERE id IN ({placeholders})
                """, restored_ids)
                logger.info(f"Removed {len(restored_ids)} records from database")
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to undo operation: {e}")
        raise


def undo_last_operation(
    db_path: str = DEFAULT_DB_PATH,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Undo the most recent organization operation.
    Convenience wrapper around undo_operation().
    
    Args:
        db_path: Path to the SQLite database file
        dry_run: If True, only log what would be done
        
    Returns:
        Dictionary with statistics (files_restored, errors)
        
    Example:
        >>> stats = undo_last_operation(dry_run=False)
        >>> print(f"Restored {stats['files_restored']} files")
    """
    logger = logging.getLogger('FileOrganizer')
    
    # Get the last operation ID
    operation_id = get_last_operation_id(db_path)
    
    if not operation_id:
        logger.warning("No operations found in database")
        return {'files_restored': 0, 'errors': 0}
    
    logger.info(f"Last operation ID: {operation_id}")
    
    # Undo that operation
    return undo_operation(operation_id, db_path, dry_run)


# ============================================================================
# QUERY & STATISTICS FUNCTIONS
# ============================================================================

def get_database_stats(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """
    Get statistics about the database.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        Dictionary with database statistics
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Total files
            cursor.execute("SELECT COUNT(*) as count FROM files")
            total_files = cursor.fetchone()['count']
            
            # Total size
            cursor.execute("SELECT SUM(file_size) as total FROM files")
            total_size = cursor.fetchone()['total'] or 0
            
            # Files by type
            cursor.execute("""
                SELECT file_type, COUNT(*) as count
                FROM files
                GROUP BY file_type
                ORDER BY count DESC
            """)
            files_by_type = {row['file_type']: row['count'] for row in cursor.fetchall()}
            
            # Number of operations
            cursor.execute("SELECT COUNT(DISTINCT operation_id) as count FROM files")
            total_operations = cursor.fetchone()['count']
            
            stats = {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'files_by_type': files_by_type,
                'total_operations': total_operations
            }
            
            return stats
            
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        raise


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def database_exists(db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Check if the database file exists.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        True if database file exists, False otherwise
    """
    return Path(db_path).exists()
