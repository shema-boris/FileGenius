# FileGenius - Local File Organizer

A privacy-first file organization tool that runs entirely on your local machine. Automatically organize files by type, creation date, and more — with no data ever sent to external servers.

## 🎯 Project Overview

**Current Status:** Phase 1 Complete

FileGenius is a personal AI assistant that helps organize files on your local machine automatically. Built with privacy as the top priority, all operations run locally.

### Core Principles

- **Privacy First:** All operations run locally — no data sent to external servers
- **File Organization:** Categorize files by type, extension, size, date, and metadata
- **Duplicate Detection:** (Coming in Phase 2) Efficient SHA-256 hashing
- **Undo Capability:** (Coming in Phase 2) Revert changes if needed
- **Automation & Intelligence:** (Future phases) AI-powered organization suggestions
- **Logging & Dry-Run:** Always preview changes before applying them

---

## 📦 Phase 1 Features

✅ **Implemented:**
- Organize files by type (images, documents, videos, audio, code, etc.)
- Organize by creation date (year/month subfolders)
- Dry-run mode to preview all changes
- Comprehensive logging to `file_organizer.log`
- Modular, extensible Python code
- Command-line interface
- Handles filename conflicts automatically
- Recursive directory scanning

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

**2. Actually organize files:**
```bash
python file_organizer.py /path/to/your/folder --no-dry-run
```

**3. Organize without date subfolders:**
```bash
python file_organizer.py /path/to/folder --no-dry-run --no-date
```

**4. Recursive scan (include subdirectories):**
```bash
python file_organizer.py /path/to/folder --recursive --dry-run
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
usage: file_organizer.py [-h] [-o OUTPUT] [--no-date] [-r] [--dry-run] [--no-dry-run] source

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
```

---

## 💻 Python API Usage

You can also use the organizer as a Python module:

```python
from file_organizer import organize_files

# Dry-run mode
stats = organize_files(
    source_directory='./my_messy_folder',
    output_directory='organized',
    organize_by_date=True,
    recursive=False,
    dry_run=True
)

print(f"Would move {stats['files_moved']} files")

# Live mode (actually move files)
stats = organize_files(
    source_directory='./my_messy_folder',
    output_directory='organized',
    organize_by_date=True,
    recursive=False,
    dry_run=False
)
```

See `example_usage.py` for more examples.

---

## 📝 Logging

All operations are logged to `file_organizer.log` in the current directory. The log includes:

- Timestamp of each operation
- Files being moved (or would be moved in dry-run)
- Errors and permission issues
- Summary statistics
- Whether dry-run or live mode was used

**Example log entry:**
```
2024-10-25 11:30:45 - FileOrganizer - INFO - WOULD MOVE: /path/photo.jpg -> organized/images/2024/10/photo.jpg
```

---

## 🧪 Testing

Create test files and run a dry-run:

```bash
# Run the example script to create test files
python example_usage.py

# Or create test files manually
mkdir test_folder
echo "test" > test_folder/document.pdf
echo "test" > test_folder/photo.jpg
echo "test" > test_folder/video.mp4

# Run dry-run
python file_organizer.py test_folder --dry-run

# Check the log
cat file_organizer.log
```

---

## 🗺️ Roadmap

### ✅ Phase 1 (Current - Complete)
- [x] Organize by file type and creation date
- [x] Dry-run mode
- [x] Comprehensive logging
- [x] Modular, extensible code
- [x] Command-line interface

### 🔄 Phase 2 (Coming Next)
- [ ] Duplicate file detection using SHA-256 hashing
- [ ] Undo/rollback functionality
- [ ] File size-based organization
- [ ] Configuration file support (YAML/JSON)
- [ ] Progress bar for large operations

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
3. **File conflicts:** If a file with the same name exists, it will be renamed with a suffix (`_1`, `_2`, etc.)
4. **Symbolic links:** Currently not handled (will be added in future phases)
5. **Large files:** No special handling yet (future optimization planned)

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

**Version:** 1.0.0 (Phase 1)  
**Last Updated:** October 2024
