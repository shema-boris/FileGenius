# FileGenius - Local File Organizer

A privacy-first file organization tool that runs entirely on your local machine. Automatically organize files by type, creation date, and more — with no data ever sent to external servers.

## 🎯 Project Overview

**Current Status:** Phase 5 Complete 🧠🔄✨

FileGenius is a self-learning personal AI assistant that continuously improves from your file organization patterns. Built with privacy as the top priority, all operations run locally with zero external dependencies.

### Core Principles

- **Privacy First:** All operations run locally — no data sent to external servers
- **File Organization:** Categorize files by type, extension, size, date, and metadata
- **Duplicate Detection:** (Coming in Phase 2) Efficient SHA-256 hashing
- **Undo Capability:** (Coming in Phase 2) Revert changes if needed
- **Automation & Intelligence:** (Future phases) AI-powered organization suggestions
- **Logging & Dry-Run:** Always preview changes before applying them

---

## 📦 Features

### ✅ Phase 1 (Complete)
- Organize files by type (images, documents, videos, audio, code, etc.)
- Organize by creation date (year/month subfolders)
- Dry-run mode to preview all changes
- Comprehensive logging to `file_organizer.log`
- Modular, extensible Python code
- Command-line interface
- Handles filename conflicts automatically
- Recursive directory scanning

### ✅ Phase 2 (Complete)
- **SQLite Database Tracking:** Every file operation is recorded with full metadata
- **SHA-256 Hashing:** Compute and store file hashes for integrity verification
- **Duplicate Detection:** Identify duplicate files across your system
- **Duplicate Removal:** Optionally delete duplicate files (with confirmation)
- **Undo Capability:** Revert the last organization operation safely
- **Database Statistics:** View insights about your organized files
- **Backward Compatible:** Can disable database features for Phase 1 behavior

### ✅ Phase 3 (Complete)
- **Smart Suggestions:** AI-driven analysis with intelligent organization recommendations
- **Batch Undo:** Undo specific operations by ID, not just the last one
- **Comprehensive Reporting:** Export detailed insights to CSV or JSON
- **Operations History:** List and manage all organization operations
- **Pattern Analysis:** Identify temporal patterns and file distribution
- **Actionable Insights:** Get specific CLI commands to optimize your file organization

### ✅ Phase 4 (Complete) 🧠
- **Adaptive Learning:** System learns from your organization habits automatically
- **Confidence-Based Predictions:** Every suggestion includes confidence score (0-100%)
- **Auto-Organize Mode:** Automatically organize files using learned patterns
- **Pattern Recognition:** Learns file type, extension, and naming patterns
- **Explainable AI:** Every prediction includes the reason and data source
- **100% Offline Learning:** All ML happens locally, zero external dependencies
- **Model Persistence:** Save and reload learned preferences

### ✅ Phase 5 (Complete) 🧠🔄
- **Continuous Learning:** Model updates automatically after every file operation
- **Incremental Updates:** Learn from each action without full retraining
- **Exponential Decay:** Recent patterns weighted more heavily (95% decay factor)
- **Feedback Reinforcement:** System improves from user confirmations/undos
- **Positive Feedback:** Reinforces correct predictions (+2 weight)
- **Negative Feedback:** Penalizes wrong predictions (-1 weight, auto-records on undo)
- **User Preferences:** Customizable settings (confidence thresholds, ignored folders, etc.)
- **Interactive Preferences:** Manage settings with interactive CLI editor
- **Learning Analytics:** Detailed insights on model accuracy and pattern strength
- **Feedback Analytics:** Track correct/wrong predictions, identify weak patterns
- **Auto-Sync:** Model syncs to disk every 5 operations (configurable)
- **Privacy-Preserving:** All learning data stays local, fully transparent

### ✅ Phase 6 (Complete) - **NEW!** 🤖🔧
- **Autonomous Maintenance:** Self-monitors and auto-organizes files continuously
- **Predictive Maintenance:** Auto-retrains when confidence drops below thresholds
- **System Diagnostics:** Comprehensive health checks for model, database, and storage
- **Auto-Optimization:** Prunes weak patterns, optimizes database, manages storage
- **Pattern Pruning:** Removes unreliable patterns (< 5 samples) automatically
- **Database Optimization:** VACUUM, REINDEX, and ANALYZE for peak performance
- **Conflict Detection:** Identifies ambiguous patterns that confuse the model
- **Maintenance Logging:** Tracks all maintenance operations with full history
- **Scheduled Maintenance:** Run maintenance tasks at specified intervals
- **Autonomous Mode:** Monitor directories and organize new files automatically
- **Health Analytics:** Real-time system health metrics in reports
- **Actionable Recommendations:** AI suggests specific optimization steps

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Standard library only (no external dependencies)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd FileCleaner

# No installation needed - uses only standard Python libraries!
```

### Basic Usage

**1. Dry-run mode (recommended first step):**
```bash
python file_organizer.py /path/to/your/folder --dry-run
```

**2. Actually organize files (with database tracking):**
```bash
python file_organizer.py /path/to/your/folder --no-dry-run
```

**3. Check for duplicates (without removing):**
```bash
python file_organizer.py /path/to/folder --no-dry-run --check-duplicates
```

**4. Remove duplicate files:**
```bash
python file_organizer.py /path/to/folder --no-dry-run --remove-duplicates
```

**5. Undo the last organization:**
```bash
python file_organizer.py --undo-last --no-dry-run
```

**6. View database statistics:**
```bash
python file_organizer.py --show-stats
```

**7. Get smart suggestions (Phase 3):**
```bash
python file_organizer.py --suggest
```

**8. Generate comprehensive report (Phase 3):**
```bash
python file_organizer.py --report my_report.json
# or
python file_organizer.py --report my_report.csv
```

**9. List all operations (Phase 3):**
```bash
python file_organizer.py --list-operations
```

**10. Undo specific operation (Phase 3):**
```bash
python file_organizer.py --undo run_20241025_120000_a3b2c1d4 --no-dry-run
```

**11. Train learning system (Phase 4):**
```bash
python file_organizer.py --learn
```

**12. Auto-organize with learned patterns (Phase 4):**
```bash
python file_organizer.py /path/to/folder --auto --dry-run
# Use --no-dry-run to actually move files
```

**13. Reset learning data (Phase 4):**
```bash
python file_organizer.py --reset-learning
```

**14. Manage user preferences (Phase 5):**
```bash
python file_organizer.py --preferences
# Interactive menu to customize settings
```

**15. View learning & feedback statistics (Phase 5):**
```bash
python file_organizer.py --stats
# Shows learning accuracy, feedback data, and preferences
```

**16. Control feedback tracking (Phase 5):**
```bash
python file_organizer.py --feedback on   # Enable
python file_organizer.py --feedback off  # Disable
```

**17. Full retrain without decay (Phase 5):**
```bash
python file_organizer.py --relearn
# Retrain from scratch, useful after major habit changes
```

**18. Run system diagnostics (Phase 6):**
```bash
python file_organizer.py --diagnose
# Comprehensive health check with actionable recommendations
```

**19. Optimize system manually (Phase 6):**
```bash
python file_organizer.py --optimize
# Prune weak patterns and optimize database
```

**20. Autonomous monitoring mode (Phase 6):**
```bash
python file_organizer.py /path/to/monitor --auto-maintain
# Continuously monitor and organize new files
```

**21. Scheduled maintenance (Phase 6):**
```bash
python file_organizer.py --schedule 30
# Run full maintenance every 30 minutes
```

---

## 📂 Folder Structure

After organization, your files will be structured like this:

```
organized/
├── images/
│   ├── 2024/
│   │   ├── 01/  (January)
│   │   ├── 02/  (February)
│   │   └── ...
│   └── 2025/
│       └── 10/
├── documents/
│   └── 2024/
│       └── 10/
├── videos/
├── audio/
├── archives/
├── code/
├── executables/
└── others/
```

Without date organization (`--no-date`):
```
organized/
├── images/
├── documents/
├── videos/
├── audio/
└── others/
```

---

## 🎨 Supported File Types

### Images
`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`, `.ico`, `.tiff`, `.tif`, `.heic`, `.heif`, `.raw`

### Documents
`.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.csv`, `.md`, `.tex`

### Videos
`.mp4`, `.avi`, `.mkv`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.mpg`, `.mpeg`, `.3gp`

### Audio
`.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.wma`, `.m4a`, `.opus`, `.aiff`

### Archives
`.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`, `.xz`, `.tar.gz`, `.tgz`

### Code
`.py`, `.js`, `.java`, `.cpp`, `.c`, `.h`, `.cs`, `.php`, `.rb`, `.go`, `.rs`, `.swift`, `.kt`, `.ts`, `.html`, `.css`, `.scss`, `.json`, `.xml`, `.yaml`, `.yml`

### Executables
`.exe`, `.msi`, `.app`, `.dmg`, `.deb`, `.rpm`, `.apk`

**Others:** Any file type not listed above will go into the `others/` folder.

---

## 🔧 Command-Line Options

```
usage: file_organizer.py [-h] [-o OUTPUT] [--no-date] [-r] [--dry-run] [--no-dry-run]
                         [--no-database] [--check-duplicates] [--remove-duplicates]
                         [--db-path DB_PATH] [--undo-last] [--show-stats]
                         [source]

positional arguments:
  source                Source directory to organize

optional arguments:
  -h, --help            Show help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory for organized files (default: organized)
  --no-date             Do not organize files by date (only by category)
  -r, --recursive       Recursively scan subdirectories
  --dry-run             Preview changes without moving files (default: True)
  --no-dry-run          Actually move files (overrides --dry-run)

Phase 2 Options:
  --no-database         Disable database tracking (Phase 1 behavior)
  --check-duplicates    Check for duplicate files using SHA-256 hashing
  --remove-duplicates   Remove duplicate files (implies --check-duplicates)
  --db-path DB_PATH     Path to SQLite database file (default: file_organizer.db)
  --undo-last           Undo the last organization operation
  --show-stats          Show database statistics

Phase 3 Options:
  --suggest             Analyze database and show intelligent suggestions
  --undo OPERATION_ID   Undo a specific operation by its ID
  --list-operations     List all operations in the database
  --report OUTPUT_PATH  Generate comprehensive report (.json or .csv)

Phase 4 Options:
  --learn               Train learning system from past organization history
  --auto                Auto-organize files using learned patterns (high confidence only)
  --reset-learning      Clear all learned preferences and models
```

---

## 💻 Python API Usage

You can also use the organizer as a Python module:

```python
from file_organizer import organize_files

# Phase 1 style - no database
stats = organize_files(
    source_directory='./my_messy_folder',
    output_directory='organized',
    organize_by_date=True,
    recursive=False,
    dry_run=True,
    enable_database=False
)

# Phase 2 - with database and duplicate detection
stats = organize_files(
    source_directory='./my_messy_folder',
    output_directory='organized',
    organize_by_date=True,
    recursive=False,
    dry_run=False,
    enable_database=True,
    check_duplicates=True,
    remove_duplicates=False,
    db_path='file_organizer.db'
)

print(f"Moved: {stats['files_moved']}, Duplicates: {stats['duplicates_found']}")
```

### Database Module API

```python
import database_manager as db

# Initialize database
db.init_db('my_organizer.db')

# Check for duplicates
file_hash = db.compute_file_hash(Path('photo.jpg'))
duplicate = db.get_duplicate(file_hash)

# Undo last operation
stats = db.undo_last_operation(dry_run=True)

# Get statistics
stats = db.get_database_stats()
print(f"Total files: {stats['total_files']}")
```

### Phase 3 APIs

```python
import suggestion_engine as suggest
import report_generator as report

# Get smart suggestions
suggestions = suggest.generate_suggestions()
for s in suggestions:
    print(f"{s.priority}: {s.description}")

# Generate detailed analysis
analysis = suggest.get_detailed_analysis()
print(analysis['duplicates'])

# Generate and export report
report.generate_report('report.json', print_console=True)

# Quick console summary
report.quick_summary()
```

### Phase 4 APIs - Adaptive Learning

```python
import learning_engine as learn

# Train model from history
model = learn.learn_from_history('file_organizer.db')

# Save trained model
learn.save_model(model)

# Load existing model
model = learn.load_model()

# Predict destination for a file
file_meta = {
    'file_name': 'report_2024.pdf',
    'file_type': 'documents',
    'file_ext': '.pdf'
}
dest, confidence, reason = learn.predict_destination(file_meta, model)
print(f"Prediction: {dest} ({confidence:.0%})")
print(f"Reason: {reason}")

# Get learning statistics
stats = learn.get_learning_stats(model)
print(f"Trained on {stats['total_samples']} files")

# Clear all learning data
learn.clear_learning_data()
```

### Phase 5 APIs - Continuous Learning & Personalization

```python
import learning_engine as learn
import feedback_manager as feedback
import preference_manager as prefs

# ---- Incremental Learning ----
# Update model after single file operation
file_meta = {
    'file_name': 'invoice.pdf',
    'file_type': 'documents',
    'file_ext': '.pdf'
}
learn.update_model_incremental(file_meta, 'documents')

# Manual sync to disk
learn.sync_learning_data()

# ---- Feedback System ----
# Record positive feedback (correct prediction)
feedback.record_positive_feedback('type', 'documents', 'documents')

# Record negative feedback (wrong prediction)
feedback.record_negative_feedback('ext', '.zip', 'others')

# Auto-record feedback on undo
feedback.record_undo_operation('operation_id_123')

# Get feedback statistics
stats = feedback.get_feedback_stats()
print(f"Overall accuracy: {stats['overall_accuracy']:.1f}%")
print(f"Strongest pattern: {stats['strongest_pattern']['pattern']}")

# Enable/disable feedback
feedback.enable_feedback()
feedback.disable_feedback()

# ---- User Preferences ----
# Load preferences
user_prefs = prefs.load_preferences()

# Get specific setting
confidence_bias = user_prefs.get('learning.confidence_bias')
auto_threshold = user_prefs.get('learning.auto_threshold')

# Set preference
user_prefs.set('learning.confidence_bias', 1.2)
prefs.save_preferences(user_prefs)

# Interactive editor
prefs.edit_preferences_interactive()

# Check settings
if prefs.is_incremental_learning_enabled():
    print("Incremental learning is ON")

if prefs.should_ask_for_confirmation(confidence=0.65):
    print("Will ask user for confirmation")
```

### Phase 6 APIs - Autonomous Maintenance & Diagnostics

```python
import maintenance_engine as maintenance
import diagnostic_engine as diagnostic

# ---- System Diagnostics ----
# Run full system diagnosis
report = diagnostic.run_full_diagnosis('file_organizer.db')
print(f"Overall health: {report['overall_health']}")

# Model confidence diagnostics
model_diag = diagnostic.diagnose_model_confidence()
print(f"Avg confidence: {model_diag['avg_confidence']:.1f}%")

# Feedback accuracy diagnostics
feedback_diag = diagnostic.diagnose_feedback_accuracy()
print(f"Overall accuracy: {feedback_diag['overall_accuracy']:.1f}%")

# Database health check
db_diag = diagnostic.diagnose_database('file_organizer.db')
print(f"Database status: {db_diag['status']}")
print(f"Integrity: {db_diag['integrity_check']}")

# Detect pattern conflicts
conflicts = diagnostic.detect_pattern_conflicts()
for conflict in conflicts:
    print(f"Conflict: {conflict['pattern']} → {conflict['primary_dest']} vs {conflict['conflict_dest']}")

# ---- Predictive Maintenance ----
# Check model health
health = maintenance.check_model_health()
print(f"Status: {health['overall_status']}")
print(f"Issues: {len(health['issues'])}")

# Auto-retrain if needed
retrained = maintenance.auto_retrain_if_needed()
if retrained:
    print("Model was retrained")

# Prune weak patterns
pruned = maintenance.prune_weak_patterns(min_samples=5)
print(f"Pruned {pruned} weak patterns")

# Optimize database
optimized = maintenance.optimize_database('file_organizer.db')
print(f"Database optimized: {optimized}")

# Run full maintenance
results = maintenance.run_full_maintenance('file_organizer.db')
print(f"Maintenance complete: {len(results['operations'])} operations")

# ---- Maintenance Logging ----
# Access maintenance log
mlog = maintenance.MaintenanceLog()
last_maint = mlog.get_last_maintenance()
print(f"Last maintenance: {last_maint}")

# Get recent operations
recent_ops = mlog.get_operations_since(hours=24)
print(f"Operations in last 24h: {len(recent_ops)}")

# ---- Autonomous Mode ----
# Monitor directory and auto-organize (blocking)
from pathlib import Path
results = maintenance.run_autonomous_mode(
    source_dir=Path('/path/to/monitor'),
    output_dir=Path('organized'),
    dry_run=False,
    max_operations=100
)
print(f"Processed {results['files_processed']} files")
print(f"Moved: {results['files_moved']}, Skipped: {results['files_skipped']}")
```

---

## 📝 Logging & Database

### Logging

All operations are logged to `file_organizer.log` in the current directory. The log includes:

- Timestamp of each operation
- Files being moved (or would be moved in dry-run)
- Duplicate detections
- Database operations
- Errors and permission issues
- Summary statistics

**Example log entry:**
```
2024-10-25 11:30:45 - FileOrganizer - INFO - MOVING: /path/photo.jpg -> organized/images/2024/10/photo.jpg
2024-10-25 11:30:45 - FileOrganizer - WARNING - DUPLICATE: photo_copy.jpg matches photo.jpg
```

### Database Tracking

Phase 2 stores all file operations in a SQLite database (`file_organizer.db`):

**Database Schema:**
- `id` - Auto-increment primary key
- `original_path` - Where the file came from
- `new_path` - Where the file was moved to
- `file_name` - Name of the file
- `file_size` - Size in bytes
- `file_type` - Category (images, documents, etc.)
- `created_at` - File creation timestamp
- `modified_at` - File modification timestamp
- `sha256_hash` - Unique file hash
- `operation_date` - When the file was organized
- `operation_id` - Unique ID for each organization run

**Benefits:**
- Track every file operation
- Enable undo functionality
- Detect duplicates across multiple runs
- Generate statistics and insights

---

## 🧪 Testing

### Create Test Files

```bash
# Create test folder
mkdir test_folder

# Create some test files
echo "test content" > test_folder/document.pdf
echo "test content" > test_folder/photo.jpg
echo "test content" > test_folder/video.mp4
echo "test content" > test_folder/duplicate.jpg  # Same content as photo.jpg
```

### Test Phase 2 Features

```bash
# 1. Dry-run to preview
python file_organizer.py test_folder --dry-run

# 2. Organize with database tracking
python file_organizer.py test_folder --no-dry-run

# 3. Check database stats
python file_organizer.py --show-stats

# 4. Try to organize again (will detect duplicates)
python file_organizer.py test_folder --no-dry-run --check-duplicates

# 5. Undo the organization
python file_organizer.py --undo-last --no-dry-run

# 6. Check the logs
cat file_organizer.log
```

---

## 🗺️ Roadmap

### ✅ Phase 1 (Complete)
- [x] Organize by file type and creation date
- [x] Dry-run mode
- [x] Comprehensive logging
- [x] Modular, extensible code
- [x] Command-line interface

### ✅ Phase 2 (Complete)
- [x] Duplicate file detection using SHA-256 hashing
- [x] Undo/rollback functionality
- [x] SQLite database tracking
- [x] Database statistics and insights
- [x] Duplicate removal with confirmation

### ✅ Phase 3 (Complete)
- [x] Smart suggestions with AI-driven analysis
- [x] Batch undo (undo specific operations by ID)
- [x] Comprehensive reporting (CSV/JSON export)
- [x] Operations history management
- [x] Temporal and pattern analysis
- [x] Actionable insights and recommendations

### 🔄 Phase 4 (Future)
- [ ] File size-based organization
- [ ] Configuration file support (YAML/JSON)
- [ ] Progress bar for large operations
- [ ] Machine learning for organization patterns
- [ ] Advanced duplicate management (keep best quality)

### 🚀 Phase 3 (Future)
- [ ] AI-powered organization suggestions
- [ ] Pattern learning from user behavior
- [ ] Smart folder recommendations
- [ ] File content analysis (OCR, metadata extraction)
- [ ] Web-based UI (still privacy-first, local only)

---

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome! Key principles:

1. **Privacy First:** No external API calls or data transmission
2. **Local Only:** All operations must run on the user's machine
3. **Standard Library:** Minimize dependencies (Phase 1 uses only standard library)
4. **Modular Design:** Easy to extend and maintain
5. **Safe by Default:** Dry-run mode should always be the default

---

## ⚠️ Important Notes

1. **Always run dry-run first:** Preview changes before applying them
2. **Backup important files:** While the tool is designed to be safe, always backup critical data
3. **Database file:** `file_organizer.db` stores all operation history - keep it safe for undo capability
4. **File conflicts:** If a file with the same name exists, it will be renamed with a suffix (`_1`, `_2`, etc.)
5. **Duplicate detection:** Only works with database enabled (default in Phase 2)
6. **Undo limitations:** Can only restore files if they haven't been moved/deleted after organization
7. **SHA-256 hashing:** May be slow for very large files (>1GB)
8. **Symbolic links:** Currently not handled (will be added in future phases)

---

## 📄 License

This project is licensed under the MIT License.

---

## 🐛 Known Issues / Limitations

- Symbolic links are not currently handled
- Very large files (>1GB) may slow down operations
- File metadata on some systems may not include creation date (falls back to modification date)
- No GUI yet (CLI only)

---

## 📧 Support

For issues, questions, or suggestions:
1. Check the log file: `file_organizer.log`
2. Run in dry-run mode to diagnose issues
3. Create an issue in the repository (if applicable)

---

**Version:** 4.0.0 (Phase 4 - Adaptive Learning)  
**Last Updated:** October 2025
