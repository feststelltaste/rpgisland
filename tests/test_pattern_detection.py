"""
Tests for pattern detection functions

Tests the pattern detection functions:
- detect_dcl_f()
- detect_f_spec()
- detect_opcode()
- detect_call()
- detect_embedded_sql_table()
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import nbimporter
import rpg_dependency_analyzer as rda


def test_detect_dcl_f_basic():
    """Test basic DCL-F detection"""
    line = "Dcl-F QCUSTCDT Usage(*Update:*Delete:*Output);"
    upper_line = line.upper()
    result = rda.detect_dcl_f(line, upper_line, is_free_context=True)

    assert result is not None
    assert result['type'] == 'file'
    assert result['name'] == 'QCUSTCDT'
    print("✓ test_detect_dcl_f_basic passed")


def test_detect_dcl_f_with_extfile():
    """Test DCL-F detection with EXTFILE"""
    line = "Dcl-F MYFILE DISK EXTFILE('LIBRARY/PHYSFILE');"
    upper_line = line.upper()
    result = rda.detect_dcl_f(line, upper_line, is_free_context=True)

    assert result is not None
    assert result['type'] == 'file'
    assert result['name'] == 'MYFILE'
    print("✓ test_detect_dcl_f_with_extfile passed")


def test_detect_dcl_f_not_free_context():
    """Test DCL-F should not match when not in free context"""
    line = "Dcl-F QCUSTCDT Usage(*Update);"
    upper_line = line.upper()
    result = rda.detect_dcl_f(line, upper_line, is_free_context=False)

    assert result is None
    print("✓ test_detect_dcl_f_not_free_context passed")


def test_detect_f_spec_basic():
    """Test basic F-Spec detection (fixed format)"""
    line = "FQCUSTCDT  UF   E           K DISK"
    result = rda.detect_f_spec(line, is_free_context=False)

    assert result is not None
    assert result['type'] == 'file'
    assert result['name'] == 'QCUSTCDT'
    print("✓ test_detect_f_spec_basic passed")


def test_detect_f_spec_in_free_context():
    """Test F-Spec should not match in free context"""
    line = "FQCUSTCDT  UF   E           K DISK"
    result = rda.detect_f_spec(line, is_free_context=True)

    assert result is None
    print("✓ test_detect_f_spec_in_free_context passed")


def test_detect_opcode_chain():
    """Test CHAIN opcode detection"""
    line = "     chain(e) RRN QCUSTCDT;"
    result = rda.detect_opcode(line)

    assert result is not None
    assert result['type'] == 'table_access'
    assert result['name'] == 'QCUSTCDT'
    assert result['operation'] == 'CHAIN'
    print("✓ test_detect_opcode_chain passed")


def test_detect_opcode_read():
    """Test READ opcode detection"""
    line = "     read CUSTOMERS;"
    result = rda.detect_opcode(line)

    assert result is not None
    assert result['type'] == 'table_access'
    assert result['name'] == 'CUSTOMERS'
    assert result['operation'] == 'READ'
    print("✓ test_detect_opcode_read passed")


def test_detect_opcode_write():
    """Test WRITE opcode detection"""
    line = "     write CUSREC;"
    result = rda.detect_opcode(line)

    assert result is not None
    assert result['type'] == 'table_access'
    assert result['name'] == 'CUSREC'
    assert result['operation'] == 'WRITE'
    print("✓ test_detect_opcode_write passed")


def test_detect_opcode_update():
    """Test UPDATE opcode detection"""
    line = "     update EMPREC;"
    result = rda.detect_opcode(line)

    assert result is not None
    assert result['type'] == 'table_access'
    assert result['name'] == 'EMPREC'
    assert result['operation'] == 'UPDATE'
    print("✓ test_detect_opcode_update passed")


def test_detect_opcode_in_string_literal():
    """Test that opcodes in string literals are NOT detected"""
    line = "dsply 'Read for update' ' ' reply;"
    result = rda.detect_opcode(line)

    # This should NOT match because 'Read' is inside a string literal
    # The detect_opcode function receives the cleaned line from parse_rpg_file
    # For this test, we need to clean it first
    cleaned, _ = rda.extract_and_strip_string_literals(line)
    result = rda.detect_opcode(cleaned)

    assert result is None
    print("✓ test_detect_opcode_in_string_literal passed")


def test_detect_call_basic():
    """Test basic CALL detection"""
    line = "     call 'MYPROG';"
    result = rda.detect_call(line)

    assert result is not None
    assert result['type'] == 'program_call'
    assert result['name'] == 'MYPROG'
    print("✓ test_detect_call_basic passed")


def test_detect_call_callp():
    """Test CALLP detection"""
    line = "     callp RCDLCKDSP(reply: myPSDS_ptr);"
    result = rda.detect_call(line)

    assert result is not None
    assert result['type'] == 'program_call'
    assert result['name'] == 'RCDLCKDSP'
    print("✓ test_detect_call_callp passed")


def test_detect_call_callb():
    """Test CALLB detection"""
    line = "     callb SUBPROC;"
    result = rda.detect_call(line)

    assert result is not None
    assert result['type'] == 'program_call'
    assert result['name'] == 'SUBPROC'
    print("✓ test_detect_call_callb passed")


def test_detect_embedded_sql_select():
    """Test embedded SQL SELECT detection"""
    line = "C/EXEC SQL SELECT * FROM EMPLOYEE INTO :EMPDATA"
    result = rda.detect_embedded_sql_table(line)

    assert result is not None
    assert result['type'] == 'table_access'
    assert 'EMPLOYEE' in result['name']
    print("✓ test_detect_embedded_sql_select passed")


def test_detect_embedded_sql_insert():
    """Test embedded SQL INSERT detection"""
    line = "C/EXEC SQL INSERT INTO CUSTOMERS VALUES (:CUSTDATA)"
    result = rda.detect_embedded_sql_table(line)

    assert result is not None
    assert result['type'] == 'table_access'
    assert 'CUSTOMERS' in result['name']
    print("✓ test_detect_embedded_sql_insert passed")


def test_detect_embedded_sql_update():
    """Test embedded SQL UPDATE detection"""
    line = "C/EXEC SQL UPDATE EMPLOYEE SET SALARY = :NEWSALARY WHERE EMPNO = :EMPNO"
    result = rda.detect_embedded_sql_table(line)

    assert result is not None
    assert result['type'] == 'table_access'
    assert 'EMPLOYEE' in result['name']
    print("✓ test_detect_embedded_sql_update passed")


def test_detect_embedded_sql_no_match():
    """Test that non-SQL lines don't match"""
    line = "     chain(e) RRN QCUSTCDT;"
    result = rda.detect_embedded_sql_table(line)

    assert result is None
    print("✓ test_detect_embedded_sql_no_match passed")


def run_all_tests():
    """Run all pattern detection tests"""
    print("\n=== Running Pattern Detection Tests ===\n")

    test_detect_dcl_f_basic()
    test_detect_dcl_f_with_extfile()
    test_detect_dcl_f_not_free_context()
    test_detect_f_spec_basic()
    test_detect_f_spec_in_free_context()
    test_detect_opcode_chain()
    test_detect_opcode_read()
    test_detect_opcode_write()
    test_detect_opcode_update()
    test_detect_opcode_in_string_literal()
    test_detect_call_basic()
    test_detect_call_callp()
    test_detect_call_callb()
    test_detect_embedded_sql_select()
    test_detect_embedded_sql_insert()
    test_detect_embedded_sql_update()
    test_detect_embedded_sql_no_match()

    print("\n✅ All pattern detection tests passed!\n")


if __name__ == '__main__':
    run_all_tests()
