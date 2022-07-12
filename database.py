from flask import g
import _sqlite3

def connect_db():
    sql = _sqlite3.connect('answer.db')
    sql.row_factory =_sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db