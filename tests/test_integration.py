"""
Integration tests for the RPG parser

Tests the complete parse_rpg_file() function with real-world scenarios
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import nbimporter
import rpg_dependency_analyzer as rda


def test_parse_rcdlckdemo_file():
    """Test parsing the actual RCDLCKDEMO.RPGLE file"""
    filepath = '/mnt/d/repos/rpgisland/src/IBM-i-RPG-Free-CLP-Code/RcdLckDsp/RCDLCKDEMO.RPGLE'

    # Check if file exists
    if not os.path.exists(filepath):
        print(f"⚠ Skipping test_parse_rcdlckdemo_file - file not found: {filepath}")
        return

    dependencies = rda.parse_rpg_file(filepath)

    # Should find dependencies
    assert len(dependencies) > 0

    # Should find the QCUSTCDT file declaration
    file_deps = [d for d in dependencies if d['type'] == 'file' and d['name'] == 'QCUSTCDT']
    assert len(file_deps) > 0

    # Should find the RCDLCKDSP program call
    call_deps = [d for d in dependencies if d['type'] == 'program_call' and d['name'] == 'RCDLCKDSP']
    assert len(call_deps) > 0

    # Should find QCmdexc program call
    qcmdexc_deps = [d for d in dependencies if d['type'] == 'program_call' and d['name'] == 'QCMDEXC']
    assert len(qcmdexc_deps) > 0

    # Should NOT find 'for' as a table (this was the bug - line 69 has 'Read for update' in a string)
    false_positive = [d for d in dependencies if d.get('name') == 'for' or d.get('name') == 'FOR']
    assert len(false_positive) == 0, "Found false positive 'for' as table - string literal not properly stripped"

    print("✓ test_parse_rcdlckdemo_file passed")


def test_parse_free_format_rpg():
    """Test parsing free-format RPG code (simulated)"""
    # Create a temporary test file
    test_file = '/tmp/test_free_format.rpgle'

    with open(test_file, 'w') as f:
        f.write("""**free
Ctl-Opt DFTACTGRP(*NO);

Dcl-F CUSTOMERS DISK USAGE(*INPUT);
Dcl-F ORDERS DISK USAGE(*OUTPUT);

Dcl-S stmt Char(500) INZ('SELECT * FROM EMPLOYEE WHERE ID = ?');

chain 'KEY001' CUSTOMERS;
write ORDREC;
callp CALCULATE_TOTALS();

*inlr = *on;
return;
""")

    dependencies = rda.parse_rpg_file(test_file)

    # Should find file declarations
    file_deps = [d for d in dependencies if d['type'] == 'file']
    assert len(file_deps) >= 2
    assert any(d['name'] == 'CUSTOMERS' for d in file_deps)
    assert any(d['name'] == 'ORDERS' for d in file_deps)

    # Should find dynamic SQL table
    sql_deps = [d for d in dependencies if d.get('name') == 'EMPLOYEE']
    assert len(sql_deps) > 0, "Should detect EMPLOYEE table from dynamic SQL"

    # Should find table operations
    chain_deps = [d for d in dependencies if d.get('operation') == 'CHAIN']
    assert len(chain_deps) > 0

    write_deps = [d for d in dependencies if d.get('operation') == 'WRITE']
    assert len(write_deps) > 0

    # Should find program call
    call_deps = [d for d in dependencies if d['type'] == 'program_call']
    assert any(d['name'] == 'CALCULATE_TOTALS' for d in call_deps)

    # Cleanup
    os.remove(test_file)

    print("✓ test_parse_free_format_rpg passed")


def test_parse_mixed_format_rpg():
    """Test parsing mixed-format RPG (fixed + free blocks)"""
    test_file = '/tmp/test_mixed_format.rpgle'

    with open(test_file, 'w') as f:
        f.write("""     FQCUSTCDT  UF   E           K DISK
     D custName       S             30A

     /FREE
     chain 'ABC123' QCUSTCDT;
     if %found(QCUSTCDT);
         custName = LSTNAM;
     endif;
     /END-FREE

     C                   READ      QCUSTCDT
     C                   RETURN
""")

    dependencies = rda.parse_rpg_file(test_file)

    # Should find F-Spec file
    file_deps = [d for d in dependencies if d['type'] == 'file' and d['name'] == 'QCUSTCDT']
    assert len(file_deps) > 0

    # Should find CHAIN in free block
    chain_deps = [d for d in dependencies if d.get('operation') == 'CHAIN']
    assert len(chain_deps) > 0

    # Should find READ in fixed block
    read_deps = [d for d in dependencies if d.get('operation') == 'READ']
    assert len(read_deps) > 0

    # Cleanup
    os.remove(test_file)

    print("✓ test_parse_mixed_format_rpg passed")


def test_parse_embedded_sql():
    """Test parsing embedded SQL statements"""
    test_file = '/tmp/test_embedded_sql.rpgle'

    with open(test_file, 'w') as f:
        f.write("""**free
Ctl-Opt DFTACTGRP(*NO);

Dcl-S empName Char(50);
Dcl-S empId Packed(9:0);

// Embedded SQL
C/EXEC SQL
C+ SELECT LASTNAME INTO :empName
C+ FROM EMPLOYEE
C+ WHERE EMPNO = :empId
C/END-EXEC

C/EXEC SQL INSERT INTO AUDIT_LOG VALUES (:empId, :empName)
C/END-EXEC

*inlr = *on;
""")

    dependencies = rda.parse_rpg_file(test_file)

    # Should find EMPLOYEE table from SELECT
    employee_deps = [d for d in dependencies if 'EMPLOYEE' in d.get('name', '')]
    assert len(employee_deps) > 0, "Should detect EMPLOYEE table from embedded SQL SELECT"

    # Should find AUDIT_LOG table from INSERT
    audit_deps = [d for d in dependencies if 'AUDIT_LOG' in d.get('name', '')]
    assert len(audit_deps) > 0, "Should detect AUDIT_LOG table from embedded SQL INSERT"

    # Cleanup
    os.remove(test_file)

    print("✓ test_parse_embedded_sql passed")


def test_false_positive_prevention():
    """Test that string literals don't create false positives"""
    test_file = '/tmp/test_false_positives.rpgle'

    with open(test_file, 'w') as f:
        f.write("""**free
// These should NOT be detected as actual code:
dsply 'Read for update' ' ' reply;
dsply 'chain to FAKETABLE' ' ' reply;
dsply 'call FAKEPROG' ' ' reply;
dsply 'write to FAKEOUT' ' ' reply;

// These SHOULD be detected:
chain 'KEY' REALTABLE;
call REALPROG;

*inlr = *on;
""")

    dependencies = rda.parse_rpg_file(test_file)

    # Should NOT find false positives from string literals
    assert not any(d.get('name') == 'for' for d in dependencies), "False positive: 'for' detected"
    assert not any(d.get('name') == 'FAKETABLE' for d in dependencies), "False positive: FAKETABLE detected"
    assert not any(d.get('name') == 'FAKEPROG' for d in dependencies), "False positive: FAKEPROG detected"
    assert not any(d.get('name') == 'FAKEOUT' for d in dependencies), "False positive: FAKEOUT detected"

    # Should find real dependencies
    assert any(d.get('name') == 'REALTABLE' for d in dependencies), "Real dependency REALTABLE not found"
    assert any(d.get('name') == 'REALPROG' for d in dependencies), "Real dependency REALPROG not found"

    # Cleanup
    os.remove(test_file)

    print("✓ test_false_positive_prevention passed")


def run_all_tests():
    """Run all integration tests"""
    print("\n=== Running Integration Tests ===\n")

    test_parse_rcdlckdemo_file()
    test_parse_free_format_rpg()
    test_parse_mixed_format_rpg()
    test_parse_embedded_sql()
    test_false_positive_prevention()

    print("\n✅ All integration tests passed!\n")


if __name__ == '__main__':
    run_all_tests()
