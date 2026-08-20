import sqlite3
import os


os.makedirs("data", exist_ok=True)

connection = sqlite3.connect(
    "data/sales.db"
)

cursor = connection.cursor()


cursor.execute("""
DROP TABLE IF EXISTS sales
""")


cursor.execute("""
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    city TEXT,
    product TEXT,
    quarter TEXT,
    revenue REAL,
    units INTEGER
)
""")


sales_data = [
    ("Mumbai", "Laptop", "Q1", 520000, 52),
    ("Mumbai", "Software", "Q1", 680000, 85),
    ("Pune", "Laptop", "Q1", 410000, 41),
    ("Pune", "Software", "Q1", 470000, 62),
    ("Delhi", "Laptop", "Q1", 590000, 59),
    ("Delhi", "Software", "Q1", 610000, 76),

    ("Mumbai", "Laptop", "Q2", 610000, 61),
    ("Mumbai", "Software", "Q2", 720000, 90),
    ("Pune", "Laptop", "Q2", 450000, 45),
    ("Pune", "Software", "Q2", 530000, 70),
    ("Delhi", "Laptop", "Q2", 640000, 64),
    ("Delhi", "Software", "Q2", 690000, 82),
]


cursor.executemany("""
INSERT INTO sales
(city, product, quarter, revenue, units)
VALUES (?, ?, ?, ?, ?)
""", sales_data)


connection.commit()
connection.close()

print("Sales database created successfully!")