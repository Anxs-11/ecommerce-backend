"""
Verification Script
===================
Run this to verify the project setup and run basic tests.
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")


def check_file_exists(filepath):
    """Check if a file exists."""
    path = Path(filepath)
    if path.exists():
        print(f"✅ {filepath}")
        return True
    else:
        print(f"❌ {filepath} - MISSING")
        return False


def verify_project_structure():
    """Verify all required files exist."""
    print_header("VERIFYING PROJECT STRUCTURE")
    
    files_to_check = [
        # Root files
        "README.md",
        "requirements.txt",
        ".gitignore",
        "postman_collection.json",
        
        # App files
        "app/__init__.py",
        "app/main.py",
        
        # Models
        "app/models/__init__.py",
        "app/models/cart.py",
        "app/models/order.py",
        "app/models/coupon.py",
        
        # Services
        "app/services/__init__.py",
        "app/services/in_memory_store.py",
        "app/services/cart_service.py",
        "app/services/checkout_service.py",
        "app/services/coupon_service.py",
        
        # API
        "app/api/__init__.py",
        "app/api/cart.py",
        "app/api/checkout.py",
        "app/api/admin.py",
        
        # Tests
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/test_cart.py",
        "tests/test_checkout.py",
        "tests/test_coupon.py",
    ]
    
    all_exist = True
    for filepath in files_to_check:
        if not check_file_exists(filepath):
            all_exist = False
    
    return all_exist


def run_tests():
    """Run pytest."""
    print_header("RUNNING TESTS")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", "--tb=short"],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False


def main():
    """Main verification function."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║          E-COMMERCE BACKEND - PROJECT VERIFICATION          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Verify structure
    structure_ok = verify_project_structure()
    
    if not structure_ok:
        print("\n❌ Project structure verification FAILED")
        print("   Some files are missing. Please check the output above.")
        return
    
    print("\n✅ Project structure verification PASSED")
    
    # Run tests
    print("\n" + "="*70)
    print("Would you like to run the test suite? (y/n): ", end="")
    
    # For automated scripts, skip the input
    import os
    if os.environ.get('AUTO_RUN') == '1':
        response = 'y'
    else:
        try:
            response = input().lower()
        except:
            response = 'n'
    
    if response == 'y':
        tests_ok = run_tests()
        
        if tests_ok:
            print("\n✅ All tests PASSED")
        else:
            print("\n⚠️  Some tests failed. Please review the output above.")
    
    # Final summary
    print_header("VERIFICATION SUMMARY")
    print("✅ Project structure is complete")
    print("✅ All required files are present")
    print("✅ Ready for development and testing")
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║   NEXT STEPS                                                 ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║   1. Install dependencies:                                   ║
    ║      pip install -r requirements.txt                         ║
    ║                                                              ║
    ║   2. Run the application:                                    ║
    ║      uvicorn app.main:app --reload                           ║
    ║                                                              ║
    ║   3. Run tests:                                              ║
    ║      pytest                                                  ║
    ║                                                              ║
    ║   4. View API documentation:                                 ║
    ║      http://localhost:8000/docs                              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
