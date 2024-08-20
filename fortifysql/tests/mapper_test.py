from fortifysql.orm import Table, Column, Database
from fortifysql.sql_data_types import Integer, Text, Real, Blob

def test_import_table():
    db = Database(":memory:")
    db.query("CREATE TABLE test (c1, c2 INTEGER, c3 REAL, c4 TEXT, c5 BlOB)")
    db.reload_tables()
    table = db.test 
    assert isinstance(table, Table)
    assert isinstance(table.c1, Column)
    assert isinstance(table.c2, Column)
    assert isinstance(table.c3, Column)
    assert isinstance(table.c4, Column)
    assert isinstance(table.c5, Column)
    assert isinstance(table.c1.dtype("1"), Text)
    assert isinstance(table.c2.dtype(1), Integer)
    assert isinstance(table.c3.dtype(1), Real)
    assert isinstance(table.c4.dtype("1"), Text)
    assert isinstance(table.c5.dtype(b'a'), Blob)

