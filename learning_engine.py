#!/usr/bin/env python3
"""
Learning Engine for Local File Organizer
Learns user organization patterns and makes intelligent predictions.

This module provides adaptive learning capabilities:
- Pattern recognition from historical data
- Confidence-based predictions
- Explainable recommendations
- 100% offline operation
"""

import json
import pickle
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, Counter
from datetime import datetime

import database_manager as db


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

DEFAULT_LEARNING_DIR = Path('learning_data')
PREFERENCES_FILE = 'preferences.json'
MODEL_FILE = 'model.pkl'

# Confidence thresholds
CONFIDENCE_HIGH = 0.8    # >80% = auto-organize safe
CONFIDENCE_MEDIUM = 0.5  # 50-80% = suggest
CONFIDENCE_LOW = 0.5     # <50% = ask user

# Minimum samples required to make predictions
MIN_SAMPLES_FOR_PREDICTION = 3


# ============================================================================
# LEARNING MODEL
# ============================================================================

def _nested_defaultdict():
    """Factory function for nested defaultdict (pickle-compatible)."""
    return defaultdict(Counter)


class FileOrganizationModel:
    """
    Learns user file organization patterns from historical data.
    Uses frequency-based heuristics for explainable predictions.
    """
    
    def __init__(self):
        """Initialize empty model."""
        # Pattern: file_type -> {destination_folder: count}
        self.type_to_folder = defaultdict(Counter)
        
        # Pattern: file_extension -> {destination_folder: count}
        self.ext_to_folder = defaultdict(Counter)
        
        # Pattern: filename_pattern -> {destination_folder: count}
        self.name_pattern_to_folder = defaultdict(Counter)
        
        # Pattern: year -> {file_type: {destination: count}}
        # Use named function instead of lambda for pickle compatibility
        self.temporal_patterns = defaultdict(_nested_defaultdict)
        
        # Metadata
        self.total_samples = 0
        self.last_trained = None
        self.version = '4.0'
    
    def __repr__(self):
        return f"<FileOrganizationModel samples={self.total_samples} trained={self.last_trained}>"


# ============================================================================
# PATTERN EXTRACTION
# ============================================================================

def extract_filename_pattern(filename: str) -> str:
    """
    Extract pattern from filename for learning.
    
    Examples:
        'report_2024_Q1.pdf' -> 'report'
        'IMG_1234.jpg' -> 'IMG'
        'document.docx' -> 'document'
    
    Args:
        filename: Original filename
        
    Returns:
        Pattern string (first word or prefix)
    """
    # Remove extension
    name_no_ext = Path(filename).stem
    
    # Split by common separators
    parts = name_no_ext.replace('_', ' ').replace('-', ' ').split()
    
    if parts:
        # Return first meaningful part (lowercase for consistency)
        return parts[0].lower()
    
    return 'unknown'


def extract_destination_pattern(path: str) -> str:
    """
    Extract meaningful destination pattern from full path.
    
    Examples:
        'C:/Users/HP/organized/documents/2024/10/file.pdf' -> 'documents'
        'organized/images/2024/10/photo.jpg' -> 'images'
    
    Args:
        path: Full file path
        
    Returns:
        Destination category or folder name
    """
    path_obj = Path(path)
    parts = path_obj.parts
    
    # Look for 'organized' in path and get the next folder
    try:
        if 'organized' in parts:
            idx = parts.index('organized')
            if idx + 1 < len(parts):
                return parts[idx + 1]
    except (ValueError, IndexError):
        pass
    
    # Fallback: use parent folder name
    if path_obj.parent.name:
        return path_obj.parent.name
    
    return 'unknown'


# ============================================================================
# TRAINING & LEARNING
# ============================================================================

def learn_from_history(db_path: str = 'file_organizer.db') -> FileOrganizationModel:
    """
    Learn user organization patterns from database history.
    
    Analyzes all past file operations to identify:
    - Which file types go to which folders
    - Extension-based routing patterns
    - Filename pattern associations
    - Temporal organization trends
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Trained FileOrganizationModel
        
    Example:
        >>> model = learn_from_history()
        >>> print(f"Learned from {model.total_samples} files")
    """
    logger = logging.getLogger('FileOrganizer')
    
    model = FileOrganizationModel()
    
    if not db.database_exists(db_path):
        logger.warning("Database not found. Cannot learn from history.")
        return model
    
    logger.info("Learning from organization history...")
    
    try:
        with db.get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Get all file records
            cursor.execute("""
                SELECT file_name, file_type, new_path, created_at
                FROM files
                ORDER BY operation_date ASC
            """)
            
            records = cursor.fetchall()
            
            for record in records:
                file_name = record['file_name']
                file_type = record['file_type']
                new_path = record['new_path']
                created_at = record['created_at']
                
                # Extract patterns
                file_ext = Path(file_name).suffix.lower()
                name_pattern = extract_filename_pattern(file_name)
                destination = extract_destination_pattern(new_path)
                
                # Learn type -> folder association
                model.type_to_folder[file_type][destination] += 1
                
                # Learn extension -> folder association
                if file_ext:
                    model.ext_to_folder[file_ext][destination] += 1
                
                # Learn filename pattern -> folder association
                model.name_pattern_to_folder[name_pattern][destination] += 1
                
                # Learn temporal patterns (year)
                try:
                    created_date = datetime.fromisoformat(created_at)
                    year = created_date.year
                    model.temporal_patterns[year][file_type][destination] += 1
                except Exception:
                    pass
                
                model.total_samples += 1
            
            model.last_trained = datetime.now().isoformat()
            
            logger.info(f"✓ Learned from {model.total_samples} files")
            logger.info(f"  • {len(model.type_to_folder)} file types")
            logger.info(f"  • {len(model.ext_to_folder)} extensions")
            logger.info(f"  • {len(model.name_pattern_to_folder)} filename patterns")
            
            return model
    
    except Exception as e:
        logger.error(f"Failed to learn from history: {e}")
        return model


# ============================================================================
# PREDICTION & INFERENCE
# ============================================================================

def predict_destination(
    file_metadata: Dict[str, Any],
    model: FileOrganizationModel
) -> Optional[Tuple[str, float, str]]:
    """
    Predict destination folder for a file based on learned patterns.
    
    Args:
        file_metadata: Dictionary with keys:
            - 'file_name': str
            - 'file_type': str (e.g., 'documents', 'images')
            - 'file_ext': str (e.g., '.pdf', '.jpg')
        model: Trained FileOrganizationModel
        
    Returns:
        Tuple of (destination, confidence, reason) or None
        - destination: Predicted folder (e.g., 'documents')
        - confidence: Float 0-1
        - reason: Explanation string
        
    Example:
        >>> metadata = {'file_name': 'report.pdf', 'file_type': 'documents', 'file_ext': '.pdf'}
        >>> dest, conf, reason = predict_destination(metadata, model)
        >>> print(f"{dest} ({conf:.0%}): {reason}")
    """
    if model.total_samples < MIN_SAMPLES_FOR_PREDICTION:
        return None
    
    file_name = file_metadata.get('file_name', '')
    file_type = file_metadata.get('file_type', '')
    file_ext = file_metadata.get('file_ext', '').lower()
    
    predictions = []
    
    # Strategy 1: File type frequency
    if file_type in model.type_to_folder:
        type_counts = model.type_to_folder[file_type]
        if type_counts:
            most_common_dest, count = type_counts.most_common(1)[0]
            total = sum(type_counts.values())
            confidence = count / total
            
            predictions.append({
                'destination': most_common_dest,
                'confidence': confidence,
                'reason': f"Based on {count}/{total} prior {file_type} files moved to '{most_common_dest}'",
                'weight': 0.5  # Type matching is moderately strong
            })
    
    # Strategy 2: File extension frequency
    if file_ext and file_ext in model.ext_to_folder:
        ext_counts = model.ext_to_folder[file_ext]
        if ext_counts:
            most_common_dest, count = ext_counts.most_common(1)[0]
            total = sum(ext_counts.values())
            confidence = count / total
            
            predictions.append({
                'destination': most_common_dest,
                'confidence': confidence,
                'reason': f"Based on {count}/{total} prior {file_ext} files moved to '{most_common_dest}'",
                'weight': 0.3  # Extension is weaker signal than type
            })
    
    # Strategy 3: Filename pattern
    name_pattern = extract_filename_pattern(file_name)
    if name_pattern in model.name_pattern_to_folder:
        pattern_counts = model.name_pattern_to_folder[name_pattern]
        if pattern_counts:
            most_common_dest, count = pattern_counts.most_common(1)[0]
            total = sum(pattern_counts.values())
            confidence = count / total
            
            predictions.append({
                'destination': most_common_dest,
                'confidence': confidence,
                'reason': f"Files starting with '{name_pattern}' usually go to '{most_common_dest}' ({count}/{total})",
                'weight': 0.2  # Filename pattern is weakest but can be useful
            })
    
    # No predictions available
    if not predictions:
        return None
    
    # Weighted voting: combine predictions
    destination_scores = defaultdict(lambda: {'total_confidence': 0, 'total_weight': 0, 'reasons': []})
    
    for pred in predictions:
        dest = pred['destination']
        weighted_conf = pred['confidence'] * pred['weight']
        
        destination_scores[dest]['total_confidence'] += weighted_conf
        destination_scores[dest]['total_weight'] += pred['weight']
        destination_scores[dest]['reasons'].append(pred['reason'])
    
    # Find best destination
    best_dest = max(
        destination_scores.items(),
        key=lambda x: x[1]['total_confidence']
    )
    
    destination = best_dest[0]
    score_data = best_dest[1]
    
    # Normalize confidence
    final_confidence = score_data['total_confidence'] / score_data['total_weight']
    
    # Combine reasons
    reason = '; '.join(score_data['reasons'])
    
    return destination, final_confidence, reason


def predict_batch(
    files: List[Dict[str, Any]],
    model: FileOrganizationModel
) -> List[Dict[str, Any]]:
    """
    Predict destinations for multiple files.
    
    Args:
        files: List of file metadata dictionaries
        model: Trained model
        
    Returns:
        List of predictions with confidence and reasons
    """
    predictions = []
    
    for file_meta in files:
        prediction = predict_destination(file_meta, model)
        
        if prediction:
            dest, conf, reason = prediction
            predictions.append({
                'file_name': file_meta.get('file_name', 'unknown'),
                'destination': dest,
                'confidence': conf,
                'reason': reason,
                'priority': get_confidence_priority(conf)
            })
        else:
            predictions.append({
                'file_name': file_meta.get('file_name', 'unknown'),
                'destination': None,
                'confidence': 0.0,
                'reason': 'Insufficient learning data',
                'priority': 'low'
            })
    
    return predictions


def get_confidence_priority(confidence: float) -> str:
    """
    Convert confidence score to priority level.
    
    Args:
        confidence: Float 0-1
        
    Returns:
        'high', 'medium', or 'low'
    """
    if confidence >= CONFIDENCE_HIGH:
        return 'high'
    elif confidence >= CONFIDENCE_MEDIUM:
        return 'medium'
    else:
        return 'low'


def get_confidence_emoji(confidence: float) -> str:
    """Get emoji for confidence level."""
    if confidence >= CONFIDENCE_HIGH:
        return '🟢'
    elif confidence >= CONFIDENCE_MEDIUM:
        return '🟡'
    else:
        return '🔴'


# ============================================================================
# MODEL PERSISTENCE
# ============================================================================

def save_model(model: FileOrganizationModel, learning_dir: Path = DEFAULT_LEARNING_DIR) -> bool:
    """
    Save trained model to disk.
    
    Args:
        model: Trained FileOrganizationModel
        learning_dir: Directory to save model
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        learning_dir.mkdir(parents=True, exist_ok=True)
        
        model_path = learning_dir / MODEL_FILE
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        logger.info(f"✓ Model saved: {model_path}")
        logger.info(f"  • {model.total_samples} training samples")
        logger.info(f"  • Last trained: {model.last_trained}")
        
        # Also save human-readable preferences
        save_preferences_json(model, learning_dir)
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to save model: {e}")
        return False


def load_model(learning_dir: Path = DEFAULT_LEARNING_DIR) -> Optional[FileOrganizationModel]:
    """
    Load trained model from disk.
    
    Args:
        learning_dir: Directory containing model
        
    Returns:
        Loaded FileOrganizationModel or None
    """
    logger = logging.getLogger('FileOrganizer')
    
    model_path = learning_dir / MODEL_FILE
    
    if not model_path.exists():
        logger.info("No trained model found. Run --learn to train.")
        return None
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        logger.info(f"✓ Model loaded: {model_path}")
        logger.info(f"  • {model.total_samples} training samples")
        logger.info(f"  • Last trained: {model.last_trained}")
        
        return model
    
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return None


def save_preferences_json(model: FileOrganizationModel, learning_dir: Path) -> bool:
    """Save human-readable preferences file."""
    try:
        prefs = {
            'metadata': {
                'version': model.version,
                'total_samples': model.total_samples,
                'last_trained': model.last_trained
            },
            'type_patterns': {
                file_type: dict(folders.most_common(3))
                for file_type, folders in model.type_to_folder.items()
            },
            'extension_patterns': {
                ext: dict(folders.most_common(3))
                for ext, folders in model.ext_to_folder.items()
            },
            'name_patterns': {
                pattern: dict(folders.most_common(3))
                for pattern, folders in model.name_pattern_to_folder.items()
            }
        }
        
        prefs_path = learning_dir / PREFERENCES_FILE
        with open(prefs_path, 'w', encoding='utf-8') as f:
            json.dump(prefs, f, indent=2, ensure_ascii=False)
        
        return True
    
    except Exception:
        return False


def clear_learning_data(learning_dir: Path = DEFAULT_LEARNING_DIR) -> bool:
    """
    Clear all learning data and models.
    
    Args:
        learning_dir: Directory containing learning data
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        if not learning_dir.exists():
            logger.info("No learning data to clear.")
            return True
        
        # Delete model file
        model_path = learning_dir / MODEL_FILE
        if model_path.exists():
            model_path.unlink()
            logger.info(f"✓ Deleted: {model_path}")
        
        # Delete preferences file
        prefs_path = learning_dir / PREFERENCES_FILE
        if prefs_path.exists():
            prefs_path.unlink()
            logger.info(f"✓ Deleted: {prefs_path}")
        
        # Remove directory if empty
        try:
            learning_dir.rmdir()
            logger.info(f"✓ Removed directory: {learning_dir}")
        except OSError:
            pass  # Directory not empty, that's ok
        
        logger.info("✓ Learning data cleared")
        return True
    
    except Exception as e:
        logger.error(f"Failed to clear learning data: {e}")
        return False


# ============================================================================
# ANALYSIS & REPORTING
# ============================================================================

def get_learning_stats(model: FileOrganizationModel) -> Dict[str, Any]:
    """
    Get statistics about the learned model.
    
    Args:
        model: Trained model
        
    Returns:
        Dictionary with learning statistics
    """
    return {
        'total_samples': model.total_samples,
        'last_trained': model.last_trained,
        'file_types_learned': len(model.type_to_folder),
        'extensions_learned': len(model.ext_to_folder),
        'name_patterns_learned': len(model.name_pattern_to_folder),
        'years_covered': len(model.temporal_patterns),
        'most_common_types': {
            ftype: folders.most_common(1)[0] if folders else None
            for ftype, folders in list(model.type_to_folder.items())[:5]
        }
    }


def print_learning_summary(model: FileOrganizationModel):
    """
    Print human-readable summary of learned patterns.
    
    Args:
        model: Trained model
    """
    logger = logging.getLogger('FileOrganizer')
    
    logger.info("=" * 70)
    logger.info("LEARNING SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Training samples: {model.total_samples}")
    logger.info(f"Last trained: {model.last_trained}")
    logger.info("")
    
    logger.info("📁 File Type Patterns:")
    for file_type, folders in list(model.type_to_folder.items())[:5]:
        if folders:
            dest, count = folders.most_common(1)[0]
            total = sum(folders.values())
            pct = (count / total * 100) if total > 0 else 0
            logger.info(f"  • {file_type:15s} → {dest:20s} ({count}/{total} = {pct:.0f}%)")
    
    logger.info("")
    logger.info("=" * 70)
