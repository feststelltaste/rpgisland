"""
Tests for dynamic SQL detection

Tests the parser's ability to detect SQL statements in string literals
and extract table names from them.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import nbimporter
import rpg_dependency_analyzer as rda


def test_dynamic_sql_single_line_select():
    """Test dynamic SQL detection in single-line DCL-S with SELECT"""
    line = "DCL-S STMT CHAR(500) INZ('SELECT LASTNAME FROM CORPDATA.EMPLOYEE WHERE EMPNO = ?');"

    # Extract strings
    cleaned, strings = rda.extract_and_strip_string_literals(line)

    # Check that we found the SQL string
    assert len(strings) == 1
    assert rda.is_sql_string(strings[0])

    # Extract tables from the SQL
    tables = rda.extract_tables_from_sql(strings[0])
    assert len(tables) == 1
    assert 'EMPLOYEE' in tables
    print("✓ test_dynamic_sql_single_line_select passed")


def test_dynamic_sql_insert():
    """Test dynamic SQL detection with INSERT statement"""
    line = "DCL-S STMT CHAR(500) INZ('INSERT INTO CUSTOMERS (NAME, CITY) VALUES (?, ?)');"

    cleaned, strings = rda.extract_and_strip_string_literals(line)

    assert len(strings) == 1
    assert rda.is_sql_string(strings[0])

    tables = rda.extract_tables_from_sql(strings[0])
    assert len(tables) == 1
    assert 'CUSTOMERS' in tables
    print("✓ test_dynamic_sql_insert passed")


def test_dynamic_sql_update():
    """Test dynamic SQL detection with UPDATE statement"""
    line = "DCL-S STMT CHAR(500) INZ('UPDATE EMPLOYEE SET SALARY = ? WHERE EMPNO = ?');"

    cleaned, strings = rda.extract_and_strip_string_literals(line)

    assert len(strings) == 1
    assert rda.is_sql_string(strings[0])

    tables = rda.extract_tables_from_sql(strings[0])
    assert len(tables) == 1
    assert 'EMPLOYEE' in tables
    print("✓ test_dynamic_sql_update passed")


def test_dynamic_sql_delete():
    """Test dynamic SQL detection with DELETE statement"""
    line = "DCL-S STMT CHAR(500) INZ('DELETE FROM ORDERS WHERE ORDERID = ?');"

    cleaned, strings = rda.extract_and_strip_string_literals(line)

    assert len(strings) == 1
    assert rda.is_sql_string(strings[0])

    tables = rda.extract_tables_from_sql(strings[0])
    assert len(tables) == 1
    assert 'ORDERS' in tables
    print("✓ test_dynamic_sql_delete passed")


def test_dynamic_sql_join():
    """Test dynamic SQL detection with JOIN"""
    line = "DCL-S STMT CHAR(500) INZ('SELECT * FROM ORDERS O JOIN CUSTOMERS C ON O.CUSTID = C.ID');"

    cleaned, strings = rda.extract_and_strip_string_literals(line)

    assert len(strings) == 1
    assert rda.is_sql_string(strings[0])

    tables = rda.extract_tables_from_sql(strings[0])
    assert len(tables) == 2
    assert 'ORDERS' in tables
    assert 'CUSTOMERS' in tables
    print("✓ test_dynamic_sql_join passed")


def test_non_sql_string_not_detected():
    """Test that non-SQL strings are not detected as SQL"""
    line = "dsply 'Read for update' ' ' reply;"

    cleaned, strings = rda.extract_and_strip_string_literals(line)

    assert len(strings) == 2
    assert not rda.is_sql_string(strings[0])  # 'Read for update' is not SQL
    assert not rda.is_sql_string(strings[1])  # ' ' is not SQL
    print("✓ test_non_sql_string_not_detected passed")


def test_dynamic_sql_with_schema():
    """Test dynamic SQL with schema.table notation"""
    line = "DCL-S STMT CHAR(500) INZ('SELECT * FROM MYLIB.MYTABLE WHERE ID = ?');"

    cleaned, strings = rda.extract_and_strip_string_literals(line)

    assert len(strings) == 1
    assert rda.is_sql_string(strings[0])

    tables = rda.extract_tables_from_sql(strings[0])
    assert len(tables) == 1
    assert 'MYTABLE' in tables  # Should extract just the table name
    print("✓ test_dynamic_sql_with_schema passed")


def test_multiple_strings_one_sql():
    """Test line with multiple strings where only one is SQL"""
    line = "dsply 'Message' 'SELECT * FROM CUSTOMERS' reply;"

    cleaned, strings = rda.extract_and_strip_string_literals(line)

    assert len(strings) == 2
    assert not rda.is_sql_string(strings[0])  # 'Message' is not SQL
    assert rda.is_sql_string(strings[1])      # Second string is SQL

    # Extract tables from SQL string
    tables = rda.extract_tables_from_sql(strings[1])
    assert len(tables) == 1
    assert 'CUSTOMERS' in tables
    print("✓ test_multiple_strings_one_sql passed")


def run_all_tests():
    """Run all dynamic SQL tests"""
    print("\n=== Running Dynamic SQL Detection Tests ===\n")

    test_dynamic_sql_single_line_select()
    test_dynamic_sql_insert()
    test_dynamic_sql_update()
    test_dynamic_sql_delete()
    test_dynamic_sql_join()
    test_non_sql_string_not_detected()
    test_dynamic_sql_with_schema()
    test_multiple_strings_one_sql()

    print("\n✅ All dynamic SQL tests passed!\n")


if __name__ == '__main__':
    run_all_tests()
