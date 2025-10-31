#!/usr/bin/env python3
"""
Insight Engine for Local File Organizer
Generates natural-language summaries and actionable insights.

This module provides:
- Weekly/monthly performance summaries
- Trend detection and analysis
- Actionable recommendations
- Natural language insights
- Confidence trend analysis
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

import database_manager as db
import learning_engine as learn
import feedback_manager as feedback
import maintenance_engine as maintenance
import diagnostic_engine as diagnostic


# ============================================================================
# INSIGHT GENERATION
# ============================================================================

def generate_weekly_summary(
    db_path: str = 'file_organizer.db',
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
) -> Dict[str, Any]:
    """
    Generate weekly performance summary.
    
    Args:
        db_path: Database path
        learning_dir: Learning data directory
        
    Returns:
        Summary dictionary with insights
    """
    summary = {
        'period': 'week',
        'generated_at': datetime.now().isoformat(),
        'insights': [],
        'stats': {},
        'recommendations': []
    }
    
    # Get current metrics
    model = learn.load_model(learning_dir)
    fb_stats = feedback.get_feedback_stats(learning_dir)
    mlog = maintenance.MaintenanceLog(learning_dir)
    
    # Model insights
    if model and model.total_samples > 0:
        # Calculate average confidence
        confidences = []
        for file_type, destinations in model.type_to_folder.items():
            total = sum(destinations.values())
            if total > 0:
                max_count = max(destinations.values())
                confidences.append((max_count / total) * 100)
        
        if confidences:
            avg_conf = sum(confidences) / len(confidences)
            summary['stats']['avg_confidence'] = avg_conf
            summary['stats']['total_patterns'] = len(confidences)
            summary['stats']['total_samples'] = model.total_samples
            
            # Insight: Model confidence
            if avg_conf >= 90:
                summary['insights'].append(
                    f"⭐ Excellent! Model confidence is very high at {avg_conf:.1f}%"
                )
            elif avg_conf >= 75:
                summary['insights'].append(
                    f"✓ Model confidence is good at {avg_conf:.1f}%"
                )
            elif avg_conf >= 60:
                summary['insights'].append(
                    f"⚠️  Model confidence is fair at {avg_conf:.1f}% - consider retraining"
                )
            else:
                summary['insights'].append(
                    f"🔴 Model confidence is low at {avg_conf:.1f}% - retrain recommended"
                )
                summary['recommendations'].append("Run --relearn to retrain the model")
    else:
        summary['insights'].append("ℹ️  No trained model found")
        summary['recommendations'].append("Run --learn to train the model")
    
    # Feedback insights
    if fb_stats['total_feedback'] > 0:
        accuracy = fb_stats.get('overall_accuracy', 0)
        summary['stats']['feedback_accuracy'] = accuracy
        summary['stats']['total_feedback'] = fb_stats['total_feedback']
        
        if accuracy >= 90:
            summary['insights'].append(
                f"📈 Accuracy is excellent at {accuracy:.1f}%"
            )
        elif accuracy >= 75:
            summary['insights'].append(
                f"✓ Accuracy is good at {accuracy:.1f}%"
            )
        elif accuracy >= 60:
            summary['insights'].append(
                f"⚠️  Accuracy needs improvement: {accuracy:.1f}%"
            )
        else:
            summary['insights'].append(
                f"🔴 Accuracy is low: {accuracy:.1f}% - review patterns"
            )
            summary['recommendations'].append("Review weak patterns and retrain")
    
    # Maintenance insights
    recent_ops = mlog.get_operations_since(hours=168)  # Last week
    if recent_ops:
        summary['stats']['maintenance_operations'] = len(recent_ops)
        
        # Count retrains
        retrains = [op for op in recent_ops if op['type'] == 'retrain']
        if len(retrains) > 2:
            summary['insights'].append(
                f"⚙️  Model retrained {len(retrains)} times this week - possible instability"
            )
            summary['recommendations'].append("Check for conflicting patterns")
        elif len(retrains) == 1:
            summary['insights'].append(
                "🔄 Model retrained once this week - keeping fresh"
            )
    
    # Database insights
    if db.database_exists(db_path):
        db_stats = db.get_database_stats(db_path)
        summary['stats']['total_files'] = db_stats['total_files']
        summary['stats']['total_operations'] = db_stats['total_operations']
        
        db_diag = diagnostic.diagnose_database(db_path)
        if db_diag['size_mb'] > 50:
            summary['insights'].append(
                f"💾 Database is getting large ({db_diag['size_mb']:.1f} MB)"
            )
            summary['recommendations'].append("Run --optimize to clean up database")
    
    return summary


def generate_cumulative_summary(
    db_path: str = 'file_organizer.db',
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
) -> Dict[str, Any]:
    """
    Generate cumulative all-time summary.
    
    Args:
        db_path: Database path
        learning_dir: Learning data directory
        
    Returns:
        Summary dictionary with insights
    """
    summary = {
        'period': 'all_time',
        'generated_at': datetime.now().isoformat(),
        'insights': [],
        'stats': {},
        'milestones': []
    }
    
    # Learning stats
    model = learn.load_model(learning_dir)
    if model:
        summary['stats']['total_samples'] = model.total_samples
        summary['stats']['file_types_learned'] = len(model.type_to_folder)
        summary['stats']['extensions_learned'] = len(model.ext_to_folder)
        
        # Milestones
        if model.total_samples >= 1000:
            summary['milestones'].append("🏆 1,000+ samples learned!")
        elif model.total_samples >= 500:
            summary['milestones'].append("🎯 500+ samples learned")
        elif model.total_samples >= 100:
            summary['milestones'].append("✨ 100+ samples learned")
    
    # Feedback stats
    fb_stats = feedback.get_feedback_stats(learning_dir)
    if fb_stats['total_feedback'] > 0:
        summary['stats']['total_feedback'] = fb_stats['total_feedback']
        summary['stats']['overall_accuracy'] = fb_stats['overall_accuracy']
        
        if fb_stats['total_feedback'] >= 100:
            summary['milestones'].append("📊 100+ feedback events recorded")
    
    # Maintenance stats
    mlog = maintenance.MaintenanceLog(learning_dir)
    maint_stats = mlog.log['stats']
    summary['stats']['total_retrains'] = maint_stats['total_retrains']
    summary['stats']['total_optimizations'] = maint_stats['total_optimizations']
    summary['stats']['patterns_pruned'] = maint_stats['patterns_pruned']
    
    # Database stats
    if db.database_exists(db_path):
        db_stats = db.get_database_stats(db_path)
        summary['stats']['total_files_organized'] = db_stats['total_files']
        summary['stats']['total_operations'] = db_stats['total_operations']
        
        # Milestones
        if db_stats['total_files'] >= 10000:
            summary['milestones'].append("🎉 10,000+ files organized!")
        elif db_stats['total_files'] >= 1000:
            summary['milestones'].append("🎊 1,000+ files organized")
    
    return summary


def detect_trends(
    db_path: str = 'file_organizer.db',
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
) -> Dict[str, Any]:
    """
    Detect trends in model performance and accuracy.
    
    Args:
        db_path: Database path
        learning_dir: Learning data directory
        
    Returns:
        Trends dictionary
    """
    trends = {
        'confidence_trend': 'stable',
        'accuracy_trend': 'stable',
        'usage_trend': 'stable',
        'insights': []
    }
    
    # Get current metrics
    model_diag = diagnostic.diagnose_model_confidence(learning_dir)
    fb_diag = diagnostic.diagnose_feedback_accuracy(learning_dir)
    
    # Analyze confidence trend
    if model_diag['status'] != 'no_model':
        avg_conf = model_diag['avg_confidence']
        
        if avg_conf >= 90:
            trends['confidence_trend'] = 'excellent'
            trends['insights'].append("Confidence levels are excellent and stable")
        elif avg_conf >= 75:
            trends['confidence_trend'] = 'good'
        elif avg_conf < 60:
            trends['confidence_trend'] = 'declining'
            trends['insights'].append("⚠️  Confidence is declining - retrain recommended")
    
    # Analyze accuracy trend
    if fb_diag['status'] != 'no_data':
        accuracy = fb_diag['overall_accuracy']
        
        if accuracy >= 90:
            trends['accuracy_trend'] = 'excellent'
            trends['insights'].append("Prediction accuracy is excellent")
        elif accuracy >= 75:
            trends['accuracy_trend'] = 'good'
        elif accuracy < 65:
            trends['accuracy_trend'] = 'declining'
            trends['insights'].append("⚠️  Accuracy is declining - review patterns")
    
    return trends


def generate_predictive_insights(
    db_path: str = 'file_organizer.db',
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
) -> List[str]:
    """
    Generate predictive insights about future actions.
    
    Args:
        db_path: Database path
        learning_dir: Learning data directory
        
    Returns:
        List of predictive insights
    """
    insights = []
    
    # Check if maintenance will be needed soon
    health = maintenance.check_model_health(db_path, learning_dir)
    
    if health['overall_status'] == 'needs_attention':
        insights.append("🔮 Prediction: Maintenance will be needed within 1-2 days")
    elif health['overall_status'] == 'degraded':
        insights.append("🔮 Prediction: Immediate maintenance recommended")
    
    # Check database size trend
    if db.database_exists(db_path):
        db_diag = diagnostic.diagnose_database(db_path)
        if db_diag['size_mb'] > 40:
            insights.append("🔮 Prediction: Database will need optimization soon")
    
    # Check pattern growth
    model = learn.load_model(learning_dir)
    if model:
        weak_patterns = sum(
            1 for _, dests in model.type_to_folder.items()
            if sum(dests.values()) < 5
        )
        
        if weak_patterns > 5:
            insights.append(f"🔮 Prediction: {weak_patterns} weak patterns may be pruned next optimization")
    
    return insights


# ============================================================================
# FORMATTED OUTPUT
# ============================================================================

def print_weekly_insights(
    db_path: str = 'file_organizer.db',
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
):
    """Print formatted weekly insights."""
    logger = logging.getLogger('FileOrganizer')
    
    summary = generate_weekly_summary(db_path, learning_dir)
    
    logger.info("=" * 70)
    logger.info("📊 WEEKLY PERFORMANCE SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Generated: {summary['generated_at'][:10]}")
    logger.info("")
    
    # Show insights
    if summary['insights']:
        logger.info("Key Insights:")
        for insight in summary['insights']:
            logger.info(f"  {insight}")
        logger.info("")
    
    # Show stats
    if summary['stats']:
        logger.info("Statistics:")
        for key, value in summary['stats'].items():
            key_formatted = key.replace('_', ' ').title()
            if isinstance(value, float):
                logger.info(f"  {key_formatted}: {value:.1f}")
            else:
                logger.info(f"  {key_formatted}: {value}")
        logger.info("")
    
    # Show recommendations
    if summary['recommendations']:
        logger.info("💡 Recommendations:")
        for i, rec in enumerate(summary['recommendations'], 1):
            logger.info(f"  {i}. {rec}")
        logger.info("")
    
    logger.info("=" * 70)


def print_cumulative_insights(
    db_path: str = 'file_organizer.db',
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
):
    """Print formatted cumulative insights."""
    logger = logging.getLogger('FileOrganizer')
    
    summary = generate_cumulative_summary(db_path, learning_dir)
    
    logger.info("=" * 70)
    logger.info("🏆 CUMULATIVE PERFORMANCE SUMMARY")
    logger.info("=" * 70)
    logger.info("")
    
    # Show milestones
    if summary['milestones']:
        logger.info("Milestones Achieved:")
        for milestone in summary['milestones']:
            logger.info(f"  {milestone}")
        logger.info("")
    
    # Show stats
    if summary['stats']:
        logger.info("All-Time Statistics:")
        for key, value in summary['stats'].items():
            key_formatted = key.replace('_', ' ').title()
            if isinstance(value, float):
                logger.info(f"  {key_formatted}: {value:.1f}")
            else:
                logger.info(f"  {key_formatted}: {value}")
        logger.info("")
    
    logger.info("=" * 70)


def print_smart_insights(
    db_path: str = 'file_organizer.db',
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
):
    """Print comprehensive smart insights."""
    logger = logging.getLogger('FileOrganizer')
    
    logger.info("=" * 70)
    logger.info("🧠 SMART INSIGHTS & ANALYSIS")
    logger.info("=" * 70)
    logger.info("")
    
    # Weekly summary
    weekly = generate_weekly_summary(db_path, learning_dir)
    
    logger.info("📈 This Week:")
    for insight in weekly['insights']:
        logger.info(f"  {insight}")
    logger.info("")
    
    # Trends
    trends = detect_trends(db_path, learning_dir)
    
    logger.info("📊 Trends:")
    logger.info(f"  Confidence: {trends['confidence_trend']}")
    logger.info(f"  Accuracy: {trends['accuracy_trend']}")
    for insight in trends['insights']:
        logger.info(f"  {insight}")
    logger.info("")
    
    # Predictions
    predictions = generate_predictive_insights(db_path, learning_dir)
    
    if predictions:
        logger.info("🔮 Predictions:")
        for pred in predictions:
            logger.info(f"  {pred}")
        logger.info("")
    
    # Recommendations
    if weekly['recommendations']:
        logger.info("💡 Action Items:")
        for i, rec in enumerate(weekly['recommendations'], 1):
            logger.info(f"  {i}. {rec}")
        logger.info("")
    
    logger.info("=" * 70)


def generate_insight_report(
    db_path: str = 'file_organizer.db',
    learning_dir: Path = maintenance.DEFAULT_LEARNING_DIR
) -> Dict[str, Any]:
    """
    Generate comprehensive insight report.
    
    Returns:
        Complete insight report
    """
    return {
        'generated_at': datetime.now().isoformat(),
        'weekly_summary': generate_weekly_summary(db_path, learning_dir),
        'cumulative_summary': generate_cumulative_summary(db_path, learning_dir),
        'trends': detect_trends(db_path, learning_dir),
        'predictions': generate_predictive_insights(db_path, learning_dir)
    }
