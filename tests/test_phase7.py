"""Test Phase 7 Features"""

print("=" * 70)
print("TESTING PHASE 7 FEATURES")
print("=" * 70)

# Test imports
print("\n1. Testing imports...")
try:
    import visual_dashboard as dashboard
    import insight_engine as insights
    print("   ✓ All Phase 7 modules imported successfully")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    exit(1)

# Test ASCII chart functions
print("\n2. Testing ASCII chart generation...")
try:
    # Test bar chart
    data = {'images': 10, 'documents': 25, 'videos': 5}
    chart = dashboard.create_bar_chart(data)
    print("   ✓ Bar chart created")
    print(f"   - Lines: {len(chart)}")
    
    # Test histogram
    values = [75.5, 80.2, 85.1, 90.5, 95.0, 78.3, 82.1]
    histogram = dashboard.create_histogram(values)
    print("   ✓ Histogram created")
    
    # Test sparkline
    sparkline = dashboard.create_sparkline([10, 20, 15, 30, 25, 35])
    print(f"   ✓ Sparkline created: {sparkline}")
    
except Exception as e:
    print(f"   ✗ Chart generation failed: {e}")

# Test insight generation
print("\n3. Testing insight generation...")
try:
    # Test weekly summary
    weekly = insights.generate_weekly_summary()
    print("   ✓ Weekly summary generated")
    print(f"   - Insights: {len(weekly['insights'])}")
    print(f"   - Recommendations: {len(weekly['recommendations'])}")
    
    # Test cumulative summary
    cumulative = insights.generate_cumulative_summary()
    print("   ✓ Cumulative summary generated")
    print(f"   - Milestones: {len(cumulative['milestones'])}")
    
    # Test trend detection
    trends = insights.detect_trends()
    print("   ✓ Trend detection complete")
    print(f"   - Confidence trend: {trends['confidence_trend']}")
    print(f"   - Accuracy trend: {trends['accuracy_trend']}")
    
except Exception as e:
    print(f"   ✗ Insight generation failed: {e}")

# Test dashboard sections
print("\n4. Testing dashboard sections...")
try:
    # Test model confidence section
    model_section = dashboard.show_model_confidence_section()
    print(f"   ✓ Model confidence section: {len(model_section)} lines")
    
    # Test file distribution section
    file_section = dashboard.show_file_distribution_section()
    print(f"   ✓ File distribution section: {len(file_section)} lines")
    
    # Test system health section
    health_section = dashboard.show_system_health_section()
    print(f"   ✓ System health section: {len(health_section)} lines")
    
except Exception as e:
    print(f"   ✗ Dashboard sections failed: {e}")

# Test predictive insights
print("\n5. Testing predictive insights...")
try:
    predictions = insights.generate_predictive_insights()
    print(f"   ✓ Predictive insights generated: {len(predictions)} predictions")
    for pred in predictions:
        print(f"      {pred}")
    
except Exception as e:
    print(f"   ✗ Predictive insights failed: {e}")

print("\n" + "=" * 70)
print("✓ PHASE 7 BASIC TESTS COMPLETE")
print("=" * 70)
print("\nNow test CLI commands:")
print("  python file_organizer.py --dashboard")
print("  python file_organizer.py --dashboard-compact")
print("  python file_organizer.py --insights")
print("  python file_organizer.py --insights-weekly")
print("  python file_organizer.py --export-dashboard dashboard.txt")
print("=" * 70)
