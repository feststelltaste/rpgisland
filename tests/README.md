# RPG Dependency Analyzer Test Suite

This directory contains comprehensive tests for the RPG dependency analyzer notebook.

## Overview

The test suite uses `nbimporter` to import functions from `rpg_dependency_analyzer.ipynb` and test them in isolation and integration.

## Test Files

### `test_parser_helpers.py`
Tests the core helper functions:
- `extract_and_strip_string_literals()` - Removes string literals to prevent false positives
- `extract_tables_from_sql()` - Extracts table names from SQL statements
- `is_sql_string()` - Detects if a string contains SQL

**Tests:** 14 test cases

### `test_pattern_detection.py`
Tests the pattern detection functions:
- `detect_dcl_f()` - Free-format file declarations (Dcl-F)
- `detect_f_spec()` - Fixed-format file specifications (F-Spec)
- `detect_opcode()` - Database operations (CHAIN, READ, WRITE, UPDATE, etc.)
- `detect_call()` - Program calls (CALL, CALLP, CALLB)
- `detect_embedded_sql_table()` - Tables in embedded SQL (EXEC SQL)

**Tests:** 17 test cases

### `test_dynamic_sql.py`
Tests dynamic SQL detection (SQL in string literals):
- Single-line SQL statements
- Various SQL operations (SELECT, INSERT, UPDATE, DELETE, JOIN)
- Schema-qualified table names
- False positive prevention

**Tests:** 8 test cases

### `test_integration.py`
Integration tests for the complete parser:
- Parsing real RPG files from the repository
- Free-format RPG
- Mixed-format RPG (fixed + free blocks)
- Embedded SQL
- False positive prevention (string literals not parsed as code)

**Tests:** 5 test cases covering real-world scenarios

## Running Tests

### Run All Tests
```bash
cd /mnt/d/repos/rpgisland
python tests/run_all_tests.py
```

### Run Individual Test Suites
```bash
python tests/test_parser_helpers.py
python tests/test_pattern_detection.py
python tests/test_dynamic_sql.py
python tests/test_integration.py
```

## Requirements

The tests require:
- `nbimporter` - To import functions from Jupyter notebooks
- All dependencies from `requirements.txt`

Install with:
```bash
pip install nbimporter
pip install -r requirements.txt
```

## Test Coverage

The test suite covers:

1. **String Literal Handling** ✓
   - Single quotes, double quotes, embedded quotes
   - Extraction and cleaning
   - False positive prevention (e.g., "Read for update" not parsed as READ opcode)

2. **SQL Detection** ✓
   - Embedded SQL (EXEC SQL blocks)
   - Dynamic SQL (SQL in string literals)
   - Table extraction from various SQL statements
   - Schema-qualified names

3. **Pattern Detection** ✓
   - File declarations (DCL-F, F-Spec)
   - Database operations (CHAIN, READ, WRITE, UPDATE, DELETE)
   - Program calls (CALL, CALLP, CALLB)
   - Context awareness (free vs. fixed format)

4. **Format Support** ✓
   - Free-format RPG (**FREE)
   - Fixed-format RPG (column-based)
   - Mixed-mode RPG (/FREE ... /END-FREE blocks)

5. **Real-World Scenarios** ✓
   - Parsing actual repository files
   - Multi-line SQL with continuations
   - Complex mixed-format programs

## Known Issues

The test suite validates the fix for the original bug:
- **Issue:** Line 69 of RCDLCKDEMO.RPGLE had `dsply 'Read for update'` which was incorrectly parsing "for" as a table name
- **Fix:** String literals are now extracted and cleaned before pattern matching
- **Test:** `test_false_positive_prevention()` ensures this doesn't regress

## Contributing

When adding new parser features:
1. Add unit tests to the appropriate test file
2. Add integration tests if the feature affects parsing workflow
3. Run the full test suite to ensure no regressions
4. Update this README if adding new test files

## Test Output

Successful test run output:
```
============================================================
  RPG Dependency Analyzer - Full Test Suite
============================================================

=== Running Parser Helper Tests ===
✓ test_extract_string_literals_single_quotes passed
✓ test_extract_string_literals_double_quotes passed
...
✅ All parser helper tests passed!

=== Running Pattern Detection Tests ===
✓ test_detect_dcl_f_basic passed
...
✅ All pattern detection tests passed!

=== Running Dynamic SQL Detection Tests ===
✓ test_dynamic_sql_single_line_select passed
...
✅ All dynamic SQL tests passed!

=== Running Integration Tests ===
✓ test_parse_rcdlckdemo_file passed
...
✅ All integration tests passed!

============================================================
  ✅ ALL TEST SUITES PASSED!
============================================================
```
