import os
import sqlite3

DB_PATH = os.getenv("DB_PATH", "sales_data.db")


def init_db() -> None:
    """Create the SQLite database with sample data if it doesn't exist."""
    if os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            region TEXT,
            sale_date TEXT,
            quantity INTEGER,
            price_per_unit REAL
        )
        """
    )
    sample_rows = [
        ("Widget", "North", "2024-01-15", 10, 9.99),
        ("Widget", "South", "2024-02-10", 5, 9.99),
        ("Gadget", "North", "2024-03-20", 7, 14.50),
        ("Gadget", "West", "2024-04-05", 12, 14.50),
        ("Doohickey", "East", "2024-05-30", 20, 4.25),
        ("Doohickey", "South", "2024-06-01", 15, 4.25),
    ]
    cur.executemany(
        "INSERT INTO sales (product_name, region, sale_date, quantity, price_per_unit) VALUES (?,?,?,?,?)",
        sample_rows,
    )
    conn.commit()
    conn.close()


def get_db_schema() -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='sales'")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""
