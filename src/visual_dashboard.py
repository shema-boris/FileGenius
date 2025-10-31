#!/usr/bin/env python3
"""
Visual Dashboard for Local File Organizer
ASCII-based CLI dashboard with charts, trends, and insights.

This module provides:
- ASCII bar charts and histograms
- Trend line visualizations
- Confidence distribution charts
- Pattern strength heatmaps
- Real-time dashboard display
- 100% offline, zero external dependencies
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict

import database_manager as db
import learning_engine as learn
import feedback_manager as feedback
import maintenance_engine as maintenance
import diagnostic_engine as diagnostic


# ============================================================================
# ASCII CHART COMPONENTS
# ============================================================================

def create_bar_chart(
    data: Dict[str, float],
    max_width: int = 50,
    show_values: bool = True,
    bar_char: str = '█'
) -> List[str]:
    """
    Create ASCII horizontal bar chart.
    
    Args:
        data: Dictionary of {label: value}
        max_width: Maximum width of bars
        show_values: Show numeric values at end of bars
        bar_char: Character to use for bars
        
    Returns:
        List of chart lines
    """
    if not data:
        return ["No data available"]
    
    lines = []
    max_value = max(data.values()) if data.values() else 1
    
    # Find longest label for alignment
    max_label_len = max(len(str(label)) for label in data.keys())
    
    for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        # Calculate bar length
        if max_value > 0:
            bar_length = int((value / max_value) * max_width)
        else:
            bar_length = 0
        
        # Create bar
        bar = bar_char * bar_length
        
        # Format line
        label_padded = str(label).ljust(max_label_len)
        
        if show_values:
            if isinstance(value, float):
                value_str = f"{value:.1f}"
            else:
                value_str = str(value)
            line = f"{label_padded} │ {bar} {value_str}"
        else:
            line = f"{label_padded} │ {bar}"
        
        lines.append(line)
    
    return lines


def create_histogram(
    values: List[float],
    bins: int = 10,
    width: int = 50,
    height: int = 10
) -> List[str]:
    """
    Create ASCII histogram.
    
    Args:
        values: List of values to plot
        bins: Number of bins
        width: Width of histogram
        height: Height of histogram
        
    Returns:
        List of histogram lines
    """
    if not values:
        return ["No data available"]
    
    # Calculate bins
    min_val = min(values)
    max_val = max(values)
    
    if min_val == max_val:
        return [f"All values are {min_val:.1f}"]
    
    bin_width = (max_val - min_val) / bins
    bin_counts = [0] * bins
    
    # Count values in each bin
    for value in values:
        bin_idx = min(int((value - min_val) / bin_width), bins - 1)
        bin_counts[bin_idx] += 1
    
    # Normalize to height
    max_count = max(bin_counts) if bin_counts else 1
    
    lines = []
    
    # Draw histogram from top to bottom
    for h in range(height, 0, -1):
        line = ""
        threshold = (h / height) * max_count
        
        for count in bin_counts:
            if count >= threshold:
                line += "█"
            else:
                line += " "
        
        lines.append(line)
    
    # Add x-axis labels
    x_axis = "─" * bins
    lines.append(x_axis)
    lines.append(f"{min_val:.0f}%" + " " * (bins - 6) + f"{max_val:.0f}%")
    
    return lines


def create_trend_line(
    data_points: List[Tuple[str, float]],
    width: int = 60,
    height: int = 10
) -> List[str]:
    """
    Create ASCII trend line chart.
    
    Args:
        data_points: List of (label, value) tuples
        width: Width of chart
        height: Height of chart
        
    Returns:
        List of chart lines
    """
    if not data_points or len(data_points) < 2:
        return ["Insufficient data for trend line"]
    
    values = [v for _, v in data_points]
    min_val = min(values)
    max_val = max(values)
    
    if min_val == max_val:
        return [f"Constant value: {min_val:.1f}"]
    
    # Normalize values to chart height
    def normalize(val):
        return int(((val - min_val) / (max_val - min_val)) * (height - 1))
    
    normalized = [normalize(v) for v in values]
    
    # Create chart grid
    lines = []
    for h in range(height - 1, -1, -1):
        line = ""
        for i, norm_val in enumerate(normalized):
            if norm_val == h:
                line += "●"
            elif norm_val > h and i > 0 and normalized[i-1] <= h:
                line += "│"
            elif norm_val < h and i > 0 and normalized[i-1] >= h:
                line += "│"
            else:
                line += " "
        
        # Add y-axis label
        y_val = min_val + (h / (height - 1)) * (max_val - min_val)
        lines.append(f"{y_val:5.1f} │ {line}")
    
    # Add x-axis
    x_axis = "─" * (width + 8)
    lines.append(x_axis)
    
    return lines


def create_sparkline(values: List[float], width: int = 50) -> str:
    """
    Create compact sparkline (single line chart).
    
    Args:
        values: List of values
        width: Width of sparkline
        
    Returns:
        Sparkline string
    """
    if not values:
        return "No data"
    
    if len(values) == 1:
        return "▄"
    
    min_val = min(values)
    max_val = max(values)
    
    if min_val == max_val:
        return "─" * min(len(values), width)
    
    # Sparkline characters from low to high
    chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    
    sparkline = ""
    for value in values[:width]:
        normalized = (value - min_val) / (max_val - min_val)
        char_idx = min(int(normalized * len(chars)), len(chars) - 1)
        sparkline += chars[char_idx]
    
    return sparkline


# ============================================================================
# DASHBOARD SECTIONS
# ============================================================================

def show_model_confidence_section() -> List[str]:
    """Generate model confidence visualization section."""
    lines = []
    lines.append("=" * 70)
    lines.append("📊 MODEL CONFIDENCE DISTRIBUTION")
    lines.append("=" * 70)
    
    model = learn.load_model()
    if not model or model.total_samples == 0:
        lines.append("⚠️  No trained model found. Run --learn first.")
        return lines
    
    # Calculate confidence for each pattern
    confidences = []
    confidence_buckets = defaultdict(int)
    
    for file_type, destinations in model.type_to_folder.items():
        total = sum(destinations.values())
        if total > 0:
            max_count = max(destinations.values())
            confidence = (max_count / total) * 100
            confidences.append(confidence)
            
            # Bucket for distribution
            bucket = int(confidence / 10) * 10
            confidence_buckets[f"{bucket}-{bucket+10}%"] += 1
    
    if not confidences:
        lines.append("No patterns available")
        return lines
    
    # Show statistics
    avg_conf = sum(confidences) / len(confidences)
    lines.append(f"\nAverage Confidence: {avg_conf:.1f}%")
    lines.append(f"Total Patterns: {len(confidences)}")
    lines.append(f"Min: {min(confidences):.1f}% | Max: {max(confidences):.1f}%")
    
    # Show histogram
    lines.append("\nConfidence Distribution:")
    histogram = create_histogram(confidences, bins=10, width=50, height=8)
    for line in histogram:
        lines.append("  " + line)
    
    # Show bucket counts
    lines.append("\nPattern Counts by Confidence Range:")
    bucket_chart = create_bar_chart(confidence_buckets, max_width=30)
    for line in bucket_chart:
        lines.append("  " + line)
    
    lines.append("")
    return lines


def show_feedback_accuracy_section() -> List[str]:
    """Generate feedback accuracy visualization section."""
    lines = []
    lines.append("=" * 70)
    lines.append("💬 FEEDBACK ACCURACY")
    lines.append("=" * 70)
    
    stats = feedback.get_feedback_stats()
    
    if stats['total_feedback'] == 0:
        lines.append("⚠️  No feedback data yet. Enable with --feedback on")
        return lines
    
    # Show overall stats
    accuracy = stats.get('overall_accuracy', 0)
    lines.append(f"\nOverall Accuracy: {accuracy:.1f}%")
    lines.append(f"Total Feedback Events: {stats['total_feedback']}")
    lines.append(f"  ✓ Correct: {stats['total_correct']}")
    lines.append(f"  ✗ Wrong: {stats['total_wrong']}")
    
    # Show pattern-level accuracy
    if stats.get('patterns'):
        lines.append("\nPattern-Level Accuracy:")
        pattern_acc = {}
        for p in stats['patterns']:
            total = p['correct'] + p['wrong']
            if total > 0:
                acc = (p['correct'] / total) * 100
                pattern_acc[p['pattern']] = acc
        
        if pattern_acc:
            chart = create_bar_chart(pattern_acc, max_width=40, bar_char='▓')
            for line in chart[:10]:  # Top 10
                lines.append("  " + line)
    
    lines.append("")
    return lines


def show_file_distribution_section(db_path: str = 'file_organizer.db') -> List[str]:
    """Generate file type distribution visualization."""
    lines = []
    lines.append("=" * 70)
    lines.append("📁 FILE TYPE DISTRIBUTION")
    lines.append("=" * 70)
    
    if not db.database_exists(db_path):
        lines.append("⚠️  No database found. Organize some files first.")
        return lines
    
    stats = db.get_database_stats(db_path)
    files_by_type = stats.get('files_by_type', {})
    
    if not files_by_type:
        lines.append("No files tracked yet")
        return lines
    
    total_files = sum(files_by_type.values())
    lines.append(f"\nTotal Files: {total_files}")
    
    # Show bar chart
    lines.append("\nFiles by Category:")
    chart = create_bar_chart(files_by_type, max_width=50)
    for line in chart:
        lines.append("  " + line)
    
    # Show percentages
    lines.append("\nPercentage Distribution:")
    percentages = {k: (v / total_files * 100) for k, v in files_by_type.items()}
    perc_chart = create_bar_chart(percentages, max_width=50, bar_char='░')
    for line in perc_chart:
        lines.append("  " + line)
    
    lines.append("")
    return lines


def show_maintenance_history_section() -> List[str]:
    """Generate maintenance history visualization."""
    lines = []
    lines.append("=" * 70)
    lines.append("🔧 MAINTENANCE HISTORY")
    lines.append("=" * 70)
    
    mlog = maintenance.MaintenanceLog()
    
    last_maint = mlog.get_last_maintenance()
    if not last_maint:
        lines.append("⚠️  No maintenance performed yet")
        return lines
    
    # Show summary stats
    stats = mlog.log['stats']
    lines.append(f"\nLast Maintenance: {last_maint[:19]}")
    lines.append(f"Total Retrains: {stats['total_retrains']}")
    lines.append(f"Total Optimizations: {stats['total_optimizations']}")
    lines.append(f"Patterns Pruned: {stats['patterns_pruned']}")
    
    # Show recent operations
    recent = mlog.get_operations_since(hours=168)  # Last week
    if recent:
        lines.append(f"\nOperations (Last 7 Days): {len(recent)}")
        
        # Count by type
        by_type = defaultdict(int)
        for op in recent:
            by_type[op['type']] += 1
        
        if by_type:
            lines.append("\nOperation Types:")
            chart = create_bar_chart(dict(by_type), max_width=30)
            for line in chart:
                lines.append("  " + line)
    
    lines.append("")
    return lines


def show_system_health_section(db_path: str = 'file_organizer.db') -> List[str]:
    """Generate system health visualization."""
    lines = []
    lines.append("=" * 70)
    lines.append("🏥 SYSTEM HEALTH STATUS")
    lines.append("=" * 70)
    
    # Run diagnostics
    model_diag = diagnostic.diagnose_model_confidence()
    feedback_diag = diagnostic.diagnose_feedback_accuracy()
    db_diag = diagnostic.diagnose_database(db_path)
    
    # Determine overall health
    health_scores = {
        'Model': model_diag['status'],
        'Feedback': feedback_diag['status'],
        'Database': db_diag['status']
    }
    
    # Map status to numeric score
    status_map = {
        'excellent': 100,
        'good': 80,
        'fair': 60,
        'poor': 40,
        'critical': 20,
        'no_data': 50,
        'no_model': 0,
        'healthy': 100,
        'corrupted': 0,
        'missing': 0,
        'unknown': 50
    }
    
    lines.append("\nComponent Health:")
    for component, status in health_scores.items():
        score = status_map.get(status, 50)
        bar_length = int(score / 2)  # Max 50 chars
        
        # Choose emoji based on score
        if score >= 90:
            emoji = "✅"
        elif score >= 70:
            emoji = "🟢"
        elif score >= 50:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        bar = "█" * bar_length + "░" * (50 - bar_length)
        lines.append(f"  {emoji} {component:12} │ {bar} {status}")
    
    lines.append("")
    return lines


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def display_dashboard(db_path: str = 'file_organizer.db'):
    """
    Display complete ASCII dashboard.
    
    Args:
        db_path: Path to database
    """
    logger = logging.getLogger('FileOrganizer')
    
    logger.info("\n" + "=" * 70)
    logger.info("🎨 FILEGENIUS INTELLIGENCE DASHBOARD")
    logger.info("=" * 70)
    logger.info(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    # Show each section
    sections = [
        show_system_health_section(db_path),
        show_model_confidence_section(),
        show_feedback_accuracy_section(),
        show_file_distribution_section(db_path),
        show_maintenance_history_section()
    ]
    
    for section in sections:
        for line in section:
            logger.info(line)
    
    logger.info("=" * 70)
    logger.info("Dashboard refresh: Use --dashboard to view again")
    logger.info("=" * 70)


def display_compact_dashboard(db_path: str = 'file_organizer.db'):
    """
    Display compact one-screen dashboard with sparklines.
    
    Args:
        db_path: Path to database
    """
    logger = logging.getLogger('FileOrganizer')
    
    logger.info("\n" + "┌" + "─" * 68 + "┐")
    logger.info("│" + " FileGenius Intelligence Dashboard ".center(68) + "│")
    logger.info("├" + "─" * 68 + "┤")
    
    # System Health
    model_diag = diagnostic.diagnose_model_confidence()
    db_diag = diagnostic.diagnose_database(db_path)
    
    model_conf = model_diag.get('avg_confidence', 0)
    health_emoji = "✅" if model_conf > 80 else "⚠️" if model_conf > 60 else "🔴"
    
    logger.info(f"│ {health_emoji} System Health: {model_diag['status']:12}  Model: {model_conf:5.1f}%          │")
    logger.info(f"│    Database: {db_diag['status']:12}  Size: {db_diag['size_mb']:5.2f} MB           │")
    
    # File Stats
    if db.database_exists(db_path):
        stats = db.get_database_stats(db_path)
        logger.info(f"│    Total Files: {stats['total_files']:6}      Operations: {stats['total_operations']:6}        │")
    
    # Feedback Stats
    fb_stats = feedback.get_feedback_stats()
    if fb_stats['total_feedback'] > 0:
        logger.info(f"│    Feedback Accuracy: {fb_stats['overall_accuracy']:5.1f}%  Events: {fb_stats['total_feedback']:6}         │")
    
    logger.info("├" + "─" * 68 + "┤")
    
    # Quick stats
    model = learn.load_model()
    if model and model.total_samples > 0:
        logger.info(f"│ 🧠 Learning: {model.total_samples} samples, {len(model.type_to_folder)} patterns              │")
    
    # Maintenance
    mlog = maintenance.MaintenanceLog()
    last_maint = mlog.get_last_maintenance()
    if last_maint:
        logger.info(f"│ 🔧 Last Maintenance: {last_maint[:19]}                         │")
    
    logger.info("└" + "─" * 68 + "┘")


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_dashboard_text(output_path: str, db_path: str = 'file_organizer.db') -> bool:
    """
    Export dashboard to text file.
    
    Args:
        output_path: Path for output file
        db_path: Database path
        
    Returns:
        True if successful
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("FILEGENIUS INTELLIGENCE DASHBOARD\n")
            f.write("=" * 70 + "\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 70 + "\n\n")
            
            sections = [
                show_system_health_section(db_path),
                show_model_confidence_section(),
                show_feedback_accuracy_section(),
                show_file_distribution_section(db_path),
                show_maintenance_history_section()
            ]
            
            for section in sections:
                for line in section:
                    f.write(line + "\n")
        
        return True
    
    except Exception as e:
        logger = logging.getLogger('FileOrganizer')
        logger.error(f"Failed to export dashboard: {e}")
        return False
