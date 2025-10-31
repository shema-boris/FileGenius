#!/usr/bin/env python3
"""
Feedback Manager for Local File Organizer
Manages user feedback reinforcement for continuous learning.

This module provides:
- Feedback tracking (correct/incorrect predictions)
- Reinforcement learning (reward/penalty system)
- Feedback-based confidence adjustment
- Analytics and reporting
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_LEARNING_DIR = Path('learning_data')
FEEDBACK_FILE = 'feedback.json'
SYNC_LOG_FILE = 'sync_log.json'

# Reinforcement parameters
POSITIVE_REINFORCEMENT = 2   # +2 weight for correct predictions
NEGATIVE_REINFORCEMENT = -1  # -1 weight for incorrect predictions
MIN_CONFIDENCE_PENALTY = 0.1 # Minimum confidence after penalties


# ============================================================================
# FEEDBACK DATA STRUCTURE
# ============================================================================

class FeedbackData:
    """
    Stores user feedback for reinforcement learning.
    
    Structure:
        {
            'patterns': {
                'type_documents': {'correct': 12, 'wrong': 3, 'confidence_adj': 0.8},
                'ext_.pdf': {'correct': 18, 'wrong': 2, 'confidence_adj': 0.9}
            },
            'metadata': {
                'total_feedback': 35,
                'last_updated': '2025-10-28T...',
                'enabled': True
            }
        }
    """
    
    def __init__(self):
        self.patterns = defaultdict(lambda: {
            'correct': 0,
            'wrong': 0,
            'confidence_adj': 1.0  # Multiplier for confidence
        })
        self.metadata = {
            'total_feedback': 0,
            'last_updated': None,
            'enabled': True,
            'version': '5.0'
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'patterns': dict(self.patterns),
            'metadata': self.metadata
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'FeedbackData':
        """Create from dictionary."""
        feedback = FeedbackData()
        feedback.patterns = defaultdict(
            lambda: {'correct': 0, 'wrong': 0, 'confidence_adj': 1.0},
            data.get('patterns', {})
        )
        feedback.metadata = data.get('metadata', feedback.metadata)
        return feedback


# ============================================================================
# FEEDBACK TRACKING
# ============================================================================

def record_positive_feedback(
    pattern_type: str,
    pattern_value: str,
    destination: str,
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> bool:
    """
    Record positive feedback (correct prediction).
    
    Args:
        pattern_type: Type of pattern ('type', 'ext', 'name')
        pattern_value: Value of pattern ('documents', '.pdf', 'report')
        destination: Where the file went
        learning_dir: Directory for learning data
        
    Returns:
        True if successful
        
    Example:
        >>> record_positive_feedback('type', 'documents', 'Documents')
        # Increases confidence for type_documents → Documents
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        feedback = load_feedback(learning_dir)
        
        if not feedback.metadata.get('enabled', True):
            return False
        
        # Create pattern key
        pattern_key = f"{pattern_type}_{pattern_value}"
        
        # Increment correct count
        feedback.patterns[pattern_key]['correct'] += POSITIVE_REINFORCEMENT
        
        # Adjust confidence (increase up to 1.5x)
        current_adj = feedback.patterns[pattern_key]['confidence_adj']
        feedback.patterns[pattern_key]['confidence_adj'] = min(1.5, current_adj + 0.05)
        
        # Update metadata
        feedback.metadata['total_feedback'] += 1
        feedback.metadata['last_updated'] = datetime.now().isoformat()
        
        # Save
        save_feedback(feedback, learning_dir)
        
        logger.info(f"[LEARNING] Reinforced mapping: {pattern_value} → {destination} (↑ +{POSITIVE_REINFORCEMENT})")
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to record positive feedback: {e}")
        return False


def record_negative_feedback(
    pattern_type: str,
    pattern_value: str,
    destination: str,
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> bool:
    """
    Record negative feedback (incorrect prediction).
    
    Args:
        pattern_type: Type of pattern ('type', 'ext', 'name')
        pattern_value: Value of pattern
        destination: Where the file was incorrectly moved
        learning_dir: Directory for learning data
        
    Returns:
        True if successful
        
    Example:
        >>> record_negative_feedback('ext', '.zip', 'others')
        # Decreases confidence for .zip → others
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        feedback = load_feedback(learning_dir)
        
        if not feedback.metadata.get('enabled', True):
            return False
        
        # Create pattern key
        pattern_key = f"{pattern_type}_{pattern_value}"
        
        # Increment wrong count
        feedback.patterns[pattern_key]['wrong'] += abs(NEGATIVE_REINFORCEMENT)
        
        # Adjust confidence (decrease but not below threshold)
        current_adj = feedback.patterns[pattern_key]['confidence_adj']
        feedback.patterns[pattern_key]['confidence_adj'] = max(
            MIN_CONFIDENCE_PENALTY,
            current_adj - 0.1
        )
        
        # Update metadata
        feedback.metadata['total_feedback'] += 1
        feedback.metadata['last_updated'] = datetime.now().isoformat()
        
        # Save
        save_feedback(feedback, learning_dir)
        
        logger.info(f"[FEEDBACK] Corrected pattern: {pattern_value} → {destination} (↓ {NEGATIVE_REINFORCEMENT})")
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to record negative feedback: {e}")
        return False


def record_undo_operation(
    operation_id: str,
    db_path: str = 'file_organizer.db',
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> bool:
    """
    Record negative feedback when user undoes an operation.
    
    Args:
        operation_id: ID of undone operation
        db_path: Path to database
        learning_dir: Directory for learning data
        
    Returns:
        True if successful
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        # Import here to avoid circular dependency
        import database_manager as db
        
        # Get files from operation
        files = db.get_operation_files(operation_id, db_path)
        
        for file_record in files:
            file_type = file_record.get('file_type', 'unknown')
            file_ext = Path(file_record['file_name']).suffix.lower()
            
            # Extract destination
            dest_path = Path(file_record['new_path'])
            # Assume organized/category/year/month structure
            parts = dest_path.parts
            if 'organized' in parts:
                idx = parts.index('organized')
                if idx + 1 < len(parts):
                    destination = parts[idx + 1]
                else:
                    continue
            else:
                continue
            
            # Record negative feedback for each pattern
            record_negative_feedback('type', file_type, destination, learning_dir)
            if file_ext:
                record_negative_feedback('ext', file_ext, destination, learning_dir)
        
        logger.info(f"[FEEDBACK] Recorded undo operation: {operation_id}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to record undo feedback: {e}")
        return False


# ============================================================================
# CONFIDENCE ADJUSTMENT
# ============================================================================

def get_confidence_adjustment(
    pattern_type: str,
    pattern_value: str,
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> float:
    """
    Get confidence adjustment multiplier for a pattern.
    
    Args:
        pattern_type: Type of pattern
        pattern_value: Value of pattern
        learning_dir: Directory for learning data
        
    Returns:
        Multiplier (0.1 to 1.5)
    """
    try:
        feedback = load_feedback(learning_dir)
        pattern_key = f"{pattern_type}_{pattern_value}"
        
        if pattern_key in feedback.patterns:
            return feedback.patterns[pattern_key]['confidence_adj']
        
        return 1.0  # Neutral (no adjustment)
    
    except Exception:
        return 1.0


def apply_feedback_to_confidence(
    base_confidence: float,
    file_metadata: Dict[str, Any],
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> float:
    """
    Apply feedback adjustments to base confidence.
    
    Args:
        base_confidence: Original confidence (0-1)
        file_metadata: File metadata with patterns
        learning_dir: Directory for learning data
        
    Returns:
        Adjusted confidence (0-1)
    """
    try:
        # Get adjustments for each pattern
        adjustments = []
        
        # File type adjustment
        if 'file_type' in file_metadata:
            adj = get_confidence_adjustment('type', file_metadata['file_type'], learning_dir)
            adjustments.append(adj)
        
        # Extension adjustment
        if 'file_ext' in file_metadata:
            adj = get_confidence_adjustment('ext', file_metadata['file_ext'], learning_dir)
            adjustments.append(adj)
        
        # Average adjustment
        if adjustments:
            avg_adjustment = sum(adjustments) / len(adjustments)
            adjusted = base_confidence * avg_adjustment
            return min(1.0, max(0.0, adjusted))
        
        return base_confidence
    
    except Exception:
        return base_confidence


# ============================================================================
# PERSISTENCE
# ============================================================================

def save_feedback(
    feedback: FeedbackData,
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> bool:
    """Save feedback data to disk."""
    logger = logging.getLogger('FileOrganizer')
    
    try:
        learning_dir.mkdir(parents=True, exist_ok=True)
        feedback_path = learning_dir / FEEDBACK_FILE
        
        with open(feedback_path, 'w', encoding='utf-8') as f:
            json.dump(feedback.to_dict(), f, indent=2, ensure_ascii=False)
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")
        return False


def load_feedback(
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> FeedbackData:
    """Load feedback data from disk."""
    feedback_path = learning_dir / FEEDBACK_FILE
    
    if not feedback_path.exists():
        return FeedbackData()
    
    try:
        with open(feedback_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return FeedbackData.from_dict(data)
    
    except Exception:
        return FeedbackData()


def clear_feedback(
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> bool:
    """Clear all feedback data."""
    logger = logging.getLogger('FileOrganizer')
    
    try:
        feedback_path = learning_dir / FEEDBACK_FILE
        
        if feedback_path.exists():
            feedback_path.unlink()
            logger.info("✓ Feedback data cleared")
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to clear feedback: {e}")
        return False


# ============================================================================
# ANALYTICS
# ============================================================================

def get_feedback_stats(
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> Dict[str, Any]:
    """
    Get feedback statistics.
    
    Returns:
        Dictionary with feedback analytics
    """
    feedback = load_feedback(learning_dir)
    
    total_correct = 0
    total_wrong = 0
    pattern_stats = []
    
    for pattern_key, data in feedback.patterns.items():
        correct = data['correct']
        wrong = data['wrong']
        
        total_correct += correct
        total_wrong += wrong
        
        total_feedback = correct + wrong
        accuracy = (correct / total_feedback * 100) if total_feedback > 0 else 0
        
        pattern_stats.append({
            'pattern': pattern_key,
            'correct': correct,
            'wrong': wrong,
            'accuracy': accuracy,
            'confidence_adj': data['confidence_adj']
        })
    
    # Sort by total feedback (most used patterns)
    pattern_stats.sort(key=lambda x: x['correct'] + x['wrong'], reverse=True)
    
    # Calculate overall accuracy
    total_feedback = total_correct + total_wrong
    overall_accuracy = (total_correct / total_feedback * 100) if total_feedback > 0 else 0
    
    # Find strongest and weakest patterns
    if pattern_stats:
        strongest = max(pattern_stats, key=lambda x: x['accuracy'])
        weakest = min(pattern_stats, key=lambda x: x['accuracy'])
    else:
        strongest = None
        weakest = None
    
    return {
        'total_feedback': total_feedback,
        'total_correct': total_correct,
        'total_wrong': total_wrong,
        'overall_accuracy': overall_accuracy,
        'pattern_count': len(pattern_stats),
        'patterns': pattern_stats[:10],  # Top 10
        'strongest_pattern': strongest,
        'weakest_pattern': weakest,
        'last_updated': feedback.metadata.get('last_updated'),
        'enabled': feedback.metadata.get('enabled', True)
    }


def print_feedback_stats(learning_dir: Path = DEFAULT_LEARNING_DIR):
    """Print feedback statistics to console."""
    logger = logging.getLogger('FileOrganizer')
    
    stats = get_feedback_stats(learning_dir)
    
    logger.info("=" * 70)
    logger.info("🧠 LEARNING INSIGHTS")
    logger.info("=" * 70)
    
    if stats['total_feedback'] == 0:
        logger.info("No feedback data available yet.")
        logger.info("The system will learn from your organization patterns automatically.")
        logger.info("=" * 70)
        return
    
    logger.info(f"Overall Accuracy: {stats['overall_accuracy']:.1f}%")
    logger.info(f"Total Feedback Events: {stats['total_feedback']}")
    logger.info(f"  ✓ Correct: {stats['total_correct']}")
    logger.info(f"  ✗ Wrong: {stats['total_wrong']}")
    logger.info("")
    
    if stats['strongest_pattern']:
        sp = stats['strongest_pattern']
        logger.info(f"Strongest Pattern: {sp['pattern']}")
        logger.info(f"  Accuracy: {sp['accuracy']:.1f}%")
        logger.info(f"  Confidence Adj: {sp['confidence_adj']:.2f}x")
    
    if stats['weakest_pattern'] and stats['pattern_count'] > 1:
        wp = stats['weakest_pattern']
        logger.info(f"Weakest Pattern: {wp['pattern']}")
        logger.info(f"  Accuracy: {wp['accuracy']:.1f}%")
        logger.info(f"  Confidence Adj: {wp['confidence_adj']:.2f}x")
    
    logger.info("")
    logger.info("Top Patterns:")
    for i, pattern in enumerate(stats['patterns'][:5], 1):
        logger.info(f"  {i}. {pattern['pattern']}: {pattern['accuracy']:.1f}% accuracy")
    
    logger.info("=" * 70)


# ============================================================================
# FEEDBACK CONTROL
# ============================================================================

def enable_feedback(learning_dir: Path = DEFAULT_LEARNING_DIR) -> bool:
    """Enable feedback tracking."""
    logger = logging.getLogger('FileOrganizer')
    
    try:
        feedback = load_feedback(learning_dir)
        feedback.metadata['enabled'] = True
        save_feedback(feedback, learning_dir)
        
        logger.info("✓ Feedback tracking enabled")
        return True
    
    except Exception as e:
        logger.error(f"Failed to enable feedback: {e}")
        return False


def disable_feedback(learning_dir: Path = DEFAULT_LEARNING_DIR) -> bool:
    """Disable feedback tracking."""
    logger = logging.getLogger('FileOrganizer')
    
    try:
        feedback = load_feedback(learning_dir)
        feedback.metadata['enabled'] = False
        save_feedback(feedback, learning_dir)
        
        logger.info("✓ Feedback tracking disabled")
        return True
    
    except Exception as e:
        logger.error(f"Failed to disable feedback: {e}")
        return False


def is_feedback_enabled(learning_dir: Path = DEFAULT_LEARNING_DIR) -> bool:
    """Check if feedback tracking is enabled."""
    try:
        feedback = load_feedback(learning_dir)
        return feedback.metadata.get('enabled', True)
    except Exception:
        return True  # Default to enabled
