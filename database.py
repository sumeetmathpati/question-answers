from flask import g
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor

# sqlite connection

# def connect_db():
#     sql = sqlite3.connect('./questions.db')
#     sql.row_factory = sqlite3.Row
#     return sql

# def get_db():
#     if not hasattr(g, 'sqlite_db'):
#         g.sqlite_db = connect_db()
#     return g.sqlite_db

def connect_db():
    conn = psycopg2.connect('postgres://zyayycrxhxtgsk:d8ffd012ca75ddb17376978461958e8ae963250273ae1cb3a096b364ab75e607@ec2-34-237-247-76.compute-1.amazonaws.com:5432/dannbqld8oej89', cursor_factory=DictCursor)
    conn.autocommit = True
    sql = conn.cursor()
    return conn, sql

def get_db():
    db = connect_db()
    
    if not hasattr(g, 'postgres_db_conn'):
        g.postgres_db_conn = db[0]
    
    if not hasattr(g, 'postgres_db_cur'):
        g.postgres_db_cur = db[1]

    return g.postgres_db_cur

def init_db():
    db = connect_db()

    db[1].execute(open('./schema.sql', 'r').read())
    db[1].close()

    db[0].close()

def init_admin():
    db = connect_db()

    db[1].execute('UPDATE users SET admin = True WHERE username = %s', ('admin', ))

    db[1].close()
    db[0].close()