"""
Master test runner

Runs all test suites for the RPG Dependency Analyzer
"""

import sys
import os

# Add parent directory to path for nbimporter
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all test modules
import test_parser_helpers
import test_pattern_detection
import test_dynamic_sql
import test_integration


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*60)
    print("  RPG Dependency Analyzer - Full Test Suite")
    print("="*60)

    try:
        # Run each test suite
        test_parser_helpers.run_all_tests()
        test_pattern_detection.run_all_tests()
        test_dynamic_sql.run_all_tests()
        test_integration.run_all_tests()

        print("\n" + "="*60)
        print("  ✅ ALL TEST SUITES PASSED!")
        print("="*60 + "\n")
        return 0

    except AssertionError as e:
        print("\n" + "="*60)
        print(f"  ❌ TEST FAILED: {e}")
        print("="*60 + "\n")
        return 1
    except Exception as e:
        print("\n" + "="*60)
        print(f"  ❌ ERROR: {e}")
        print("="*60 + "\n")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
