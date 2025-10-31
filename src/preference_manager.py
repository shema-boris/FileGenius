#!/usr/bin/env python3
"""
Preference Manager for Local File Organizer
Manages user personalization settings and preferences.

This module provides:
- User preference storage
- Interactive preference editing
- Preference-based behavior customization
- Preference validation
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_LEARNING_DIR = Path('learning_data')
PREFERENCES_FILE = 'user_preferences.json'

# Default preferences
DEFAULT_PREFERENCES = {
    'version': '5.0',
    'organization': {
        'preferred_structure': 'year/month',  # 'year/month', 'year', 'flat'
        'naming_style': 'original',           # 'original', 'lowercase', 'uppercase', 'lowercase_underscore'
        'date_format': '%Y/%m'                # Strftime format
    },
    'filtering': {
        'ignored_folders': ['temp', 'cache', '.git', '__pycache__'],
        'ignored_extensions': ['.tmp', '.cache', '.lock'],
        'min_file_size_bytes': 0,             # Ignore files smaller than this
        'max_file_size_bytes': None           # No limit by default
    },
    'learning': {
        'confidence_bias': 1.0,               # Multiplier for all confidence scores
        'auto_threshold': 0.8,                # Threshold for auto-organize
        'enable_decay': True,                 # Enable exponential decay
        'decay_factor': 0.95,                 # Weight decay factor
        'incremental_learning': True,         # Learn after every operation
        'sync_frequency': 5                   # Sync to disk every N operations
    },
    'feedback': {
        'enable_interactive': True,           # Ask user for medium-confidence files
        'medium_confidence_min': 0.5,
        'medium_confidence_max': 0.8,
        'auto_record_undo': True              # Auto-record negative feedback on undo
    },
    'ui': {
        'use_emojis': True,
        'verbose_logging': False,
        'show_confidence_in_suggestions': True,
        'color_output': True
    },
    'metadata': {
        'created_at': None,
        'last_modified': None,
        'modification_count': 0
    }
}


# ============================================================================
# PREFERENCE DATA
# ============================================================================

class UserPreferences:
    """User preference data structure."""
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize preferences with data or defaults."""
        if data:
            self.data = data
        else:
            self.data = self._deep_copy(DEFAULT_PREFERENCES)
    
    def _deep_copy(self, obj):
        """Deep copy dictionary."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get preference value using dot notation.
        
        Args:
            key_path: Path like 'learning.confidence_bias'
            default: Default value if not found
            
        Returns:
            Preference value or default
            
        Example:
            >>> prefs.get('learning.confidence_bias')
            1.0
        """
        keys = key_path.split('.')
        value = self.data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        Set preference value using dot notation.
        
        Args:
            key_path: Path like 'learning.confidence_bias'
            value: New value
            
        Returns:
            True if successful
        """
        keys = key_path.split('.')
        data = self.data
        
        # Navigate to parent
        for key in keys[:-1]:
            if key not in data:
                data[key] = {}
            data = data[key]
        
        # Set value
        data[keys[-1]] = value
        
        # Update metadata
        from datetime import datetime
        self.data['metadata']['last_modified'] = datetime.now().isoformat()
        self.data['metadata']['modification_count'] += 1
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.data
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UserPreferences':
        """Create from dictionary."""
        return UserPreferences(data)


# ============================================================================
# PERSISTENCE
# ============================================================================

def save_preferences(
    preferences: UserPreferences,
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> bool:
    """Save preferences to disk."""
    logger = logging.getLogger('FileOrganizer')
    
    try:
        learning_dir.mkdir(parents=True, exist_ok=True)
        prefs_path = learning_dir / PREFERENCES_FILE
        
        with open(prefs_path, 'w', encoding='utf-8') as f:
            json.dump(preferences.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Preferences saved: {prefs_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to save preferences: {e}")
        return False


def load_preferences(
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> UserPreferences:
    """Load preferences from disk."""
    prefs_path = learning_dir / PREFERENCES_FILE
    
    if not prefs_path.exists():
        # Create default preferences
        from datetime import datetime
        prefs = UserPreferences()
        prefs.data['metadata']['created_at'] = datetime.now().isoformat()
        save_preferences(prefs, learning_dir)
        return prefs
    
    try:
        with open(prefs_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return UserPreferences.from_dict(data)
    
    except Exception as e:
        logger = logging.getLogger('FileOrganizer')
        logger.warning(f"Failed to load preferences, using defaults: {e}")
        return UserPreferences()


def reset_preferences(
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> bool:
    """Reset preferences to defaults."""
    logger = logging.getLogger('FileOrganizer')
    
    try:
        from datetime import datetime
        prefs = UserPreferences()
        prefs.data['metadata']['created_at'] = datetime.now().isoformat()
        
        save_preferences(prefs, learning_dir)
        logger.info("✓ Preferences reset to defaults")
        return True
    
    except Exception as e:
        logger.error(f"Failed to reset preferences: {e}")
        return False


# ============================================================================
# INTERACTIVE EDITING
# ============================================================================

def edit_preferences_interactive(
    learning_dir: Path = DEFAULT_LEARNING_DIR
) -> bool:
    """
    Interactive preference editor.
    
    Returns:
        True if preferences were modified
    """
    logger = logging.getLogger('FileOrganizer')
    
    logger.info("=" * 70)
    logger.info("PREFERENCE EDITOR")
    logger.info("=" * 70)
    logger.info("")
    
    prefs = load_preferences(learning_dir)
    modified = False
    
    # Menu options
    menu = """
Select preference to edit:
  1. Organization structure (current: {})
  2. Confidence bias (current: {})
  3. Auto-organize threshold (current: {})
  4. Enable interactive feedback (current: {})
  5. Enable incremental learning (current: {})
  6. Ignored folders (current: {})
  7. Reset to defaults
  8. View all preferences
  9. Exit

Choice: """
    
    while True:
        org_structure = prefs.get('organization.preferred_structure')
        conf_bias = prefs.get('learning.confidence_bias')
        auto_thresh = prefs.get('learning.auto_threshold')
        interactive = prefs.get('feedback.enable_interactive')
        incremental = prefs.get('learning.incremental_learning')
        ignored = ', '.join(prefs.get('filtering.ignored_folders', [])[:3])
        
        choice = input(menu.format(
            org_structure, conf_bias, auto_thresh, 
            interactive, incremental, ignored
        )).strip()
        
        if choice == '1':
            print("\nOrganization structures:")
            print("  a. year/month (e.g., 2025/10)")
            print("  b. year (e.g., 2025)")
            print("  c. flat (no date folders)")
            structure_choice = input("Choice [a/b/c]: ").strip().lower()
            
            structure_map = {
                'a': 'year/month',
                'b': 'year',
                'c': 'flat'
            }
            
            if structure_choice in structure_map:
                prefs.set('organization.preferred_structure', structure_map[structure_choice])
                logger.info(f"✓ Organization structure set to: {structure_map[structure_choice]}")
                modified = True
        
        elif choice == '2':
            try:
                new_bias = float(input("\nConfidence bias (0.5 - 1.5): ").strip())
                if 0.5 <= new_bias <= 1.5:
                    prefs.set('learning.confidence_bias', new_bias)
                    logger.info(f"✓ Confidence bias set to: {new_bias}")
                    modified = True
                else:
                    logger.warning("Value must be between 0.5 and 1.5")
            except ValueError:
                logger.warning("Invalid number")
        
        elif choice == '3':
            try:
                new_thresh = float(input("\nAuto-organize threshold (0.0 - 1.0): ").strip())
                if 0.0 <= new_thresh <= 1.0:
                    prefs.set('learning.auto_threshold', new_thresh)
                    logger.info(f"✓ Auto-organize threshold set to: {new_thresh}")
                    modified = True
                else:
                    logger.warning("Value must be between 0.0 and 1.0")
            except ValueError:
                logger.warning("Invalid number")
        
        elif choice == '4':
            toggle = input("\nEnable interactive feedback? [y/n]: ").strip().lower()
            if toggle in ['y', 'n']:
                prefs.set('feedback.enable_interactive', toggle == 'y')
                logger.info(f"✓ Interactive feedback: {'enabled' if toggle == 'y' else 'disabled'}")
                modified = True
        
        elif choice == '5':
            toggle = input("\nEnable incremental learning? [y/n]: ").strip().lower()
            if toggle in ['y', 'n']:
                prefs.set('learning.incremental_learning', toggle == 'y')
                logger.info(f"✓ Incremental learning: {'enabled' if toggle == 'y' else 'disabled'}")
                modified = True
        
        elif choice == '6':
            print("\nCurrent ignored folders:", prefs.get('filtering.ignored_folders'))
            action = input("Add or remove? [a/r]: ").strip().lower()
            
            if action == 'a':
                folder = input("Folder name to ignore: ").strip()
                if folder:
                    current = prefs.get('filtering.ignored_folders', [])
                    if folder not in current:
                        current.append(folder)
                        prefs.set('filtering.ignored_folders', current)
                        logger.info(f"✓ Added '{folder}' to ignored folders")
                        modified = True
            
            elif action == 'r':
                folder = input("Folder name to remove: ").strip()
                current = prefs.get('filtering.ignored_folders', [])
                if folder in current:
                    current.remove(folder)
                    prefs.set('filtering.ignored_folders', current)
                    logger.info(f"✓ Removed '{folder}' from ignored folders")
                    modified = True
        
        elif choice == '7':
            confirm = input("\nReset all preferences to defaults? [yes/no]: ").strip().lower()
            if confirm == 'yes':
                reset_preferences(learning_dir)
                logger.info("✓ All preferences reset")
                modified = True
                break
        
        elif choice == '8':
            print("\n" + "=" * 70)
            print("ALL PREFERENCES:")
            print("=" * 70)
            print(json.dumps(prefs.to_dict(), indent=2))
            print("=" * 70)
            input("\nPress Enter to continue...")
        
        elif choice == '9':
            break
        
        else:
            logger.warning("Invalid choice")
    
    if modified:
        save_preferences(prefs, learning_dir)
        logger.info("")
        logger.info("✓ Preferences saved")
    
    logger.info("=" * 70)
    
    return modified


# ============================================================================
# PREFERENCE QUERIES
# ============================================================================

def get_confidence_bias(learning_dir: Path = DEFAULT_LEARNING_DIR) -> float:
    """Get confidence bias multiplier."""
    prefs = load_preferences(learning_dir)
    return prefs.get('learning.confidence_bias', 1.0)


def get_auto_threshold(learning_dir: Path = DEFAULT_LEARNING_DIR) -> float:
    """Get auto-organize confidence threshold."""
    prefs = load_preferences(learning_dir)
    return prefs.get('learning.auto_threshold', 0.8)


def is_incremental_learning_enabled(learning_dir: Path = DEFAULT_LEARNING_DIR) -> bool:
    """Check if incremental learning is enabled."""
    prefs = load_preferences(learning_dir)
    return prefs.get('learning.incremental_learning', True)


def is_interactive_feedback_enabled(learning_dir: Path = DEFAULT_LEARNING_DIR) -> bool:
    """Check if interactive feedback is enabled."""
    prefs = load_preferences(learning_dir)
    return prefs.get('feedback.enable_interactive', True)


def get_ignored_folders(learning_dir: Path = DEFAULT_LEARNING_DIR) -> List[str]:
    """Get list of ignored folders."""
    prefs = load_preferences(learning_dir)
    return prefs.get('filtering.ignored_folders', [])


def should_ask_for_confirmation(confidence: float, learning_dir: Path = DEFAULT_LEARNING_DIR) -> bool:
    """
    Determine if user should be asked for confirmation.
    
    Args:
        confidence: Prediction confidence (0-1)
        learning_dir: Directory for learning data
        
    Returns:
        True if should ask for confirmation
    """
    prefs = load_preferences(learning_dir)
    
    if not prefs.get('feedback.enable_interactive', True):
        return False
    
    min_conf = prefs.get('feedback.medium_confidence_min', 0.5)
    max_conf = prefs.get('feedback.medium_confidence_max', 0.8)
    
    return min_conf <= confidence < max_conf


# ============================================================================
# DISPLAY
# ============================================================================

def print_preferences_summary(learning_dir: Path = DEFAULT_LEARNING_DIR):
    """Print summary of current preferences."""
    logger = logging.getLogger('FileOrganizer')
    
    prefs = load_preferences(learning_dir)
    
    logger.info("=" * 70)
    logger.info("USER PREFERENCES")
    logger.info("=" * 70)
    
    logger.info("\n📂 Organization:")
    logger.info(f"  Structure: {prefs.get('organization.preferred_structure')}")
    logger.info(f"  Naming style: {prefs.get('organization.naming_style')}")
    
    logger.info("\n🧠 Learning:")
    logger.info(f"  Confidence bias: {prefs.get('learning.confidence_bias')}")
    logger.info(f"  Auto threshold: {prefs.get('learning.auto_threshold')}")
    logger.info(f"  Incremental learning: {prefs.get('learning.incremental_learning')}")
    logger.info(f"  Decay enabled: {prefs.get('learning.enable_decay')}")
    
    logger.info("\n💬 Feedback:")
    logger.info(f"  Interactive: {prefs.get('feedback.enable_interactive')}")
    logger.info(f"  Auto-record undo: {prefs.get('feedback.auto_record_undo')}")
    
    logger.info("\n🚫 Filtering:")
    ignored = prefs.get('filtering.ignored_folders', [])
    logger.info(f"  Ignored folders: {', '.join(ignored[:5])}")
    if len(ignored) > 5:
        logger.info(f"    ...and {len(ignored) - 5} more")
    
    logger.info("\n📊 Metadata:")
    created = prefs.get('metadata.created_at', 'N/A')
    logger.info(f"  Created: {created[:19] if created != 'N/A' else 'N/A'}")
    modified = prefs.get('metadata.last_modified', 'N/A')
    logger.info(f"  Modified: {modified[:19] if modified and modified != 'N/A' else 'Never'}")
    logger.info(f"  Modifications: {prefs.get('metadata.modification_count', 0)}")
    
    logger.info("=" * 70)
