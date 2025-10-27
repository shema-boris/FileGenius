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
    
    # Build report
    report = {
        'report_metadata': {
            'generated_at': datetime.now().isoformat(),
            'database_path': db_path,
            'report_version': '3.0'
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
                'action': s.action
            }
            for s in suggestions
        ]
    }
    
    return report


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
