#!/usr/bin/env python3
"""
Report Generator for Local File Organizer
Creates detailed reports and exports data in various formats.

Supports:
- CSV export
- JSON export
- Console-friendly summaries
- Statistics and insights
"""

import json
import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

import database_manager as db
import suggestion_engine as suggest
import learning_engine as learn
import feedback_manager as feedback
import maintenance_engine as maintenance
import diagnostic_engine as diagnostic


# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_report_data(db_path: str = 'file_organizer.db') -> Dict[str, Any]:
    """
    Generate comprehensive report data from database.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Dictionary with all report data
    """
    logger = logging.getLogger('FileOrganizer')
    
    if not db.database_exists(db_path):
        logger.error(f"Database not found: {db_path}")
        return {}
    
    # Get all analyses
    stats = db.get_database_stats(db_path)
    distribution = suggest.analyze_file_distribution(db_path)
    duplicates = suggest.analyze_duplicates(db_path)
    large_files = suggest.analyze_large_files(db_path, limit=10)
    temporal = suggest.analyze_temporal_patterns(db_path)
    operations = suggest.analyze_operations(db_path)
    suggestions = suggest.generate_suggestions(db_path)
    
    # Phase 5: Get learning and feedback analytics
    learning_analytics = _get_learning_analytics()
    feedback_analytics = _get_feedback_analytics()
    
    # Phase 6: Get diagnostics and maintenance analytics
    diagnostics = _get_diagnostic_analytics(db_path)
    maintenance_history = _get_maintenance_analytics()
    
    # Build report
    report = {
        'report_metadata': {
            'generated_at': datetime.now().isoformat(),
            'database_path': db_path,
            'report_version': '6.0'  # Updated to Phase 6
        },
        'summary': {
            'total_files': stats['total_files'],
            'total_size_mb': stats['total_size_mb'],
            'total_size_bytes': stats['total_size_bytes'],
            'total_operations': stats['total_operations'],
            'file_categories': len(stats['files_by_type'])
        },
        'file_distribution': {
            'by_type': stats['files_by_type'],
            'percentages': distribution.get('distribution', {})
        },
        'duplicates': {
            'total_duplicate_groups': duplicates.get('duplicate_groups', 0),
            'total_duplicate_files': duplicates.get('total_duplicates', 0),
            'wasted_space_mb': duplicates.get('wasted_space_mb', 0),
            'wasted_space_bytes': duplicates.get('wasted_space_bytes', 0),
            'details': duplicates.get('details', [])
        },
        'large_files': {
            'top_10': large_files
        },
        'temporal_analysis': temporal,
        'operations_history': operations,
        'suggestions': [
            {
                'type': s.type,
                'priority': s.priority,
                'description': s.description,
                'details': s.details,
                'action': s.action,
                'confidence': s.confidence,
                'reason': s.reason
            }
            for s in suggestions
        ],
        # Phase 5: Learning and feedback insights
        'learning_insights': learning_analytics,
        'feedback_insights': feedback_analytics,
        # Phase 6: Diagnostics and maintenance
        'system_diagnostics': diagnostics,
        'maintenance_history': maintenance_history
    }
    
    return report


# ============================================================================
# PHASE 5: LEARNING & FEEDBACK ANALYTICS
# ============================================================================

def _get_learning_analytics() -> Dict[str, Any]:
    """
    Get learning model analytics for report.
    
    Returns:
        Dictionary with learning insights
    """
    try:
        model = learn.load_model()
        
        if not model or model.total_samples == 0:
            return {
                'enabled': False,
                'status': 'No learning data available',
                'total_samples': 0
            }
        
        stats = learn.get_learning_stats(model)
        
        # Calculate pattern strengths
        pattern_strengths = []
        
        # Type patterns
        for file_type, destinations in model.type_to_folder.items():
            total_count = sum(destinations.values())
            most_common = destinations.most_common(1)
            if most_common:
                dest, count = most_common[0]
                confidence = (count / total_count) * 100
                pattern_strengths.append({
                    'pattern': f'type:{file_type}',
                    'destination': dest,
                    'confidence': confidence,
                    'sample_count': total_count
                })
        
        # Extension patterns
        for ext, destinations in model.ext_to_folder.items():
            total_count = sum(destinations.values())
            most_common = destinations.most_common(1)
            if most_common:
                dest, count = most_common[0]
                confidence = (count / total_count) * 100
                pattern_strengths.append({
                    'pattern': f'ext:{ext}',
                    'destination': dest,
                    'confidence': confidence,
                    'sample_count': total_count
                })
        
        # Sort by confidence
        pattern_strengths.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Calculate average confidence
        avg_confidence = sum(p['confidence'] for p in pattern_strengths) / len(pattern_strengths) if pattern_strengths else 0
        
        # Find strongest and weakest patterns
        strongest = pattern_strengths[0] if pattern_strengths else None
        weakest = pattern_strengths[-1] if pattern_strengths else None
        
        return {
            'enabled': True,
            'status': 'Active',
            'total_samples': stats['total_samples'],
            'file_types_learned': stats['file_types_learned'],
            'extensions_learned': stats['extensions_learned'],
            'last_trained': stats['last_trained'],
            'average_confidence': avg_confidence,
            'strongest_pattern': strongest,
            'weakest_pattern': weakest,
            'top_patterns': pattern_strengths[:10]
        }
    
    except Exception as e:
        return {
            'enabled': False,
            'status': f'Error: {str(e)}',
            'total_samples': 0
        }


def _get_feedback_analytics() -> Dict[str, Any]:
    """
    Get feedback reinforcement analytics for report.
    
    Returns:
        Dictionary with feedback insights
    """
    try:
        feedback_stats = feedback.get_feedback_stats()
        
        if feedback_stats['total_feedback'] == 0:
            return {
                'enabled': feedback_stats['enabled'],
                'status': 'No feedback data available',
                'total_feedback': 0
            }
        
        return {
            'enabled': feedback_stats['enabled'],
            'status': 'Active',
            'total_feedback': feedback_stats['total_feedback'],
            'total_correct': feedback_stats['total_correct'],
            'total_wrong': feedback_stats['total_wrong'],
            'overall_accuracy': feedback_stats['overall_accuracy'],
            'strongest_pattern': feedback_stats['strongest_pattern'],
            'weakest_pattern': feedback_stats['weakest_pattern'],
            'top_patterns': feedback_stats['patterns'][:10],
            'last_updated': feedback_stats['last_updated']
        }
    
    except Exception as e:
        return {
            'enabled': False,
            'status': f'Error: {str(e)}',
            'total_feedback': 0
        }


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_to_json(report_data: Dict[str, Any], output_path: str) -> bool:
    """
    Export report data to JSON file.
    
    Args:
        report_data: Report data dictionary
        output_path: Path to output JSON file
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        output_file = Path(output_path)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON report exported: {output_file}")
        logger.info(f"File size: {output_file.stat().st_size} bytes")
        return True
    
    except Exception as e:
        logger.error(f"Failed to export JSON report: {e}")
        return False


def export_to_csv(report_data: Dict[str, Any], output_path: str) -> bool:
    """
    Export report data to CSV file.
    Creates multiple CSV files for different data sections.
    
    Args:
        report_data: Report data dictionary
        output_path: Path to output CSV file (base name)
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger('FileOrganizer')
    
    try:
        output_file = Path(output_path)
        base_name = output_file.stem
        output_dir = output_file.parent
        
        # Export summary
        summary_file = output_dir / f"{base_name}_summary.csv"
        with open(summary_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            for key, value in report_data['summary'].items():
                writer.writerow([key, value])
        logger.info(f"Summary exported: {summary_file}")
        
        # Export file distribution
        dist_file = output_dir / f"{base_name}_distribution.csv"
        with open(dist_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['File Type', 'Count', 'Percentage'])
            for file_type, data in report_data['file_distribution']['percentages'].items():
                writer.writerow([
                    file_type,
                    data['count'],
                    f"{data['percentage']}%"
                ])
        logger.info(f"Distribution exported: {dist_file}")
        
        # Export large files
        if report_data['large_files']['top_10']:
            large_file = output_dir / f"{base_name}_large_files.csv"
            with open(large_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['File Name', 'Size (MB)', 'Type', 'Path'])
                for file_info in report_data['large_files']['top_10']:
                    writer.writerow([
                        file_info['file_name'],
                        file_info['file_size_mb'],
                        file_info['file_type'],
                        file_info['path']
                    ])
            logger.info(f"Large files exported: {large_file}")
        
        # Export duplicates
        if report_data['duplicates']['details']:
            dup_file = output_dir / f"{base_name}_duplicates.csv"
            with open(dup_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['File Name', 'Duplicate Count', 'Size (MB)', 'Wasted Space (MB)'])
                for dup_info in report_data['duplicates']['details']:
                    writer.writerow([
                        dup_info['file_name'],
                        dup_info['count'],
                        round(dup_info['size_bytes'] / (1024 * 1024), 2),
                        round(dup_info['wasted_bytes'] / (1024 * 1024), 2)
                    ])
            logger.info(f"Duplicates exported: {dup_file}")
        
        # Export operations
        if report_data['operations_history']['operations']:
            ops_file = output_dir / f"{base_name}_operations.csv"
            with open(ops_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Operation ID', 'Date', 'Files Moved'])
                for op in report_data['operations_history']['operations']:
                    writer.writerow([
                        op['operation_id'],
                        op['operation_date'],
                        op['file_count']
                    ])
            logger.info(f"Operations exported: {ops_file}")
        
        logger.info(f"CSV reports exported to: {output_dir}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to export CSV report: {e}")
        return False


# ============================================================================
# PHASE 6: DIAGNOSTICS & MAINTENANCE ANALYTICS
# ============================================================================

def _get_diagnostic_analytics(db_path: str = 'file_organizer.db') -> Dict[str, Any]:
    """
    Get system diagnostics for report.
    
    Returns:
        Dictionary with diagnostic results
    """
    try:
        # Run lightweight diagnostics
        model_diag = diagnostic.diagnose_model_confidence()
        feedback_diag = diagnostic.diagnose_feedback_accuracy()
        db_diag = diagnostic.diagnose_database(db_path)
        storage_diag = diagnostic.diagnose_storage()
        
        # Determine overall health
        critical_count = sum([
            1 for d in [model_diag, feedback_diag, db_diag]
            if d.get('status') in ['critical', 'poor', 'corrupted']
        ])
        
        overall = 'healthy'
        if critical_count > 0:
            overall = 'critical'
        elif any(d.get('status') == 'fair' for d in [model_diag, feedback_diag]):
            overall = 'needs_attention'
        
        return {
            'enabled': True,
            'overall_health': overall,
            'model': {
                'status': model_diag['status'],
                'avg_confidence': model_diag['avg_confidence'],
                'patterns_count': len(model_diag['patterns'])
            },
            'feedback': {
                'status': feedback_diag['status'],
                'overall_accuracy': feedback_diag.get('overall_accuracy', 0),
                'total_feedback': feedback_diag['total_feedback']
            },
            'database': {
                'status': db_diag['status'],
                'size_mb': db_diag['size_mb'],
                'integrity': db_diag['integrity_check']
            },
            'storage': {
                'status': storage_diag['status'],
                'total_size_mb': storage_diag['total_size_mb']
            }
        }
    
    except Exception as e:
        return {
            'enabled': False,
            'error': str(e)
        }


def _get_maintenance_analytics() -> Dict[str, Any]:
    """
    Get maintenance history for report.
    
    Returns:
        Dictionary with maintenance statistics
    """
    try:
        mlog = maintenance.MaintenanceLog()
        
        recent_ops = mlog.get_operations_since(hours=24)
        
        return {
            'enabled': True,
            'last_maintenance': mlog.get_last_maintenance(),
            'stats': mlog.log['stats'],
            'recent_operations': len(recent_ops),
            'operations_last_24h': recent_ops
        }
    
    except Exception as e:
        return {
            'enabled': False,
            'error': str(e)
        }


# ============================================================================
# CONSOLE REPORTING
# ============================================================================

def print_summary_report(report_data: Dict[str, Any]):
    """
    Print a human-readable summary report to console.
    
    Args:
        report_data: Report data dictionary
    """
    logger = logging.getLogger('FileOrganizer')
    
    logger.info("=" * 70)
    logger.info("FILE ORGANIZER - COMPREHENSIVE REPORT")
    logger.info("=" * 70)
    logger.info(f"Generated: {report_data['report_metadata']['generated_at']}")
    logger.info("")
    
    # Summary
    summary = report_data['summary']
    logger.info("📊 SUMMARY")
    logger.info("-" * 70)
    logger.info(f"Total Files Tracked: {summary['total_files']}")
    logger.info(f"Total Size: {summary['total_size_mb']} MB ({summary['total_size_bytes']} bytes)")
    logger.info(f"Total Operations: {summary['total_operations']}")
    logger.info(f"File Categories: {summary['file_categories']}")
    logger.info("")
    
    # File Distribution
    logger.info("📁 FILE DISTRIBUTION")
    logger.info("-" * 70)
    for file_type, data in report_data['file_distribution']['percentages'].items():
        bar_length = int(data['percentage'] / 2)  # Scale to 50 chars max
        bar = '█' * bar_length
        logger.info(f"{file_type:15s} {bar} {data['percentage']:5.1f}% ({data['count']} files)")
    logger.info("")
    
    # Duplicates
    dup_info = report_data['duplicates']
    if dup_info['total_duplicate_files'] > 0:
        logger.info("🔄 DUPLICATES")
        logger.info("-" * 70)
        logger.info(f"Duplicate Groups: {dup_info['total_duplicate_groups']}")
        logger.info(f"Total Duplicate Files: {dup_info['total_duplicate_files']}")
        logger.info(f"Wasted Space: {dup_info['wasted_space_mb']} MB")
        logger.info("")
        
        if dup_info['details']:
            logger.info("Top duplicate files:")
            for i, dup in enumerate(dup_info['details'][:5], 1):
                size_mb = round(dup['wasted_bytes'] / (1024 * 1024), 2)
                logger.info(f"  {i}. {dup['file_name']} - {dup['count']} copies, wastes {size_mb} MB")
            logger.info("")
    
    # Large Files
    large_files = report_data['large_files']['top_10']
    if large_files:
        logger.info("📦 LARGEST FILES (Top 10)")
        logger.info("-" * 70)
        for i, file_info in enumerate(large_files, 1):
            logger.info(f"{i:2d}. {file_info['file_name']:40s} {file_info['file_size_mb']:8.2f} MB ({file_info['file_type']})")
        logger.info("")
    
    # Temporal Analysis
    temporal = report_data['temporal_analysis']
    if temporal.get('years'):
        logger.info("📅 TEMPORAL DISTRIBUTION")
        logger.info("-" * 70)
        logger.info("Files by year:")
        for year, count in sorted(temporal['years'].items(), reverse=True):
            logger.info(f"  {year}: {count} files")
        logger.info("")
    
    # Operations
    operations = report_data['operations_history']
    if operations['total_operations'] > 0:
        logger.info("🔧 RECENT OPERATIONS")
        logger.info("-" * 70)
        logger.info(f"Total: {operations['total_operations']} operations")
        if operations['operations']:
            logger.info("Most recent:")
            for op in operations['operations'][:5]:
                logger.info(f"  • {op['operation_id'][:30]}... - {op['file_count']} files ({op['operation_date'][:10]})")
            logger.info("")
    
    # Phase 5: Learning Insights
    learning_insights = report_data.get('learning_insights', {})
    if learning_insights.get('enabled'):
        logger.info("🧠 LEARNING INSIGHTS")
        logger.info("-" * 70)
        logger.info(f"Status: {learning_insights['status']}")
        logger.info(f"Training Samples: {learning_insights['total_samples']}")
        logger.info(f"Average Confidence: {learning_insights.get('average_confidence', 0):.1f}%")
        logger.info("")
        
        strongest = learning_insights.get('strongest_pattern')
        if strongest:
            logger.info(f"Strongest Pattern: {strongest['pattern']} → {strongest['destination']}")
            logger.info(f"  Confidence: {strongest['confidence']:.1f}% ({strongest['sample_count']} samples)")
        
        weakest = learning_insights.get('weakest_pattern')
        if weakest and learning_insights.get('file_types_learned', 0) > 1:
            logger.info(f"Weakest Pattern: {weakest['pattern']} → {weakest['destination']}")
            logger.info(f"  Confidence: {weakest['confidence']:.1f}% ({weakest['sample_count']} samples)")
        
        logger.info("")
    
    # Phase 5: Feedback Insights
    feedback_insights = report_data.get('feedback_insights', {})
    if feedback_insights.get('enabled') and feedback_insights.get('total_feedback', 0) > 0:
        logger.info("📊 FEEDBACK INSIGHTS")
        logger.info("-" * 70)
        logger.info(f"Overall Accuracy: {feedback_insights['overall_accuracy']:.1f}%")
        logger.info(f"Total Feedback Events: {feedback_insights['total_feedback']}")
        logger.info(f"  ✓ Correct: {feedback_insights['total_correct']}")
        logger.info(f"  ✗ Wrong: {feedback_insights['total_wrong']}")
        logger.info("")
    
    # Phase 6: System Diagnostics
    diagnostics = report_data.get('system_diagnostics', {})
    if diagnostics.get('enabled'):
        logger.info("🔍 SYSTEM HEALTH")
        logger.info("-" * 70)
        
        health_emoji = {'healthy': '✅', 'needs_attention': '⚠️', 'critical': '🔴'}
        emoji = health_emoji.get(diagnostics['overall_health'], '❓')
        logger.info(f"{emoji} Overall Health: {diagnostics['overall_health'].upper()}")
        
        model_status = diagnostics['model']
        logger.info(f"  Model: {model_status['status']} ({model_status['avg_confidence']:.1f}% avg confidence)")
        
        db_status = diagnostics['database']
        logger.info(f"  Database: {db_status['status']} ({db_status['size_mb']:.2f} MB, {db_status['integrity']})")
        
        logger.info("")
    
    # Phase 6: Maintenance History
    maintenance_history = report_data.get('maintenance_history', {})
    if maintenance_history.get('enabled'):
        logger.info("🔧 MAINTENANCE")
        logger.info("-" * 70)
        
        last_maint = maintenance_history.get('last_maintenance')
        if last_maint:
            logger.info(f"Last Maintenance: {last_maint[:19]}")
        else:
            logger.info("Last Maintenance: Never")
        
        stats = maintenance_history.get('stats', {})
        logger.info(f"Total Retrains: {stats.get('total_retrains', 0)}")
        logger.info(f"Total Optimizations: {stats.get('total_optimizations', 0)}")
        logger.info(f"Patterns Pruned: {stats.get('patterns_pruned', 0)}")
        logger.info("")
    
    # Suggestions
    suggestions = report_data['suggestions']
    if suggestions:
        logger.info("💡 SUGGESTIONS")
        logger.info("-" * 70)
        for i, sugg in enumerate(suggestions, 1):
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
            emoji = priority_emoji.get(sugg['priority'], '⚪')
            logger.info(f"{i}. {emoji} [{sugg['priority'].upper()}] {sugg['description']}")
        logger.info("")
    
    logger.info("=" * 70)


# ============================================================================
# MAIN REPORT INTERFACE
# ============================================================================

def generate_report(output_path: str, db_path: str = 'file_organizer.db', 
                   print_console: bool = True) -> bool:
    """
    Generate and export a comprehensive report.
    
    Args:
        output_path: Path to output file (extension determines format)
        db_path: Path to SQLite database
        print_console: Whether to print summary to console
        
    Returns:
        True if successful, False otherwise
    """
    logger = logging.getLogger('FileOrganizer')
    
    logger.info("=" * 70)
    logger.info("GENERATING REPORT")
    logger.info("=" * 70)
    
    # Generate report data
    logger.info("Analyzing database...")
    report_data = generate_report_data(db_path)
    
    if not report_data:
        logger.error("Failed to generate report data")
        return False
    
    # Determine format from extension
    output_file = Path(output_path)
    extension = output_file.suffix.lower()
    
    success = False
    
    if extension == '.json':
        success = export_to_json(report_data, output_path)
    elif extension == '.csv':
        success = export_to_csv(report_data, output_path)
    else:
        logger.error(f"Unsupported format: {extension}. Use .json or .csv")
        return False
    
    # Print console summary
    if print_console and success:
        logger.info("")
        print_summary_report(report_data)
    
    if success:
        logger.info(f"✓ Report generated successfully: {output_path}")
    
    return success


def quick_summary(db_path: str = 'file_organizer.db'):
    """
    Print a quick summary report to console.
    
    Args:
        db_path: Path to SQLite database
    """
    report_data = generate_report_data(db_path)
    if report_data:
        print_summary_report(report_data)
