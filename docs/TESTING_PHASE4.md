# Testing Phase 4: Adaptive Learning

## Quick Test Suite

### Test 1: Train Learning System

```bash
# Ensure you have organized files (training data)
python file_organizer.py --show-stats
# Should show: Total files tracked: 3 (or more)

# Train the model
python file_organizer.py --learn
```

**Expected Output:**
```
======================================================================
TRAINING LEARNING SYSTEM
======================================================================
Learning from organization history...
✓ Learned from 3 files
  • 2 file types
  • 3 extensions
  • 3 filename patterns

======================================================================
LEARNING SUMMARY
======================================================================
Training samples: 3
Last trained: 2025-10-27T...

📁 File Type Patterns:
  • documents       → documents            (2/3 = 67%)
  • images          → images               (1/3 = 33%)

✓ Learning complete! Model saved.
  Use --suggest to see adaptive recommendations
  Use --auto to auto-organize with learned patterns
======================================================================
```

**Verify:**
```bash
# Check model files created
dir learning_data
# Should see: model.pkl, preferences.json

# View preferences
type learning_data\preferences.json
```

---

### Test 2: Adaptive Suggestions

```bash
python file_organizer.py --suggest
```

**Expected Output:**
```
======================================================================
SMART SUGGESTIONS - AI-DRIVEN FILE ORGANIZATION INSIGHTS
======================================================================
Analyzing 3 files across 1 operations...

Found 2 suggestions:

Suggestion 1:
🟢 [LOW] Adaptive Learning System Active
  🟢 Confidence: 100.0%
  📊 Reason: Model trained on 3 historical file operations
  • Training samples: 3
  • File types learned: 2
  • Last trained: 2025-10-27 ...
  💡 Suggested action: python file_organizer.py --auto  # Auto-organize with learned patterns

Suggestion 2:
🟡 [MEDIUM] Found 1 duplicate files
  ...
```

**Key Points:**
- ✅ Shows learning system is active
- ✅ Displays confidence score (100%)
- ✅ Shows training statistics
- ✅ Provides actionable command

---

### Test 3: View Learning Data (Human-Readable)

```bash
type learning_data\preferences.json
```

**Expected JSON Structure:**
```json
{
  "metadata": {
    "version": "4.0",
    "total_samples": 3,
    "last_trained": "2025-10-27T..."
  },
  "type_patterns": {
    "documents": {
      "documents": 2
    },
    "images": {
      "images": 1
    }
  },
  "extension_patterns": {
    ".pdf": {
      "documents": 2
    },
    ".jpg": {
      "images": 1
    }
  },
  "name_patterns": {
    "doc": {
      "documents": 2
    },
    "photo": {
      "images": 1
    }
  }
}
```

**Insights:**
- Shows what patterns were learned
- Frequency counts for each destination
- Human-readable format

---

### Test 4: Auto-Organize Mode (Dry-Run)

```bash
# Create new test files
mkdir test_auto
echo "test content" > test_auto/report.pdf
echo "test content" > test_auto/image.jpg

# Try auto-organize in dry-run
python file_organizer.py test_auto --auto --dry-run
```

**Expected Output:**
```
======================================================================
AUTO-ORGANIZE MODE (Adaptive Learning)
======================================================================
✓ Model loaded (3 samples)
Auto-organizing with high-confidence predictions (>80%)

⚠ Auto-organize will apply learned patterns automatically
  Only files with >80% confidence will be moved

DRY-RUN MODE: Use --no-dry-run to actually move files
======================================================================
```

**Note:** With only 3 training samples, confidence may be low. Need more training data for high-confidence predictions.

---

### Test 5: Reset Learning Data

```bash
python file_organizer.py --reset-learning
```

**Prompt:**
```
Are you sure you want to clear all learned data? (yes/no):
```

**Type:** `yes`

**Expected Output:**
```
======================================================================
RESET LEARNING DATA
======================================================================
✓ Deleted: learning_data\model.pkl
✓ Deleted: learning_data\preferences.json
✓ Removed directory: learning_data
✓ Learning data cleared
======================================================================
```

**Verify:**
```bash
dir learning_data
# Should show: "File Not Found" or directory doesn't exist
```

---

### Test 6: Retrain After Reset

```bash
# Train again
python file_organizer.py --learn

# Check suggestions
python file_organizer.py --suggest
```

**Should work exactly as before** - model is retrained from database.

---

## Advanced Testing

### Test 7: Build Larger Training Set

```bash
# Create diverse test files
mkdir test_large
echo "content" > test_large/report_2024.pdf
echo "content" > test_large/invoice_jan.pdf
echo "content" > test_large/photo_001.jpg
echo "content" > test_large/photo_002.jpg
echo "content" > test_large/video.mp4
echo "content" > test_large/presentation.pptx
echo "content" > test_large/spreadsheet.xlsx
echo "content" > test_large/code.py
echo "content" > test_large/data.csv
echo "content" > test_large/archive.zip

# Organize them
python file_organizer.py test_large --no-dry-run

# Now you have 13 total files (3 original + 10 new)
python file_organizer.py --show-stats
# Should show: Total files tracked: 13

# Retrain with more data
python file_organizer.py --learn
```

**Expected:**
- More patterns learned
- Higher confidence scores
- Better predictions

---

### Test 8: Check Confidence Scores

```bash
# After training with more data
python file_organizer.py --suggest
```

**Look for:**
- Confidence percentages in suggestions
- 🟢 for high confidence (>80%)
- 🟡 for medium (50-80%)
- 🔴 for low (<50%)

---

### Test 9: Prediction API (Python)

Create file `test_learning.py`:

```python
import learning_engine as learn
from pathlib import Path

# Load trained model
model = learn.load_model()

if model:
    # Test prediction
    file_meta = {
        'file_name': 'new_report.pdf',
        'file_type': 'documents',
        'file_ext': '.pdf'
    }
    
    result = learn.predict_destination(file_meta, model)
    
    if result:
        dest, conf, reason = result
        print(f"Prediction: {dest}")
        print(f"Confidence: {conf:.1%}")
        print(f"Reason: {reason}")
    else:
        print("No prediction available")
    
    # Get stats
    stats = learn.get_learning_stats(model)
    print(f"\nModel Stats:")
    print(f"  Training samples: {stats['total_samples']}")
    print(f"  File types: {stats['file_types_learned']}")
else:
    print("No model found. Run --learn first.")
```

Run:
```bash
python test_learning.py
```

**Expected Output:**
```
Prediction: documents
Confidence: 66.7%
Reason: Based on 2/3 prior documents files moved to 'documents'; ...

Model Stats:
  Training samples: 3
  File types: 2
```

---

## Troubleshooting

### Issue 1: "No trained model found"

**Cause:** Haven't run `--learn` yet

**Solution:**
```bash
python file_organizer.py --learn
```

---

### Issue 2: "Insufficient training data"

**Cause:** Need at least 3 files organized

**Solution:**
```bash
# Check current count
python file_organizer.py --show-stats

# Organize more files if needed
python file_organizer.py test_files --no-dry-run
```

---

### Issue 3: Low confidence scores

**Cause:** Not enough training data or inconsistent patterns

**Solution:**
- Organize more files (aim for 20+ files)
- Ensure consistent organization (same file types to same folders)
- Retrain: `python file_organizer.py --learn`

---

### Issue 4: Model file corrupted

**Symptoms:** Error loading model

**Solution:**
```bash
# Reset and retrain
python file_organizer.py --reset-learning
# Type: yes

python file_organizer.py --learn
```

---

## Success Checklist

After Phase 4 implementation, you should be able to:

- [ ] Run `--learn` and see training statistics
- [ ] View `learning_data/preferences.json`
- [ ] See adaptive suggestions with confidence scores
- [ ] Run `--auto` mode (even if dry-run)
- [ ] Reset learning data with `--reset-learning`
- [ ] Retrain model after reset
- [ ] All Phase 1-3 features still work

---

## Performance Benchmarks

**Expected Performance:**

| Files | Training Time | Prediction Time | Model Size |
|-------|---------------|-----------------|------------|
| 10    | <0.1s         | <0.001s         | ~10 KB     |
| 100   | <0.5s         | <0.001s         | ~50 KB     |
| 1,000 | <3s           | <0.001s         | ~500 KB    |

---

## Next Steps

1. **Organize more files** to build training data
2. **Run --learn** to train the model
3. **Check --suggest** to see adaptive recommendations
4. **Try --auto** when confidence is high
5. **Iterate:** Organize → Learn → Improve

---

**Happy Testing!** 🧠✨
