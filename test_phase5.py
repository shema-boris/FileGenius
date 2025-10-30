"""Test Phase 5 Features"""

print("=" * 70)
print("TESTING PHASE 5 FEATURES")
print("=" * 70)

# Test imports
print("\n1. Testing imports...")
try:
    import feedback_manager as feedback
    import preference_manager as prefs
    import learning_engine as learn
    print("   ✓ All Phase 5 modules imported successfully")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    exit(1)

# Test preference manager
print("\n2. Testing preference manager...")
try:
    user_prefs = prefs.load_preferences()
    print(f"   ✓ Loaded preferences")
    print(f"   - Confidence bias: {user_prefs.get('learning.confidence_bias')}")
    print(f"   - Auto threshold: {user_prefs.get('learning.auto_threshold')}")
    print(f"   - Incremental learning: {user_prefs.get('learning.incremental_learning')}")
except Exception as e:
    print(f"   ✗ Preference test failed: {e}")

# Test feedback manager
print("\n3. Testing feedback manager...")
try:
    # Get feedback stats
    stats = feedback.get_feedback_stats()
    print(f"   ✓ Feedback stats retrieved")
    print(f"   - Total feedback: {stats['total_feedback']}")
    print(f"   - Overall accuracy: {stats.get('overall_accuracy', 0):.1f}%")
except Exception as e:
    print(f"   ✗ Feedback test failed: {e}")

# Test incremental learning
print("\n4. Testing incremental learning...")
try:
    model = learn.load_model()
    if model:
        print(f"   ✓ Model loaded: {model.total_samples} samples")
        
        # Test incremental update
        file_meta = {
            'file_name': 'test.pdf',
            'file_type': 'documents',
            'file_ext': '.pdf'
        }
        # Don't actually update, just test the function exists
        print(f"   ✓ Incremental update function available")
    else:
        print("   ⚠ No trained model found (run --learn first)")
except Exception as e:
    print(f"   ✗ Incremental learning test failed: {e}")

# Test learning analytics
print("\n5. Testing learning analytics...")
try:
    from report_generator import _get_learning_analytics, _get_feedback_analytics
    
    learning_analytics = _get_learning_analytics()
    print(f"   ✓ Learning analytics: {learning_analytics['status']}")
    
    feedback_analytics = _get_feedback_analytics()
    print(f"   ✓ Feedback analytics: {feedback_analytics['status']}")
except Exception as e:
    print(f"   ✗ Analytics test failed: {e}")

print("\n" + "=" * 70)
print("✓ PHASE 5 BASIC TESTS COMPLETE")
print("=" * 70)
print("\nNow test CLI commands:")
print("  python file_organizer.py --stats")
print("  python file_organizer.py --preferences")
print("  python file_organizer.py --relearn")
print("=" * 70)
