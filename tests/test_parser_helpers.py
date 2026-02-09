"""
Tests for parser helper functions

Tests the core helper functions:
- extract_and_strip_string_literals()
- extract_tables_from_sql()
- is_sql_string()
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import nbimporter
import rpg_dependency_analyzer as rda


def test_extract_string_literals_single_quotes():
    """Test extraction of string literals with single quotes"""
    line = "dsply 'Read for update' ' ' reply;"
    cleaned, strings = rda.extract_and_strip_string_literals(line)

    assert cleaned == "dsply '' '' reply;"
    assert len(strings) == 2
    assert strings[0] == 'Read for update'
    assert strings[1] == ' '
    print("✓ test_extract_string_literals_single_quotes passed")


def test_extract_string_literals_double_quotes():
    """Test extraction of string literals with double quotes"""
    line = 'Cmd = "SELECT * FROM TABLE";'
    cleaned, strings = rda.extract_and_strip_string_literals(line)

    assert cleaned == 'Cmd = "";'
    assert len(strings) == 1
    assert strings[0] == 'SELECT * FROM TABLE'
    print("✓ test_extract_string_literals_double_quotes passed")


def test_extract_string_literals_embedded_quotes():
    """Test extraction with embedded/escaped quotes (RPG uses '' for embedded ')"""
    line = "dsply 'Customer''s name' ' ' reply;"
    cleaned, strings = rda.extract_and_strip_string_literals(line)

    assert cleaned == "dsply '' '' reply;"
    assert len(strings) == 2
    assert strings[0] == "Customer's name"  # Double quotes converted to single
    print("✓ test_extract_string_literals_embedded_quotes passed")


def test_extract_string_literals_no_strings():
    """Test line with no string literals"""
    line = "chain(e) RRN QCUSTCDT;"
    cleaned, strings = rda.extract_and_strip_string_literals(line)

    assert cleaned == line
    assert len(strings) == 0
    print("✓ test_extract_string_literals_no_strings passed")


def test_is_sql_string_select():
    """Test SQL detection for SELECT statement"""
    sql = "SELECT LASTNAME FROM CORPDATA.EMPLOYEE WHERE EMPNO = ?"
    assert rda.is_sql_string(sql) == True
    print("✓ test_is_sql_string_select passed")


def test_is_sql_string_insert():
    """Test SQL detection for INSERT statement"""
    sql = "INSERT INTO CUSTOMERS (NAME, CITY) VALUES (?, ?)"
    assert rda.is_sql_string(sql) == True
    print("✓ test_is_sql_string_insert passed")


def test_is_sql_string_update():
    """Test SQL detection for UPDATE statement"""
    sql = "UPDATE EMPLOYEE SET SALARY = ? WHERE EMPNO = ?"
    assert rda.is_sql_string(sql) == True
    print("✓ test_is_sql_string_update passed")


def test_is_sql_string_non_sql():
    """Test SQL detection returns False for non-SQL strings"""
    text = "Read for update"
    assert rda.is_sql_string(text) == False
    print("✓ test_is_sql_string_non_sql passed")


def test_extract_tables_from_sql_select():
    """Test table extraction from SELECT statement"""
    sql = "SELECT LASTNAME FROM CORPDATA.EMPLOYEE WHERE EMPNO = ?"
    tables = rda.extract_tables_from_sql(sql)

    assert len(tables) == 1
    assert 'EMPLOYEE' in tables
    print("✓ test_extract_tables_from_sql_select passed")


def test_extract_tables_from_sql_join():
    """Test table extraction from JOIN statement"""
    sql = "SELECT * FROM ORDERS O JOIN CUSTOMERS C ON O.CUSTID = C.ID"
    tables = rda.extract_tables_from_sql(sql)

    assert len(tables) == 2
    assert 'ORDERS' in tables
    assert 'CUSTOMERS' in tables
    print("✓ test_extract_tables_from_sql_join passed")


def test_extract_tables_from_sql_insert():
    """Test table extraction from INSERT statement"""
    sql = "INSERT INTO CUSTOMERS (NAME, CITY) VALUES (?, ?)"
    tables = rda.extract_tables_from_sql(sql)

    assert len(tables) == 1
    assert 'CUSTOMERS' in tables
    print("✓ test_extract_tables_from_sql_insert passed")


def test_extract_tables_from_sql_update():
    """Test table extraction from UPDATE statement"""
    sql = "UPDATE EMPLOYEE SET SALARY = ? WHERE EMPNO = ?"
    tables = rda.extract_tables_from_sql(sql)

    assert len(tables) == 1
    assert 'EMPLOYEE' in tables
    print("✓ test_extract_tables_from_sql_update passed")


def test_extract_tables_from_sql_delete():
    """Test table extraction from DELETE statement"""
    sql = "DELETE FROM ORDERS WHERE ORDERID = ?"
    tables = rda.extract_tables_from_sql(sql)

    assert len(tables) == 1
    assert 'ORDERS' in tables
    print("✓ test_extract_tables_from_sql_delete passed")


def test_extract_tables_with_schema():
    """Test table extraction preserves only table name when schema.table format is used"""
    sql = "SELECT * FROM CORPDATA.EMPLOYEE"
    tables = rda.extract_tables_from_sql(sql)

    assert len(tables) == 1
    assert 'EMPLOYEE' in tables
    assert 'CORPDATA.EMPLOYEE' not in tables  # Should only have table name
    print("✓ test_extract_tables_with_schema passed")


def run_all_tests():
    """Run all helper function tests"""
    print("\n=== Running Parser Helper Tests ===\n")

    test_extract_string_literals_single_quotes()
    test_extract_string_literals_double_quotes()
    test_extract_string_literals_embedded_quotes()
    test_extract_string_literals_no_strings()
    test_is_sql_string_select()
    test_is_sql_string_insert()
    test_is_sql_string_update()
    test_is_sql_string_non_sql()
    test_extract_tables_from_sql_select()
    test_extract_tables_from_sql_join()
    test_extract_tables_from_sql_insert()
    test_extract_tables_from_sql_update()
    test_extract_tables_from_sql_delete()
    test_extract_tables_with_schema()

    print("\n✅ All parser helper tests passed!\n")


if __name__ == '__main__':
    run_all_tests()
