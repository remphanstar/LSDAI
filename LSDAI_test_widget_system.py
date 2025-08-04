#!/usr/bin/env python3
"""
LSDAI Widget System Test Script
Tests the enhanced widget system and identifies any remaining issues
"""

import sys
import os
from pathlib import Path

# Add LSDAI modules to path
LSDAI_PATH = Path('/home/z/my-project/LSDAI')
if str(LSDAI_PATH) not in sys.path:
    sys.path.insert(0, str(LSDAI_PATH))
    sys.path.insert(0, str(LSDAI_PATH / 'modules'))

def test_imports():
    """Test basic imports"""
    print("🧪 Testing Basic Imports...")
    
    try:
        from modules.widget_factory import WidgetFactory
        print("✅ WidgetFactory imported successfully")
    except Exception as e:
        print(f"❌ WidgetFactory import failed: {e}")
        return False
    
    try:
        from modules.verbose_output_manager import get_verbose_manager, VerbosityLevel
        print("✅ VerboseOutputManager imported successfully")
    except Exception as e:
        print(f"❌ VerboseOutputManager import failed: {e}")
        return False
    
    try:
        from modules import json_utils as js
        print("✅ json_utils imported successfully")
    except Exception as e:
        print(f"❌ json_utils import failed: {e}")
        return False
    
    try:
        from modules.webui_utils import update_current_webui
        print("✅ webui_utils imported successfully")
    except Exception as e:
        print(f"❌ webui_utils import failed: {e}")
        return False
    
    return True

def test_widget_factory():
    """Test WidgetFactory functionality"""
    print("\\n🧪 Testing WidgetFactory...")
    
    try:
        from modules.widget_factory import WidgetFactory
        factory = WidgetFactory()
        print("✅ WidgetFactory created successfully")
        
        # Test basic widget creation
        text_widget = factory.create_text("test", "Test Text:")
        print("✅ Text widget created successfully")
        
        dropdown_widget = factory.create_dropdown(['A', 'B', 'C'], 'A', 'Test Dropdown:')
        print("✅ Dropdown widget created successfully")
        
        # Test missing methods
        header_widget = factory.create_header("Test Header")
        print("✅ Header widget created successfully")
        
        multi_dropdown = factory.create_dropdown_multiple(['A', 'B', 'C'], ['A'], 'Test Multi:')
        print("✅ Multiple dropdown widget created successfully")
        
        # Test layout widgets
        hbox = factory.create_hbox([text_widget, dropdown_widget])
        print("✅ HBox layout created successfully")
        
        vbox = factory.create_vbox([header_widget, hbox])
        print("✅ VBox layout created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ WidgetFactory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_verbose_manager():
    """Test VerboseOutputManager functionality"""
    print("\\n🧪 Testing VerboseOutputManager...")
    
    try:
        from modules.verbose_output_manager import get_verbose_manager, VerbosityLevel
        
        vm = get_verbose_manager()
        print("✅ VerboseOutputManager created successfully")
        
        # Test verbosity levels
        print(f"✅ Current verbosity level: {vm.get_current_level_name()}")
        
        # Test verbosity setting
        vm.set_verbosity(VerbosityLevel.DETAILED)
        print(f"✅ Set verbosity to DETAILED: {vm.get_current_level_name()}")
        
        # Test verbosity checking
        should_show = vm.should_show(VerbosityLevel.NORMAL)
        print(f"✅ Should show NORMAL level: {should_show}")
        
        # Test print_if_verbose
        vm.print_if_verbose("This is a test message", VerbosityLevel.NORMAL)
        print("✅ print_if_verbose test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ VerboseOutputManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_utils():
    """Test json_utils functionality"""
    print("\\n🧪 Testing json_utils...")
    
    try:
        from modules import json_utils as js
        
        # Test settings path
        settings_path = js.get_settings_path()
        print(f"✅ Settings path: {settings_path}")
        
        # Test settings structure
        success = js.ensure_settings_structure()
        print(f"✅ Settings structure ensured: {success}")
        
        # Test read/write operations
        test_data = {"test_key": "test_value", "test_number": 42}
        success = js.save_settings(test_data, "TEST_SECTION")
        print(f"✅ Settings saved: {success}")
        
        loaded_data = js.load_settings("TEST_SECTION")
        print(f"✅ Settings loaded: {loaded_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ json_utils test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_webui_utils():
    """Test webui_utils functionality"""
    print("\\n🧪 Testing webui_utils...")
    
    try:
        from modules.webui_utils import get_available_webuis, get_webui_names, get_current_webui
        
        # Test WebUI configurations
        available_webuis = get_available_webuis()
        print(f"✅ Available WebUIs: {available_webuis}")
        
        webui_names = get_webui_names()
        print(f"✅ WebUI names: {webui_names}")
        
        current_webui = get_current_webui()
        print(f"✅ Current WebUI: {current_webui}")
        
        return True
        
    except Exception as e:
        print(f"❌ webui_utils test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_widget_manager():
    """Test WidgetManager functionality"""
    print("\\n🧪 Testing WidgetManager...")
    
    try:
        # Set up environment variables for testing
        os.environ['scr_path'] = '/home/z/my-project/LSDAI'
        os.environ['settings_path'] = '/home/z/my-project/LSDAI/settings.json'
        
        # Import and test WidgetManager
        sys.path.insert(0, str(LSDAI_PATH / 'scripts'))
        from enhanced_widgets_en_fixed import WidgetManager
        
        wm = WidgetManager()
        print("✅ WidgetManager created successfully")
        
        # Test widget creation
        wm.create_widgets()
        print("✅ Widgets created successfully")
        
        # Test verbosity control
        verbosity_section = wm.create_verbosity_control_section()
        print("✅ Verbosity control section created successfully")
        
        # Test layout creation
        layout = wm.create_layout()
        print("✅ Layout created successfully")
        
        # Test settings operations
        wm.save_settings()
        print("✅ Settings saved successfully")
        
        wm.load_settings()
        print("✅ Settings loaded successfully")
        
        # Test callbacks
        wm.setup_callbacks()
        print("✅ Callbacks set up successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ WidgetManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_dependencies():
    """Test required file dependencies"""
    print("\\n🧪 Testing File Dependencies...")
    
    required_files = [
        '/home/z/my-project/LSDAI/modules/widget_factory.py',
        '/home/z/my-project/LSDAI/modules/verbose_output_manager.py',
        '/home/z/my-project/LSDAI/modules/json_utils.py',
        '/home/z/my-project/LSDAI/modules/webui_utils.py',
        '/home/z/my-project/LSDAI/scripts/enhanced_widgets_en_fixed.py',
        '/home/z/my-project/LSDAI/scripts/_models_data.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\\n❌ Missing {len(missing_files)} required files")
        return False
    else:
        print("\\n✅ All required files present")
        return True

def main():
    """Run all tests"""
    print("🚀 LSDAI Widget System Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Dependencies", test_file_dependencies),
        ("Basic Imports", test_imports),
        ("WidgetFactory", test_widget_factory),
        ("VerboseOutputManager", test_verbose_manager),
        ("json_utils", test_json_utils),
        ("webui_utils", test_webui_utils),
        ("WidgetManager", test_widget_manager)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\\n📈 Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\\n🎉 All tests passed! The widget system is ready to use.")
        return True
    else:
        print(f"\\n⚠️  {failed} tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
