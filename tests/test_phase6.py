"""Test Phase 6 Features"""

print("=" * 70)
print("TESTING PHASE 6 FEATURES")
print("=" * 70)

# Test imports
print("\n1. Testing imports...")
try:
    import maintenance_engine as maintenance
    import diagnostic_engine as diagnostic
    print("   ✓ All Phase 6 modules imported successfully")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    exit(1)

# Test maintenance log
print("\n2. Testing maintenance log...")
try:
    from pathlib import Path
    log = maintenance.MaintenanceLog()
    print(f"   ✓ Maintenance log loaded")
    print(f"   - Last maintenance: {log.get_last_maintenance()}")
    print(f"   - Total retrains: {log.log['stats']['total_retrains']}")
except Exception as e:
    print(f"   ✗ Maintenance log test failed: {e}")

# Test model health check
print("\n3. Testing model health check...")
try:
    health = maintenance.check_model_health()
    print(f"   ✓ Health check complete")
    print(f"   - Overall status: {health['overall_status']}")
    print(f"   - Issues: {len(health['issues'])}")
    print(f"   - Recommendations: {len(health['recommendations'])}")
except Exception as e:
    print(f"   ✗ Health check failed: {e}")

# Test diagnostics
print("\n4. Testing diagnostic engine...")
try:
    model_diag = diagnostic.diagnose_model_confidence()
    print(f"   ✓ Model diagnostics complete")
    print(f"   - Status: {model_diag['status']}")
    print(f"   - Avg confidence: {model_diag['avg_confidence']:.1f}%")
    
    feedback_diag = diagnostic.diagnose_feedback_accuracy()
    print(f"   ✓ Feedback diagnostics complete")
    print(f"   - Status: {feedback_diag['status']}")
    
    db_diag = diagnostic.diagnose_database()
    print(f"   ✓ Database diagnostics complete")
    print(f"   - Status: {db_diag['status']}")
except Exception as e:
    print(f"   ✗ Diagnostics failed: {e}")

# Test pattern conflict detection
print("\n5. Testing pattern conflict detection...")
try:
    conflicts = diagnostic.detect_pattern_conflicts()
    print(f"   ✓ Conflict detection complete")
    print(f"   - Conflicts found: {len(conflicts)}")
except Exception as e:
    print(f"   ✗ Conflict detection failed: {e}")

print("\n" + "=" * 70)
print("✓ PHASE 6 BASIC TESTS COMPLETE")
print("=" * 70)
print("\nNow test CLI commands:")
print("  python file_organizer.py --diagnose")
print("  python file_organizer.py --optimize")
print("  python file_organizer.py /path/to/folder --auto-maintain --dry-run")
print("=" * 70)
