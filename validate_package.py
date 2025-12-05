#!/usr/bin/env python3
"""
Simple package validation - no external dependencies needed
"""

import os
import json
import sys

def validate_files():
    """Validate all required files exist"""
    print("\n" + "="*70)
    print(" PACKAGE VALIDATION")
    print("="*70)
    
    required_files = [
        ('Dockerfile', 'Docker configuration'),
        ('requirements.txt', 'Python dependencies'),
        ('README.md', 'Documentation'),
        ('.dockerignore', 'Docker ignore file'),
        ('src/__init__.py', 'Package init'),
        ('src/__main__.py', 'Entry point'),
        ('src/main.py', 'Main logic'),
        ('.actor/actor.json', 'Actor metadata'),
        ('.actor/input_schema.json', 'Input schema'),
        ('.actor/output_schema.json', 'Output schema'),
        ('.actor/dataset_schema.json', 'Dataset schema'),
    ]
    
    print("\n✓ Checking required files...")
    all_found = True
    
    for file_path, description in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✓ {file_path:30s} ({size:,} bytes) - {description}")
        else:
            print(f"  ✗ {file_path:30s} - MISSING!")
            all_found = False
    
    return all_found

def validate_json_files():
    """Validate JSON files"""
    print("\n✓ Validating JSON files...")
    
    json_files = [
        '.actor/actor.json',
        '.actor/input_schema.json',
        '.actor/output_schema.json',
        '.actor/dataset_schema.json'
    ]
    
    all_valid = True
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            print(f"  ✓ {file_path} - Valid JSON")
        except json.JSONDecodeError as e:
            print(f"  ✗ {file_path} - Invalid JSON: {e}")
            all_valid = False
        except Exception as e:
            print(f"  ✗ {file_path} - Error: {e}")
            all_valid = False
    
    return all_valid

def validate_python_syntax():
    """Validate Python files syntax"""
    print("\n✓ Validating Python syntax...")
    
    python_files = [
        'src/__init__.py',
        'src/__main__.py',
        'src/main.py'
    ]
    
    all_valid = True
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
            print(f"  ✓ {file_path} - Valid syntax")
        except SyntaxError as e:
            print(f"  ✗ {file_path} - Syntax error: {e}")
            all_valid = False
        except Exception as e:
            print(f"  ✗ {file_path} - Error: {e}")
            all_valid = False
    
    return all_valid

def check_zip():
    """Check if ZIP file exists"""
    print("\n✓ Checking deployment ZIP...")
    
    if os.path.exists('httrack-actor.zip'):
        size = os.path.getsize('httrack-actor.zip')
        print(f"  ✓ httrack-actor.zip exists ({size:,} bytes)")
        return True
    else:
        print("  ✗ httrack-actor.zip not found")
        return False

def main():
    """Run all validations"""
    
    results = []
    
    results.append(('Required Files', validate_files()))
    results.append(('JSON Configuration', validate_json_files()))
    results.append(('Python Syntax', validate_python_syntax()))
    results.append(('Deployment ZIP', check_zip()))
    
    print("\n" + "="*70)
    print(" VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}  {name}")
    
    print("="*70)
    print(f"\nResults: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n" + "="*70)
        print(" ✅ ALL VALIDATIONS PASSED")
        print("="*70)
        print("\n Your package is READY TO DEPLOY!")
        print("\n Next steps:")
        print("  1. Open: DOWNLOAD_ACTOR.html in browser")
        print("  2. Download: httrack-actor.zip")
        print("  3. Upload to: https://console.apify.com/")
        print("\n" + "="*70)
        return True
    else:
        print(f"\n⚠️  {total - passed} validation(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


