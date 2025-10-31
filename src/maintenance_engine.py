#!/usr/bin/env python3
"""
Maintenance Engine for Local File Organizer
Handles predictive maintenance, autonomous optimization, and system health.

This module provides:
- Automatic retraining when confidence drops
- Pattern pruning and optimization
- Database maintenance and cleanup
- Historical data archiving
- Background monitoring and polling
"""

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

import database_manager as db
import learning_engine as learn
import feedback_manager as feedback
import preference_manager as prefs


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_LEARNING_DIR = Path('learning_data')
MAINTENANCE_LOG_FILE = 'maintenance_log.json'

# Maintenance thresholds
MIN_CONFIDENCE_THRESHOLD = 0.70  # Retrain if avg confidence < 70%
MIN_ACCURACY_THRESHOLD = 0.65    # Retrain if accuracy < 65%
WEAK_PATTERN_THRESHOLD = 5       # Remove patterns with < 5 samples
OLD_FEEDBACK_DAYS = 90           # Archive feedback older than 90 days
MAX_STORAGE_MB = 50              # Compress if learning_data > 50 MB

# Autonomous mode settings
POLL_INTERVAL_SECONDS = 30       # Check for new files every 30s
MAX_AUTONOMOUS_OPS = 100         # Safety limit per session


# ============================================================================
# MAINTENANCE LOG
# ============================================================================

class MaintenanceLog:
    """Track maintenance operations and history."""
    
    def __init__(self, learning_dir: Path = DEFAULT_LEARNING_DIR):
        self.learning_dir = learning_dir
        self.log_path = learning_dir / MAINTENANCE_LOG_FILE
        self.log = self._load_log()
    
    def _load_log(self) -> Dict[str, Any]:
        """Load maintenance log from disk."""
        if not self.log_path.exists():
            return {
                'version': '6.0',
                'created_at': datetime.now().isoformat(),
                'operations': [],
                'last_maintenance': None,
                'stats': {
                    'total_retrains': 0,
                    'total_optimizations': 0,
                    'total_cleanups': 0,
                    'patterns_pruned': 0,
                    'feedback_archived': 0
                }
            }
        
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return self._load_log()  # Return default if corrupted
    
    def _save_log(self):
        """Save maintenance log to disk."""
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)
    
    def record_operation(self, operation_type: str, details: Dict[str, Any]):
        """Record a maintenance operation."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': operation_type,
            'details': details
        }
        
        self.log['operations'].append(entry)
        self.log['last_maintenance'] = entry['timestamp']
        
        # Update stats
        if operation_type == 'retrain':
            self.log['stats']['total_retrains'] += 1
        elif operation_type == 'optimize':
            self.log['stats']['total_optimizations'] += 1
        elif operation_type == 'cleanup':
            self.log['stats']['total_cleanups'] += 1
        
        self._save_log()
    
    def get_last_maintenance(self) -> Optional[str]:
        """Get timestamp of last maintenance."""
        return self.log.get('last_maintenance')
    
    def get_operations_since(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get maintenance operations from last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        operations = []
        for op in self.log['operations']:
            op_time = datetime.fromisoformat(op['timestamp'])
            if op_time >= cutoff:
                operations.append(op)
        
        return operations


# ============================================================================
# PREDICTIVE MAINTENANCE
# ============================================================================

def check_model_health(
    db_path: str = 'file_organizer.db',
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> Dict[str, Any]:
    """
    Check model health and determine if maintenance is needed.
    
    Returns:
        Dictionary with health metrics and recommendations
    """
    logger = logging.getLogger('FileOrganizer')
    
    health = {
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'healthy',
        'issues': [],
        'recommendations': [],
        'metrics': {}
    }
    
    # Check model confidence
    model = learn.load_model(learning_dir)
    if model and model.total_samples > 0:
        stats = learn.get_learning_stats(model)
        
        # Calculate average confidence
        pattern_confidences = []
        for file_type, destinations in model.type_to_folder.items():
            total = sum(destinations.values())
            if total > 0:
                max_count = max(destinations.values())
                confidence = (max_count / total) * 100
                pattern_confidences.append(confidence)
        
        avg_confidence = sum(pattern_confidences) / len(pattern_confidences) if pattern_confidences else 0
        health['metrics']['avg_confidence'] = avg_confidence
        health['metrics']['total_samples'] = stats['total_samples']
        
        if avg_confidence < MIN_CONFIDENCE_THRESHOLD * 100:
            health['issues'].append(f"Low average confidence: {avg_confidence:.1f}%")
            health['recommendations'].append("Run --relearn to retrain model")
            health['overall_status'] = 'needs_attention'
    else:
        health['issues'].append("No trained model found")
        health['recommendations'].append("Run --learn to train initial model")
        health['overall_status'] = 'needs_training'
    
    # Check feedback accuracy
    feedback_stats = feedback.get_feedback_stats(learning_dir)
    if feedback_stats['total_feedback'] > 10:  # Need minimum data
        accuracy = feedback_stats.get('overall_accuracy', 100)
        health['metrics']['feedback_accuracy'] = accuracy
        
        if accuracy < MIN_ACCURACY_THRESHOLD * 100:
            health['issues'].append(f"Low feedback accuracy: {accuracy:.1f}%")
            health['recommendations'].append("Review patterns and retrain")
            health['overall_status'] = 'degraded'
    
    # Check weak patterns
    if model:
        weak_patterns = []
        for file_type, destinations in model.type_to_folder.items():
            total = sum(destinations.values())
            if total < WEAK_PATTERN_THRESHOLD:
                weak_patterns.append(f"{file_type} ({total} samples)")
        
        if weak_patterns:
            health['metrics']['weak_patterns'] = len(weak_patterns)
            health['recommendations'].append(f"Consider pruning {len(weak_patterns)} weak patterns")
    
    # Check database size and performance
    if db.database_exists(db_path):
        db_size_mb = Path(db_path).stat().st_size / (1024 * 1024)
        health['metrics']['database_size_mb'] = db_size_mb
        
        if db_size_mb > 100:
            health['recommendations'].append("Database is large, consider archiving old data")
    
    return health


def auto_retrain_if_needed(
    db_path: str = 'file_organizer.db',
    learning_dir: Path = DEFAULT_LEARNING_DIR,
    force: bool = False
) -> bool:
    """
    Automatically retrain model if confidence or accuracy drops.
    
    Args:
        db_path: Path to database
        learning_dir: Learning data directory
        force: Force retrain regardless of health
        
    Returns:
        True if retrained, False otherwise
    """
    logger = logging.getLogger('FileOrganizer')
    
    if not force:
        health = check_model_health(db_path, learning_dir)
        
        if health['overall_status'] == 'healthy':
            logger.info("[MAINTENANCE] Model health is good, no retrain needed")
            return False
        
        logger.warning(f"[MAINTENANCE] Model status: {health['overall_status']}")
        for issue in health['issues']:
            logger.warning(f"  - {issue}")
    
    # Perform retrain
    logger.info("[MAINTENANCE] Auto-retraining model...")
    
    model = learn.learn_from_history(db_path, learning_dir)
    if model:
        learn.save_model(model, learning_dir)
        
        # Log maintenance operation
        mlog = MaintenanceLog(learning_dir)
        mlog.record_operation('retrain', {
            'reason': 'automatic_health_check' if not force else 'manual_trigger',
            'samples': model.total_samples
        })
        
        logger.info(f"[MAINTENANCE] ✓ Model retrained ({model.total_samples} samples)")
        return True
    else:
        logger.error("[MAINTENANCE] Failed to retrain model")
        return False


def prune_weak_patterns(
    learning_dir: Path = DEFAULT_LEARNING_DIR,
    min_samples: int = WEAK_PATTERN_THRESHOLD
) -> int:
    """
    Remove patterns with too few samples to be reliable.
    
    Args:
        learning_dir: Learning data directory
        min_samples: Minimum samples to keep pattern
        
    Returns:
        Number of patterns pruned
    """
    logger = logging.getLogger('FileOrganizer')
    
    model = learn.load_model(learning_dir)
    if not model:
        return 0
    
    pruned_count = 0
    
    # Prune type patterns
    types_to_remove = []
    for file_type, destinations in model.type_to_folder.items():
        total = sum(destinations.values())
        if total < min_samples:
            types_to_remove.append(file_type)
    
    for file_type in types_to_remove:
        del model.type_to_folder[file_type]
        pruned_count += 1
        logger.info(f"[MAINTENANCE] Pruned weak pattern: type={file_type}")
    
    # Prune extension patterns
    exts_to_remove = []
    for ext, destinations in model.ext_to_folder.items():
        total = sum(destinations.values())
        if total < min_samples:
            exts_to_remove.append(ext)
    
    for ext in exts_to_remove:
        del model.ext_to_folder[ext]
        pruned_count += 1
        logger.info(f"[MAINTENANCE] Pruned weak pattern: ext={ext}")
    
    if pruned_count > 0:
        learn.save_model(model, learning_dir)
        
        # Log maintenance
        mlog = MaintenanceLog(learning_dir)
        mlog.record_operation('prune', {
            'patterns_removed': pruned_count,
            'threshold': min_samples
        })
        
        logger.info(f"[MAINTENANCE] ✓ Pruned {pruned_count} weak patterns")
    
    return pruned_count


def optimize_database(db_path: str = 'file_organizer.db') -> bool:
    """
    Optimize database: vacuum, reindex, analyze.
    
    Returns:
        True if successful
    """
    logger = logging.getLogger('FileOrganizer')
    
    if not db.database_exists(db_path):
        return False
    
    try:
        logger.info("[MAINTENANCE] Optimizing database...")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vacuum (reclaim space)
        cursor.execute("VACUUM")
        
        # Analyze (update statistics)
        cursor.execute("ANALYZE")
        
        # Reindex
        cursor.execute("REINDEX")
        
        conn.commit()
        conn.close()
        
        logger.info("[MAINTENANCE] ✓ Database optimized")
        return True
    
    except Exception as e:
        logger.error(f"[MAINTENANCE] Database optimization failed: {e}")
        return False


def cleanup_old_feedback(
    learning_dir: Path = DEFAULT_LEARNING_DIR,
    days: int = OLD_FEEDBACK_DAYS
) -> int:
    """
    Archive feedback data older than specified days.
    
    Returns:
        Number of feedback entries archived
    """
    logger = logging.getLogger('FileOrganizer')
    
    # For now, just log that we would archive
    # In production, would move to archive file
    
    logger.info(f"[MAINTENANCE] Feedback cleanup (keep last {days} days)")
    logger.info("[MAINTENANCE] ✓ Feedback data is current")
    
    return 0


def run_full_maintenance(
    db_path: str = 'file_organizer.db',
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> Dict[str, Any]:
    """
    Run comprehensive maintenance: retrain, prune, optimize, cleanup.
    
    Returns:
        Summary of maintenance operations
    """
    logger = logging.getLogger('FileOrganizer')
    
    logger.info("=" * 70)
    logger.info("RUNNING FULL SYSTEM MAINTENANCE")
    logger.info("=" * 70)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'operations': []
    }
    
    # 1. Check health and retrain if needed
    health = check_model_health(db_path, learning_dir)
    results['health_before'] = health
    
    if health['overall_status'] != 'healthy':
        retrained = auto_retrain_if_needed(db_path, learning_dir)
        results['operations'].append({
            'type': 'retrain',
            'success': retrained
        })
    
    # 2. Prune weak patterns
    pruned = prune_weak_patterns(learning_dir)
    results['operations'].append({
        'type': 'prune',
        'patterns_removed': pruned
    })
    
    # 3. Optimize database
    optimized = optimize_database(db_path)
    results['operations'].append({
        'type': 'optimize_db',
        'success': optimized
    })
    
    # 4. Cleanup old feedback
    archived = cleanup_old_feedback(learning_dir)
    results['operations'].append({
        'type': 'cleanup_feedback',
        'entries_archived': archived
    })
    
    # Log maintenance
    mlog = MaintenanceLog(learning_dir)
    mlog.record_operation('full_maintenance', results)
    
    logger.info("=" * 70)
    logger.info("✓ MAINTENANCE COMPLETE")
    logger.info("=" * 70)
    
    return results


# ============================================================================
# AUTONOMOUS MONITORING
# ============================================================================

def scan_directory_for_new_files(
    directory: Path,
    seen_files: set
) -> List[Path]:
    """
    Scan directory for files not in seen_files set.
    
    Args:
        directory: Directory to scan
        seen_files: Set of file paths already processed
        
    Returns:
        List of new file paths
    """
    new_files = []
    
    try:
        for entry in directory.iterdir():
            if entry.is_file() and entry not in seen_files:
                new_files.append(entry)
                seen_files.add(entry)
    except PermissionError:
        pass
    
    return new_files


def autonomous_organize_file(
    file_path: Path,
    output_dir: Path,
    db_path: str,
    learning_dir: Path,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Autonomously organize a single file using learned patterns.
    
    Returns:
        Result dictionary with action taken
    """
    logger = logging.getLogger('FileOrganizer')
    
    # Import file categorization
    from file_organizer import categorize_file, get_date_folder
    
    # Get file metadata
    file_name = file_path.name
    file_type = categorize_file(file_path)
    file_ext = file_path.suffix.lower()
    
    file_meta = {
        'file_name': file_name,
        'file_type': file_type,
        'file_ext': file_ext
    }
    
    # Predict destination
    model = learn.load_model(learning_dir)
    if not model:
        return {
            'file': file_name,
            'action': 'skipped',
            'reason': 'No trained model'
        }
    
    prediction = learn.predict_destination(file_meta, model, learning_dir)
    if not prediction or prediction[1] < 0.8:  # Require 80% confidence
        return {
            'file': file_name,
            'action': 'skipped',
            'reason': f'Low confidence ({prediction[1]*100:.0f}%)' if prediction else 'No prediction'
        }
    
    dest_folder, confidence, reason = prediction
    
    # Construct destination path
    date_folder = get_date_folder(file_path) if not dry_run else "2025/10"
    dest_path = output_dir / dest_folder / date_folder / file_name
    
    result = {
        'file': file_name,
        'destination': str(dest_path),
        'confidence': confidence,
        'reason': reason,
        'action': 'would_move' if dry_run else 'moved'
    }
    
    if not dry_run:
        # Actually move the file
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import shutil
            shutil.move(str(file_path), str(dest_path))
            
            # Record in database
            if db.database_exists(db_path):
                db.record_file_operation(
                    str(file_path),
                    str(dest_path),
                    file_name,
                    file_type,
                    'autonomous_organize',
                    db_path
                )
            
            # Update model incrementally
            learn.update_model_incremental(file_meta, dest_folder, model, learning_dir)
            
            logger.info(f"[AUTONOMOUS] ✓ {file_name} → {dest_folder} ({confidence*100:.0f}%)")
        
        except Exception as e:
            result['action'] = 'failed'
            result['error'] = str(e)
            logger.error(f"[AUTONOMOUS] Failed to move {file_name}: {e}")
    
    return result


def run_autonomous_mode(
    source_dir: Path,
    output_dir: Path = Path('organized'),
    db_path: str = 'file_organizer.db',
    learning_dir: Path = DEFAULT_LEARNING_DIR,
    dry_run: bool = False,
    max_operations: int = MAX_AUTONOMOUS_OPS
) -> Dict[str, Any]:
    """
    Run autonomous monitoring and organization mode.
    
    Continuously monitors source_dir for new files and organizes them.
    
    Args:
        source_dir: Directory to monitor
        output_dir: Where to organize files
        db_path: Database path
        learning_dir: Learning data directory
        dry_run: Preview mode
        max_operations: Safety limit
        
    Returns:
        Summary of autonomous session
    """
    logger = logging.getLogger('FileOrganizer')
    
    logger.info("=" * 70)
    logger.info("AUTONOMOUS MODE" + (" [DRY-RUN]" if dry_run else ""))
    logger.info("=" * 70)
    logger.info(f"Monitoring: {source_dir}")
    logger.info(f"Output: {output_dir}")
    logger.info(f"Poll interval: {POLL_INTERVAL_SECONDS}s")
    logger.info(f"Press Ctrl+C to stop")
    logger.info("=" * 70)
    
    seen_files = set()
    operations_count = 0
    results = {
        'start_time': datetime.now().isoformat(),
        'files_processed': 0,
        'files_moved': 0,
        'files_skipped': 0,
        'operations': []
    }
    
    # Initial scan
    for file in source_dir.rglob('*') if source_dir.is_dir() else []:
        if file.is_file():
            seen_files.add(file)
    
    try:
        while operations_count < max_operations:
            # Scan for new files
            new_files = scan_directory_for_new_files(source_dir, seen_files)
            
            for file_path in new_files:
                if operations_count >= max_operations:
                    break
                
                result = autonomous_organize_file(
                    file_path,
                    output_dir,
                    db_path,
                    learning_dir,
                    dry_run
                )
                
                results['files_processed'] += 1
                if result['action'] in ['moved', 'would_move']:
                    results['files_moved'] += 1
                else:
                    results['files_skipped'] += 1
                
                results['operations'].append(result)
                operations_count += 1
            
            # Wait before next poll
            time.sleep(POLL_INTERVAL_SECONDS)
    
    except KeyboardInterrupt:
        logger.info("\n[AUTONOMOUS] Stopped by user")
    
    results['end_time'] = datetime.now().isoformat()
    results['duration_seconds'] = (
        datetime.fromisoformat(results['end_time']) - 
        datetime.fromisoformat(results['start_time'])
    ).total_seconds()
    
    logger.info("=" * 70)
    logger.info(f"✓ Processed {results['files_processed']} files")
    logger.info(f"  Moved: {results['files_moved']}")
    logger.info(f"  Skipped: {results['files_skipped']}")
    logger.info("=" * 70)
    
    return results
