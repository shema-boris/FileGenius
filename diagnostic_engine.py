#!/usr/bin/env python3
"""
Diagnostic Engine for Local File Organizer
System health evaluation, performance analysis, and actionable recommendations.

This module provides:
- Model confidence analysis
- Feedback accuracy evaluation
- Database integrity checks
- Performance metrics
- Actionable recommendations
- Trend analysis
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

import database_manager as db
import learning_engine as learn
import feedback_manager as feedback
import preference_manager as prefs
import maintenance_engine as maintenance


# ============================================================================
# DIAGNOSTIC THRESHOLDS
# ============================================================================

CONFIDENCE_EXCELLENT = 0.90
CONFIDENCE_GOOD = 0.75
CONFIDENCE_FAIR = 0.60
CONFIDENCE_POOR = 0.50

ACCURACY_EXCELLENT = 0.95
ACCURACY_GOOD = 0.85
ACCURACY_FAIR = 0.70
ACCURACY_POOR = 0.60


# ============================================================================
# MODEL DIAGNOSTICS
# ============================================================================

def diagnose_model_confidence(
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
) -> Dict[str, Any]:
    """
    Analyze model confidence levels in detail.
    
    Returns:
        Diagnostic report with confidence analysis
    """
    logger = logging.getLogger('FileOrganizer')
    
    report = {
        'status': 'unknown',
        'avg_confidence': 0.0,
        'confidence_distribution': {
            'excellent': 0,  # >90%
            'good': 0,       # 75-90%
            'fair': 0,       # 60-75%
            'poor': 0,       # 50-60%
            'very_poor': 0   # <50%
        },
        'patterns': [],
        'recommendations': []
    }
    
    model = learn.load_model(learning_dir)
    if not model or model.total_samples == 0:
        report['status'] = 'no_model'
        report['recommendations'].append("Train initial model with --learn")
        return report
    
    # Analyze all patterns
    all_confidences = []
    
    for file_type, destinations in model.type_to_folder.items():
        total = sum(destinations.values())
        if total == 0:
            continue
        
        max_count = max(destinations.values())
        confidence = max_count / total
        all_confidences.append(confidence)
        
        # Categorize
        if confidence >= CONFIDENCE_EXCELLENT:
            report['confidence_distribution']['excellent'] += 1
        elif confidence >= CONFIDENCE_GOOD:
            report['confidence_distribution']['good'] += 1
        elif confidence >= CONFIDENCE_FAIR:
            report['confidence_distribution']['fair'] += 1
        elif confidence >= CONFIDENCE_POOR:
            report['confidence_distribution']['poor'] += 1
        else:
            report['confidence_distribution']['very_poor'] += 1
        
        report['patterns'].append({
            'pattern': f"type:{file_type}",
            'confidence': confidence * 100,
            'samples': total
        })
    
    # Calculate average
    if all_confidences:
        avg_conf = sum(all_confidences) / len(all_confidences)
        report['avg_confidence'] = avg_conf * 100
        
        # Determine status
        if avg_conf >= CONFIDENCE_EXCELLENT:
            report['status'] = 'excellent'
        elif avg_conf >= CONFIDENCE_GOOD:
            report['status'] = 'good'
        elif avg_conf >= CONFIDENCE_FAIR:
            report['status'] = 'fair'
            report['recommendations'].append("Consider retraining to improve confidence")
        elif avg_conf >= CONFIDENCE_POOR:
            report['status'] = 'poor'
            report['recommendations'].append("RECOMMENDED: Run --relearn to retrain model")
        else:
            report['status'] = 'critical'
            report['recommendations'].append("URGENT: Model confidence is very low, retrain immediately")
    
    # Sort patterns by confidence (lowest first)
    report['patterns'].sort(key=lambda x: x['confidence'])
    
    return report


def diagnose_feedback_accuracy(
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
) -> Dict[str, Any]:
    """
    Analyze feedback accuracy and trends.
    
    Returns:
        Diagnostic report with accuracy analysis
    """
    report = {
        'status': 'unknown',
        'overall_accuracy': 0.0,
        'total_feedback': 0,
        'correct': 0,
        'wrong': 0,
        'patterns': [],
        'recommendations': []
    }
    
    stats = feedback.get_feedback_stats(learning_dir)
    
    if stats['total_feedback'] == 0:
        report['status'] = 'no_data'
        report['recommendations'].append("Enable feedback tracking with --feedback on")
        return report
    
    report['total_feedback'] = stats['total_feedback']
    report['correct'] = stats['total_correct']
    report['wrong'] = stats['total_wrong']
    
    accuracy = stats.get('overall_accuracy', 0) / 100.0
    report['overall_accuracy'] = accuracy * 100
    
    # Determine status
    if accuracy >= ACCURACY_EXCELLENT:
        report['status'] = 'excellent'
    elif accuracy >= ACCURACY_GOOD:
        report['status'] = 'good'
    elif accuracy >= ACCURACY_FAIR:
        report['status'] = 'fair'
        report['recommendations'].append("Review weak patterns")
    elif accuracy >= ACCURACY_POOR:
        report['status'] = 'poor'
        report['recommendations'].append("RECOMMENDED: Retrain or adjust preferences")
    else:
        report['status'] = 'critical'
        report['recommendations'].append("URGENT: Accuracy is very low, review system configuration")
    
    # Pattern-level accuracy
    for pattern_info in stats.get('patterns', []):
        pattern_total = pattern_info['correct'] + pattern_info['wrong']
        if pattern_total > 0:
            pattern_acc = pattern_info['correct'] / pattern_total * 100
            report['patterns'].append({
                'pattern': pattern_info['pattern'],
                'accuracy': pattern_acc,
                'correct': pattern_info['correct'],
                'wrong': pattern_info['wrong']
            })
    
    # Sort by accuracy (lowest first)
    report['patterns'].sort(key=lambda x: x['accuracy'])
    
    return report


def diagnose_database(db_path: str = 'file_organizer.db') -> Dict[str, Any]:
    """
    Check database integrity and performance.
    
    Returns:
        Diagnostic report for database
    """
    report = {
        'status': 'unknown',
        'exists': False,
        'size_mb': 0,
        'total_files': 0,
        'total_operations': 0,
        'integrity_check': 'not_performed',
        'recommendations': []
    }
    
    if not db.database_exists(db_path):
        report['status'] = 'missing'
        report['recommendations'].append("Initialize database by organizing files")
        return report
    
    report['exists'] = True
    
    # Get size
    db_size = Path(db_path).stat().st_size
    report['size_mb'] = db_size / (1024 * 1024)
    
    # Get statistics
    try:
        stats = db.get_database_stats(db_path)
        report['total_files'] = stats.get('total_files', 0)
        report['total_operations'] = stats.get('total_operations', 0)
        
        # Check integrity
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == 'ok':
            report['integrity_check'] = 'ok'
            report['status'] = 'healthy'
        else:
            report['integrity_check'] = 'failed'
            report['status'] = 'corrupted'
            report['recommendations'].append("URGENT: Database may be corrupted, backup and reinitialize")
    
    except Exception as e:
        report['status'] = 'error'
        report['integrity_check'] = f'error: {str(e)}'
        report['recommendations'].append("Database access failed, check permissions")
    
    # Performance recommendations
    if report['size_mb'] > 100:
        report['recommendations'].append("Database is large (>100MB), consider archiving old operations")
    
    if report['size_mb'] > 50:
        report['recommendations'].append("Run --optimize to improve database performance")
    
    return report


def diagnose_storage(
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
) -> Dict[str, Any]:
    """
    Analyze storage usage of learning data.
    
    Returns:
        Storage diagnostic report
    """
    report = {
        'status': 'unknown',
        'total_size_mb': 0,
        'files': {},
        'recommendations': []
    }
    
    if not learning_dir.exists():
        report['status'] = 'no_data'
        return report
    
    # Calculate sizes
    total_size = 0
    for file_path in learning_dir.rglob('*'):
        if file_path.is_file():
            size = file_path.stat().st_size
            total_size += size
            report['files'][file_path.name] = size / 1024  # KB
    
    report['total_size_mb'] = total_size / (1024 * 1024)
    
    # Determine status
    if report['total_size_mb'] < 10:
        report['status'] = 'healthy'
    elif report['total_size_mb'] < 50:
        report['status'] = 'normal'
    elif report['total_size_mb'] < 100:
        report['status'] = 'large'
        report['recommendations'].append("Consider cleaning old feedback data")
    else:
        report['status'] = 'very_large'
        report['recommendations'].append("RECOMMENDED: Archive or compress learning data")
    
    return report


# ============================================================================
# TREND ANALYSIS
# ============================================================================

def analyze_accuracy_trends(
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR,
    days: int = 30
) -> Dict[str, Any]:
    """
    Analyze accuracy trends over time.
    
    Returns:
        Trend analysis report
    """
    # For Phase 6, we'll provide basic trend info
    # Future: Track historical accuracy in maintenance log
    
    report = {
        'period_days': days,
        'trend': 'stable',  # stable, improving, declining
        'current_accuracy': 0.0,
        'change_percentage': 0.0,
        'recommendations': []
    }
    
    stats = feedback.get_feedback_stats(learning_dir)
    report['current_accuracy'] = stats.get('overall_accuracy', 0)
    
    # Placeholder for trend detection
    # Would need historical data to calculate actual trends
    
    if report['current_accuracy'] < 70:
        report['trend'] = 'declining'
        report['recommendations'].append("Accuracy is declining, investigate weak patterns")
    elif report['current_accuracy'] > 90:
        report['trend'] = 'excellent'
    else:
        report['trend'] = 'stable'
    
    return report


def analyze_confidence_trends(
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
) -> Dict[str, Any]:
    """
    Analyze confidence trends and decay effects.
    
    Returns:
        Confidence trend analysis
    """
    report = {
        'current_avg': 0.0,
        'trend': 'stable',
        'decay_impact': 'normal',
        'recommendations': []
    }
    
    model = learn.load_model(learning_dir)
    if not model or model.total_samples == 0:
        report['trend'] = 'no_data'
        return report
    
    # Calculate current average
    confidences = []
    for file_type, destinations in model.type_to_folder.items():
        total = sum(destinations.values())
        if total > 0:
            max_count = max(destinations.values())
            confidences.append(max_count / total)
    
    if confidences:
        report['current_avg'] = sum(confidences) / len(confidences) * 100
        
        if report['current_avg'] < 60:
            report['decay_impact'] = 'high'
            report['recommendations'].append("Decay may be too aggressive, consider disabling")
        elif report['current_avg'] > 95:
            report['decay_impact'] = 'low'
    
    return report


# ============================================================================
# COMPREHENSIVE DIAGNOSIS
# ============================================================================

def run_full_diagnosis(
    db_path: str = 'file_organizer.db',
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
) -> Dict[str, Any]:
    """
    Run comprehensive system diagnosis.
    
    Returns:
        Complete diagnostic report
    """
    logger = logging.getLogger('FileOrganizer')
    
    logger.info("=" * 70)
    logger.info("SYSTEM DIAGNOSTICS")
    logger.info("=" * 70)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'overall_health': 'unknown',
        'diagnostics': {}
    }
    
    # 1. Model confidence
    logger.info("\n1️⃣  Model Confidence Analysis...")
    model_diag = diagnose_model_confidence(learning_dir)
    report['diagnostics']['model'] = model_diag
    
    # 2. Feedback accuracy
    logger.info("2️⃣  Feedback Accuracy Analysis...")
    feedback_diag = diagnose_feedback_accuracy(learning_dir)
    report['diagnostics']['feedback'] = feedback_diag
    
    # 3. Database health
    logger.info("3️⃣  Database Integrity Check...")
    db_diag = diagnose_database(db_path)
    report['diagnostics']['database'] = db_diag
    
    # 4. Storage analysis
    logger.info("4️⃣  Storage Analysis...")
    storage_diag = diagnose_storage(learning_dir)
    report['diagnostics']['storage'] = storage_diag
    
    # 5. Trend analysis
    logger.info("5️⃣  Trend Analysis...")
    accuracy_trend = analyze_accuracy_trends(learning_dir)
    confidence_trend = analyze_confidence_trends(learning_dir)
    report['diagnostics']['trends'] = {
        'accuracy': accuracy_trend,
        'confidence': confidence_trend
    }
    
    # Determine overall health
    critical_issues = []
    warnings = []
    
    if model_diag['status'] in ['critical', 'poor']:
        critical_issues.append("Model confidence is low")
    elif model_diag['status'] == 'fair':
        warnings.append("Model confidence could be improved")
    
    if feedback_diag['status'] in ['critical', 'poor']:
        critical_issues.append("Feedback accuracy is low")
    elif feedback_diag['status'] == 'fair':
        warnings.append("Feedback accuracy needs attention")
    
    if db_diag['status'] == 'corrupted':
        critical_issues.append("Database integrity compromised")
    
    if storage_diag['status'] == 'very_large':
        warnings.append("Storage usage is high")
    
    # Set overall health
    if critical_issues:
        report['overall_health'] = 'critical'
    elif warnings:
        report['overall_health'] = 'needs_attention'
    else:
        report['overall_health'] = 'healthy'
    
    report['critical_issues'] = critical_issues
    report['warnings'] = warnings
    
    # Collect all recommendations
    all_recommendations = []
    for diag_type, diag_report in report['diagnostics'].items():
        if isinstance(diag_report, dict) and 'recommendations' in diag_report:
            all_recommendations.extend(diag_report['recommendations'])
        elif isinstance(diag_report, dict):
            for sub_key, sub_report in diag_report.items():
                if isinstance(sub_report, dict) and 'recommendations' in sub_report:
                    all_recommendations.extend(sub_report['recommendations'])
    
    report['recommendations'] = list(set(all_recommendations))  # Remove duplicates
    
    return report


def print_diagnosis_report(report: Dict[str, Any]):
    """Print formatted diagnosis report to console."""
    logger = logging.getLogger('FileOrganizer')
    
    logger.info("\n" + "=" * 70)
    logger.info("DIAGNOSIS SUMMARY")
    logger.info("=" * 70)
    
    # Overall health
    health_emoji = {
        'healthy': '✅',
        'needs_attention': '⚠️',
        'critical': '🔴',
        'unknown': '❓'
    }
    emoji = health_emoji.get(report['overall_health'], '❓')
    logger.info(f"\n{emoji} Overall Health: {report['overall_health'].upper()}")
    
    # Critical issues
    if report.get('critical_issues'):
        logger.info("\n🔴 CRITICAL ISSUES:")
        for issue in report['critical_issues']:
            logger.info(f"  • {issue}")
    
    # Warnings
    if report.get('warnings'):
        logger.info("\n⚠️  WARNINGS:")
        for warning in report['warnings']:
            logger.info(f"  • {warning}")
    
    # Model confidence
    model = report['diagnostics'].get('model', {})
    if model:
        logger.info("\n📊 MODEL CONFIDENCE:")
        logger.info(f"  Status: {model['status']}")
        logger.info(f"  Average: {model['avg_confidence']:.1f}%")
        logger.info("  Distribution:")
        dist = model['confidence_distribution']
        logger.info(f"    Excellent (>90%): {dist['excellent']} patterns")
        logger.info(f"    Good (75-90%): {dist['good']} patterns")
        logger.info(f"    Fair (60-75%): {dist['fair']} patterns")
        logger.info(f"    Poor (<60%): {dist['poor'] + dist['very_poor']} patterns")
    
    # Feedback accuracy
    fb = report['diagnostics'].get('feedback', {})
    if fb and fb['status'] != 'no_data':
        logger.info("\n💬 FEEDBACK ACCURACY:")
        logger.info(f"  Status: {fb['status']}")
        logger.info(f"  Overall: {fb['overall_accuracy']:.1f}%")
        logger.info(f"  Correct: {fb['correct']}")
        logger.info(f"  Wrong: {fb['wrong']}")
    
    # Database
    db_info = report['diagnostics'].get('database', {})
    if db_info:
        logger.info("\n💾 DATABASE:")
        logger.info(f"  Status: {db_info['status']}")
        logger.info(f"  Size: {db_info['size_mb']:.2f} MB")
        logger.info(f"  Files: {db_info['total_files']}")
        logger.info(f"  Operations: {db_info['total_operations']}")
        logger.info(f"  Integrity: {db_info['integrity_check']}")
    
    # Storage
    storage = report['diagnostics'].get('storage', {})
    if storage:
        logger.info("\n📁 STORAGE:")
        logger.info(f"  Status: {storage['status']}")
        logger.info(f"  Total: {storage['total_size_mb']:.2f} MB")
    
    # Recommendations
    if report.get('recommendations'):
        logger.info("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            logger.info(f"  {i}. {rec}")
    
    logger.info("\n" + "=" * 70)


# ============================================================================
# PATTERN CONFLICT DETECTION
# ============================================================================

def detect_pattern_conflicts(
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
) -> List[Dict[str, Any]]:
    """
    Detect conflicting patterns that may confuse the model.
    
    Returns:
        List of detected conflicts
    """
    conflicts = []
    
    model = learn.load_model(learning_dir)
    if not model:
        return conflicts
    
    # Check for patterns with low confidence (conflicting destinations)
    for file_type, destinations in model.type_to_folder.items():
        total = sum(destinations.values())
        if total < 5:  # Skip patterns with too few samples
            continue
        
        # Get top 2 destinations
        top_dests = destinations.most_common(2)
        if len(top_dests) >= 2:
            first_count = top_dests[0][1]
            second_count = top_dests[1][1]
            
            # If second destination has >30% of samples, it's a conflict
            if second_count / total > 0.3:
                conflicts.append({
                    'pattern': f"type:{file_type}",
                    'primary_dest': top_dests[0][0],
                    'primary_count': first_count,
                    'conflict_dest': top_dests[1][0],
                    'conflict_count': second_count,
                    'confidence': first_count / total * 100
                })
    
    return conflicts
