import sqlite3


DB_NAME = 'agency.sqlite'


def get_db_connection():
    """Возвращает объект подключения к sqlite"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
