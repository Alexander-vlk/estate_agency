import sqlite3

conn = sqlite3.connect("agency.sqlite")
cursor = conn.cursor()

with open("create_tables.sql", "r") as f:
    cursor.executescript(f.read())

conn.commit()
conn.close()
