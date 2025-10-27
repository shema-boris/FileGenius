# FileGenius - Local File Organizer

A privacy-first file organization tool that runs entirely on your local machine. Automatically organize files by type, creation date, and more — with no data ever sent to external servers.

## 🎯 Project Overview

**Current Status:** Phase 3 Complete 🚀

FileGenius is a personal AI assistant that helps organize files on your local machine automatically. Built with privacy as the top priority, all operations run locally.

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

### ✅ Phase 3 (Complete) - **NEW!**
- **Smart Suggestions:** AI-driven analysis with intelligent organization recommendations
- **Batch Undo:** Undo specific operations by ID, not just the last one
- **Comprehensive Reporting:** Export detailed insights to CSV or JSON
- **Operations History:** List and manage all organization operations
- **Pattern Analysis:** Identify temporal patterns and file distribution
- **Actionable Insights:** Get specific CLI commands to optimize your file organization

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

**Version:** 3.0.0 (Phase 3)  
**Last Updated:** October 2025
