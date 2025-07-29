# Quick integration test
import sys
from pathlib import Path

def test_integration():
    """Test that all components work together"""
    
    print("🧪 Testing LSDAI Enhancement Integration")
    print("=" * 45)
    
    tests = []
    
    # Test 1: Original LSDAI components
    try:
        import json_utils as js
        print("✅ json_utils import successful")
        tests.append(True)
    except ImportError as e:
        print(f"❌ json_utils import failed: {e}")
        tests.append(False)
        
    # Test 2: Enhanced modules
    try:
        from modules.EnhancedManager import get_enhanced_manager
        print("✅ Enhanced Manager import successful")
        tests.append(True)
    except ImportError as e:
        print(f"❌ Enhanced Manager import failed: {e}")
        tests.append(False)
        
    # Test 3: Widget integration
    try:
        from scripts.enhanced_widgets_integration import IntegratedWidgetSystem
        print("✅ Widget integration successful")
        tests.append(True)
    except ImportError as e:
        print(f"❌ Widget integration failed: {e}")
        tests.append(False)
        
    # Test 4: File structure
    required_dirs = ['modules', 'CSS', 'JS', 'data']
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ Directory {directory} exists")
            tests.append(True)
        else:
            print(f"❌ Directory {directory} missing")
            tests.append(False)
            
    # Results
    passed = sum(tests)
    total = len(tests)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 Integration test passed! You're ready to use enhanced LSDAI")
    else:
        print("⚠️  Some tests failed. Check the installation.")
        
    return passed == total

if __name__ == "__main__":
    test_integration()
