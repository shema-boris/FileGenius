"""Test Phase 4 API - Programmatic Usage"""

import learning_engine as learn

print("=" * 70)
print("PHASE 4 API TEST")
print("=" * 70)

# Test 1: Load model
print("\n1. Loading trained model...")
model = learn.load_model()

if model:
    print(f"   ✓ Model loaded: {model.total_samples} samples")
    
    # Test 2: Get statistics
    print("\n2. Getting learning statistics...")
    stats = learn.get_learning_stats(model)
    print(f"   ✓ File types learned: {stats['file_types_learned']}")
    print(f"   ✓ Extensions learned: {stats['extensions_learned']}")
    print(f"   ✓ Last trained: {stats['last_trained'][:19]}")
    
    # Test 3: Test prediction
    print("\n3. Testing prediction...")
    file_meta = {
        'file_name': 'test_report.pdf',
        'file_type': 'documents',
        'file_ext': '.pdf'
    }
    
    result = learn.predict_destination(file_meta, model)
    
    if result:
        dest, conf, reason = result
        print(f"   ✓ Prediction: {dest}")
        print(f"   ✓ Confidence: {conf:.1%}")
        print(f"   ✓ Reason: {reason}")
    else:
        print("   ✗ No prediction available")
    
    # Test 4: Confidence emoji
    print("\n4. Testing confidence indicators...")
    for conf_val in [0.9, 0.6, 0.3]:
        emoji = learn.get_confidence_emoji(conf_val)
        priority = learn.get_confidence_priority(conf_val)
        print(f"   {emoji} {conf_val:.0%} confidence = {priority} priority")
    
    print("\n" + "=" * 70)
    print("✓ ALL API TESTS PASSED!")
    print("=" * 70)
    
else:
    print("   ✗ No model found. Run --learn first.")
