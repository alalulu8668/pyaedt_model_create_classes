#!/usr/bin/env python3
"""
Simple test script to check AEDT licensing and EDB availability.
Run this first to diagnose licensing issues.
"""

import os
import sys

print("="*60)
print("AEDT/EDB LICENSE AND VERSION TEST")
print("="*60)

# Test 1: Check if PyAEDT is properly installed
print("\n1. Testing PyAEDT import...")
try:
    import pyaedt
    print(f"✓ PyAEDT imported successfully - version: {pyaedt.__version__}")
except ImportError as e:
    print(f"✗ PyAEDT import failed: {e}")
    sys.exit(1)

# Test 2: Check EDB import
print("\n2. Testing EDB import...")
try:
    from pyaedt import Edb
    print("✓ EDB class imported successfully")
except ImportError as e:
    print(f"✗ EDB import failed: {e}")
    sys.exit(1)

# Test 3: Check AEDT installation
print("\n3. Checking AEDT installation...")
try:
    from pyaedt.generic.general_methods import inside_desktop
    if inside_desktop:
        print("✓ Running inside AEDT Desktop")
    else:
        print("⚠ Running outside AEDT Desktop")
        
    # Try to get AEDT version info
    from pyaedt.application.Variables import LATEST_AVAILABLE_VERSION
    print(f"✓ Latest available AEDT version: {LATEST_AVAILABLE_VERSION}")
except Exception as e:
    print(f"⚠ Could not determine AEDT version info: {e}")

# Test 4: Simple EDB creation test
print("\n4. Testing EDB creation with minimal setup...")
test_path = os.path.join(os.getcwd(), "test_edb_license")

# Try different approaches
versions_to_try = [None, "2024.1", "2023.2", "2023.1", "2022.2"]

for i, version in enumerate(versions_to_try):
    version_str = f"version {version}" if version else "default version"
    print(f"\n   Test 4.{i+1}: Trying {version_str}...")
    
    try:
        if os.path.exists(test_path):
            import shutil
            shutil.rmtree(test_path)
            
        if version:
            edb = Edb(test_path, edbversion=version)
        else:
            edb = Edb(test_path)
            
        print(f"   ✓ EDB created successfully with {version_str}")
        print(f"   EDB version: {getattr(edb, 'edbversion', 'Unknown')}")
        
        # Clean up
        edb.close_edb()
        if os.path.exists(test_path):
            import shutil
            shutil.rmtree(test_path)
        
        print(f"\n✓ SUCCESS: EDB licensing works with {version_str}")
        break
        
    except Exception as e:
        print(f"   ✗ Failed with {version_str}: {e}")
        
        # Clean up on failure
        try:
            if 'edb' in locals():
                edb.close_edb()
        except:
            pass
        if os.path.exists(test_path):
            import shutil
            shutil.rmtree(test_path)
            
        if i == len(versions_to_try) - 1:  # Last attempt
            print(f"\n✗ FAILURE: All EDB initialization attempts failed")
            print("\nLICENSING TROUBLESHOOTING:")
            print("- Ensure AEDT Electronics Desktop is properly licensed")
            print("- Try opening AEDT Electronics Desktop first")
            print("- Check license server connectivity")
            print("- Contact your AEDT administrator")
            print("- Make sure you're running this from within AEDT if required")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60) 