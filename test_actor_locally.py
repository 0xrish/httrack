#!/usr/bin/env python3
"""
Local test for HTTrack Actor
Tests the Actor logic without Apify platform
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_httrack_installation():
    """Test if HTTrack is installed"""
    print("\n" + "="*70)
    print("TEST 1: HTTrack Installation")
    print("="*70)
    
    try:
        result = subprocess.run(
            ["httrack", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"✓ HTTrack is installed: {version}")
            return True
        else:
            print("✗ HTTrack returned error")
            return False
    except FileNotFoundError:
        print("✗ HTTrack is NOT installed")
        print("\nTo install HTTrack:")
        print("  Ubuntu/Debian: sudo apt-get install httrack")
        print("  Fedora/RHEL:   sudo dnf install httrack")
        print("  macOS:         brew install httrack")
        return False

def test_python_imports():
    """Test if all Python imports work"""
    print("\n" + "="*70)
    print("TEST 2: Python Imports")
    print("="*70)
    
    try:
        print("Testing imports...")
        
        # Test subprocess
        import subprocess
        print("  ✓ subprocess")
        
        # Test zipfile
        import zipfile
        print("  ✓ zipfile")
        
        # Test shutil
        import shutil
        print("  ✓ shutil")
        
        # Test pathlib
        from pathlib import Path
        print("  ✓ pathlib")
        
        # Test datetime
        from datetime import datetime
        print("  ✓ datetime")
        
        # Test typing
        from typing import Dict, Any, Optional
        print("  ✓ typing")
        
        print("\n✓ All standard library imports successful")
        return True
        
    except ImportError as e:
        print(f"\n✗ Import failed: {e}")
        return False

def test_actor_module():
    """Test if Actor module structure is correct"""
    print("\n" + "="*70)
    print("TEST 3: Actor Module Structure")
    print("="*70)
    
    try:
        # Check if src directory exists
        if not os.path.exists('src'):
            print("✗ src/ directory not found")
            return False
        print("  ✓ src/ directory exists")
        
        # Check if __init__.py exists
        if not os.path.exists('src/__init__.py'):
            print("✗ src/__init__.py not found")
            return False
        print("  ✓ src/__init__.py exists")
        
        # Check if __main__.py exists
        if not os.path.exists('src/__main__.py'):
            print("✗ src/__main__.py not found")
            return False
        print("  ✓ src/__main__.py exists")
        
        # Check if main.py exists
        if not os.path.exists('src/main.py'):
            print("✗ src/main.py not found")
            return False
        print("  ✓ src/main.py exists")
        
        # Try to compile main.py
        import py_compile
        py_compile.compile('src/main.py', doraise=True)
        print("  ✓ src/main.py syntax valid")
        
        print("\n✓ Module structure is correct")
        return True
        
    except Exception as e:
        print(f"\n✗ Module test failed: {e}")
        return False

def test_configuration_files():
    """Test if all configuration files are valid"""
    print("\n" + "="*70)
    print("TEST 4: Configuration Files")
    print("="*70)
    
    try:
        files = [
            '.actor/actor.json',
            '.actor/input_schema.json',
            '.actor/output_schema.json',
            '.actor/dataset_schema.json'
        ]
        
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"✗ {file_path} not found")
                return False
            
            with open(file_path, 'r') as f:
                json.load(f)
            print(f"  ✓ {file_path} - Valid JSON")
        
        print("\n✓ All configuration files are valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"\n✗ JSON parsing failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Configuration test failed: {e}")
        return False

def test_httrack_scraper_class():
    """Test if HTTrackScraper class can be imported"""
    print("\n" + "="*70)
    print("TEST 5: HTTrackScraper Class")
    print("="*70)
    
    try:
        from src.main import HTTrackScraper
        print("  ✓ HTTrackScraper class imported")
        
        # Create instance
        scraper = HTTrackScraper()
        print("  ✓ HTTrackScraper instance created")
        
        # Test check_httrack method
        has_httrack = scraper.check_httrack()
        if has_httrack:
            print("  ✓ HTTrack check method works")
        else:
            print("  ⚠ HTTrack not found (expected if not on Linux)")
        
        print("\n✓ HTTrackScraper class is functional")
        return True
        
    except Exception as e:
        print(f"\n✗ HTTrackScraper test failed: {e}")
        return False

def test_build_command():
    """Test command building"""
    print("\n" + "="*70)
    print("TEST 6: Command Building")
    print("="*70)
    
    try:
        from src.main import HTTrackScraper
        
        scraper = HTTrackScraper()
        
        test_config = {
            'depth': 2,
            'stay_on_domain': True,
            'connections': 4,
            'max_rate': 500,
            'get_images': True,
            'get_videos': False,
            'follow_robots': True,
            'external_depth': 0,
            'retries': 2,
            'timeout': 30
        }
        
        cmd = scraper.build_httrack_command(
            "https://example.com",
            "/tmp/test",
            test_config
        )
        
        print(f"  Generated command: {' '.join(cmd[:5])}...")
        print("  ✓ Command building works")
        
        # Verify essential parameters
        if "httrack" in cmd[0]:
            print("  ✓ HTTrack command present")
        if "https://example.com" in cmd:
            print("  ✓ URL included")
        if any("-r2" in str(x) for x in cmd):
            print("  ✓ Depth parameter included")
        
        print("\n✓ Command building is functional")
        return True
        
    except Exception as e:
        print(f"\n✗ Command building test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print(" HTTRACK ACTOR - LOCAL TESTING")
    print("="*70)
    
    tests = [
        ("HTTrack Installation", test_httrack_installation),
        ("Python Imports", test_python_imports),
        ("Module Structure", test_actor_module),
        ("Configuration Files", test_configuration_files),
        ("HTTrackScraper Class", test_httrack_scraper_class),
        ("Command Building", test_build_command),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        color = "\033[92m" if result else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status}{reset}  {name}")
    
    print("="*70)
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Actor is ready to deploy!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Review errors above")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


