#!/usr/bin/env python3
"""
Suggestion Engine for Local File Organizer
Analyzes file organization patterns and suggests optimization strategies.

This module provides intelligent suggestions based on:
- File type distributions
- Organization patterns
- Size analysis
- Duplicate detection
- Temporal patterns
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter

import database_manager as db
import learning_engine as learn


# ============================================================================
# SUGGESTION TYPES
# ============================================================================

class Suggestion:
    """Base class for organization suggestions."""
    
    def __init__(self, suggestion_type: str, priority: str, description: str, 
                 details: Dict[str, Any], action: Optional[str] = None,
                 confidence: Optional[float] = None, reason: Optional[str] = None):
        self.type = suggestion_type
        self.priority = priority  # 'high', 'medium', 'low'
        self.description = description
        self.details = details
        self.action = action  # Recommended CLI command
        self.confidence = confidence  # Phase 4: 0-1 confidence score
        self.reason = reason  # Phase 4: Explanation for prediction
    
    def __str__(self):
        priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
        emoji = priority_emoji.get(self.priority, '⚪')
        
        output = f"{emoji} [{self.priority.upper()}] {self.description}\n"
        
        # Phase 4: Show confidence if available
        if self.confidence is not None:
            conf_emoji = learn.get_confidence_emoji(self.confidence)
            output += f"  {conf_emoji} Confidence: {self.confidence:.1%}\n"
        
        # Phase 4: Show reason if available
        if self.reason:
            output += f"  📊 Reason: {self.reason}\n"
        
        for key, value in self.details.items():
            output += f"  • {key}: {value}\n"
        if self.action:
            output += f"  💡 Suggested action: {self.action}\n"
        return output


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def analyze_file_distribution(db_path: str = 'file_organizer.db') -> Dict[str, Any]:
    """
    Analyze the distribution of files by type.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Dictionary with file type statistics
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        stats = db.get_database_stats(db_path)
        
        total_files = stats['total_files']
        files_by_type = stats['files_by_type']
        
        # Calculate percentages
        distribution = {}
        for file_type, count in files_by_type.items():
            percentage = (count / total_files * 100) if total_files > 0 else 0
            distribution[file_type] = {
                'count': count,
                'percentage': round(percentage, 2)
            }
        
        return {
            'total_files': total_files,
            'distribution': distribution,
            'num_categories': len(files_by_type)
        }
    
    except Exception as e:
        logger.error(f"Failed to analyze file distribution: {e}")
        return {}


def analyze_duplicates(db_path: str = 'file_organizer.db') -> Dict[str, Any]:
    """
    Analyze duplicate files in the database.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Dictionary with duplicate statistics
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        duplicate_groups = db.get_all_duplicates(db_path)
        
        total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
        wasted_space = 0
        
        duplicate_details = []
        for group in duplicate_groups:
            if len(group) > 1:
                file_size = group[0]['file_size']
                wasted_size = file_size * (len(group) - 1)
                wasted_space += wasted_size
                
                duplicate_details.append({
                    'file_name': group[0]['file_name'],
                    'count': len(group),
                    'size_bytes': file_size,
                    'wasted_bytes': wasted_size,
                    'paths': [f['new_path'] for f in group]
                })
        
        return {
            'duplicate_groups': len(duplicate_groups),
            'total_duplicates': total_duplicates,
            'wasted_space_bytes': wasted_space,
            'wasted_space_mb': round(wasted_space / (1024 * 1024), 2),
            'details': duplicate_details
        }
    
    except Exception as e:
        logger.error(f"Failed to analyze duplicates: {e}")
        return {}


def analyze_large_files(db_path: str = 'file_organizer.db', limit: int = 10) -> List[Dict[str, Any]]:
    """
    Find the largest files in the database.
    
    Args:
        db_path: Path to SQLite database
        limit: Number of large files to return
        
    Returns:
        List of largest file records
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        with db.get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT file_name, file_size, file_type, new_path
                FROM files
                ORDER BY file_size DESC
                LIMIT ?
            """, (limit,))
            
            large_files = []
            for row in cursor.fetchall():
                large_files.append({
                    'file_name': row['file_name'],
                    'file_size': row['file_size'],
                    'file_size_mb': round(row['file_size'] / (1024 * 1024), 2),
                    'file_type': row['file_type'],
                    'path': row['new_path']
                })
            
            return large_files
    
    except Exception as e:
        logger.error(f"Failed to analyze large files: {e}")
        return []


def analyze_temporal_patterns(db_path: str = 'file_organizer.db') -> Dict[str, Any]:
    """
    Analyze when files were created/modified.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Dictionary with temporal statistics
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        with db.get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT created_at, modified_at, file_type
                FROM files
            """)
            
            years = Counter()
            months = Counter()
            file_types_by_year = defaultdict(Counter)
            
            for row in cursor.fetchall():
                try:
                    created = datetime.fromisoformat(row['created_at'])
                    year = created.year
                    month = f"{year}-{created.month:02d}"
                    
                    years[year] += 1
                    months[month] += 1
                    file_types_by_year[year][row['file_type']] += 1
                except Exception:
                    continue
            
            return {
                'years': dict(years.most_common()),
                'months': dict(months.most_common(12)),
                'file_types_by_year': {
                    year: dict(types) for year, types in file_types_by_year.items()
                }
            }
    
    except Exception as e:
        logger.error(f"Failed to analyze temporal patterns: {e}")
        return {}


def analyze_operations(db_path: str = 'file_organizer.db') -> Dict[str, Any]:
    """
    Analyze organization operations history.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Dictionary with operation statistics
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        with db.get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Get all operations
            cursor.execute("""
                SELECT operation_id, operation_date, COUNT(*) as file_count
                FROM files
                GROUP BY operation_id
                ORDER BY operation_date DESC
            """)
            
            operations = []
            for row in cursor.fetchall():
                operations.append({
                    'operation_id': row['operation_id'],
                    'operation_date': row['operation_date'],
                    'file_count': row['file_count']
                })
            
            return {
                'total_operations': len(operations),
                'operations': operations
            }
    
    except Exception as e:
        logger.error(f"Failed to analyze operations: {e}")
        return {}


# ============================================================================
# ADAPTIVE LEARNING SUGGESTIONS (PHASE 4)
# ============================================================================

def generate_adaptive_suggestions(
    db_path: str,
    model: 'learn.FileOrganizationModel'
) -> List[Suggestion]:
    """
    Generate suggestions using adaptive learning predictions.
    
    Args:
        db_path: Path to database
        model: Trained learning model
        
    Returns:
        List of adaptive suggestions with confidence scores
    """
    logger = logging.getLogger('FileOrganizer')
    suggestions = []
    
    # Add learning system status
    stats = learn.get_learning_stats(model)
    
    suggestions.append(Suggestion(
        suggestion_type='learning_active',
        priority='low',
        description="Adaptive Learning System Active",
        details={
            'Training samples': stats['total_samples'],
            'File types learned': stats['file_types_learned'],
            'Last trained': stats['last_trained'][:19] if stats['last_trained'] else 'Never'
        },
        confidence=1.0,
        reason=f"Model trained on {stats['total_samples']} historical file operations",
        action="python file_organizer.py --auto  # Auto-organize with learned patterns"
    ))
    
    return suggestions


# ============================================================================
# SUGGESTION GENERATION
# ============================================================================

def generate_suggestions(db_path: str = 'file_organizer.db', 
                        use_learning: bool = True) -> List[Suggestion]:
    """
    Generate intelligent suggestions based on database analysis.
    
    Args:
        db_path: Path to SQLite database
        use_learning: Whether to include adaptive learning predictions (Phase 4)
        
    Returns:
        List of Suggestion objects
    """
    logger = logging.getLogger('FileOrganizer')
    suggestions = []
    
    if not db.database_exists(db_path):
        logger.warning("Database not found. No suggestions available.")
        return suggestions
    
    # Phase 4: Load learning model if available
    model = None
    if use_learning:
        model = learn.load_model()
        if model:
            logger.info(f"✓ Loaded learning model ({model.total_samples} samples)")
    
    # Phase 4: Add adaptive predictions if model exists
    if model and model.total_samples >= learn.MIN_SAMPLES_FOR_PREDICTION:
        adaptive_suggestions = generate_adaptive_suggestions(db_path, model)
        suggestions.extend(adaptive_suggestions)
    
    # Analyze duplicates
    dup_analysis = analyze_duplicates(db_path)
    if dup_analysis.get('total_duplicates', 0) > 0:
        wasted_mb = dup_analysis.get('wasted_space_mb', 0)
        suggestions.append(Suggestion(
            suggestion_type='duplicates',
            priority='high' if wasted_mb > 10 else 'medium',
            description=f"Found {dup_analysis['total_duplicates']} duplicate files",
            details={
                'Duplicate groups': dup_analysis['duplicate_groups'],
                'Wasted space': f"{wasted_mb} MB",
                'Potential savings': f"Delete duplicates to free {wasted_mb} MB"
            },
            action="python file_organizer.py <folder> --no-dry-run --remove-duplicates"
        ))
    
    # Analyze file distribution
    dist_analysis = analyze_file_distribution(db_path)
    if dist_analysis:
        total = dist_analysis['total_files']
        distribution = dist_analysis['distribution']
        
        # Check for unbalanced categories
        if distribution:
            max_category = max(distribution.items(), key=lambda x: x[1]['count'])
            max_name, max_data = max_category
            
            if max_data['percentage'] > 50:
                suggestions.append(Suggestion(
                    suggestion_type='distribution',
                    priority='low',
                    description=f"Category '{max_name}' dominates your files",
                    details={
                        'Percentage': f"{max_data['percentage']}%",
                        'File count': max_data['count'],
                        'Suggestion': f"Consider creating subcategories for {max_name}"
                    }
                ))
    
    # Analyze large files
    large_files = analyze_large_files(db_path, limit=5)
    if large_files:
        total_large_size = sum(f['file_size'] for f in large_files)
        total_large_mb = round(total_large_size / (1024 * 1024), 2)
        
        if total_large_mb > 100:
            suggestions.append(Suggestion(
                suggestion_type='large_files',
                priority='medium',
                description=f"Top 5 files occupy {total_large_mb} MB",
                details={
                    'Largest file': large_files[0]['file_name'],
                    'Size': f"{large_files[0]['file_size_mb']} MB",
                    'Suggestion': 'Consider archiving or compressing large files'
                }
            ))
    
    # Analyze operations
    ops_analysis = analyze_operations(db_path)
    if ops_analysis.get('total_operations', 0) > 5:
        suggestions.append(Suggestion(
            suggestion_type='operations',
            priority='low',
            description=f"You have {ops_analysis['total_operations']} organization operations",
            details={
                'Total operations': ops_analysis['total_operations'],
                'Suggestion': 'Consider consolidating or cleaning old operations'
            },
            action="python file_organizer.py --show-stats"
        ))
    
    # Check for no duplicates (positive feedback)
    if dup_analysis.get('total_duplicates', 0) == 0 and dist_analysis.get('total_files', 0) > 0:
        suggestions.append(Suggestion(
            suggestion_type='positive',
            priority='low',
            description="No duplicates found - excellent file management!",
            details={
                'Total files': dist_analysis['total_files'],
                'Status': '✓ All files are unique'
            }
        ))
    
    return suggestions


# ============================================================================
# MAIN SUGGESTION INTERFACE
# ============================================================================

def print_suggestions(db_path: str = 'file_organizer.db'):
    """
    Analyze database and print suggestions to console.
    
    Args:
        db_path: Path to SQLite database
    """
    logger = logging.getLogger('FileOrganizer')
    
    logger.info("=" * 70)
    logger.info("SMART SUGGESTIONS - AI-DRIVEN FILE ORGANIZATION INSIGHTS")
    logger.info("=" * 70)
    
    if not db.database_exists(db_path):
        logger.error(f"Database not found: {db_path}")
        logger.info("Run an organization operation first to generate suggestions.")
        return
    
    # Get database stats
    stats = db.get_database_stats(db_path)
    logger.info(f"Analyzing {stats['total_files']} files across {stats['total_operations']} operations...")
    logger.info("")
    
    # Generate suggestions
    suggestions = generate_suggestions(db_path)
    
    if not suggestions:
        logger.info("No suggestions at this time. Your files are well organized!")
        logger.info("=" * 70)
        return
    
    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    suggestions.sort(key=lambda s: priority_order.get(s.priority, 3))
    
    # Print suggestions
    logger.info(f"Found {len(suggestions)} suggestions:\n")
    for i, suggestion in enumerate(suggestions, 1):
        logger.info(f"Suggestion {i}:")
        logger.info(str(suggestion))
    
    logger.info("=" * 70)


def get_detailed_analysis(db_path: str = 'file_organizer.db') -> Dict[str, Any]:
    """
    Get comprehensive analysis of all database metrics.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Dictionary with all analysis results
    """
    return {
        'distribution': analyze_file_distribution(db_path),
        'duplicates': analyze_duplicates(db_path),
        'large_files': analyze_large_files(db_path, limit=10),
        'temporal': analyze_temporal_patterns(db_path),
        'operations': analyze_operations(db_path),
        'suggestions': [
            {
                'type': s.type,
                'priority': s.priority,
                'description': s.description,
                'details': s.details,
                'action': s.action
            }
            for s in generate_suggestions(db_path)
        ]
    }
