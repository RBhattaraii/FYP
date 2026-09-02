#!/usr/bin/env python3
"""
Remove duplicate product rows from a SQLite product database.
Usage:
  python clean_duplicates.py [path/to/db_file.db]
If no path is provided, uses master_products.db.
"""

import os
import sqlite3
import sys

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else 'master_products.db'

if not os.path.exists(DB_PATH):
    print(f"Database file not found: {DB_PATH}")
    sys.exit(1)

print(f"Cleaning duplicates in: {DB_PATH}")
conn = sqlite3.connect(DB_PATH, timeout=30)
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM products')
total_before = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(DISTINCT product_url) FROM products WHERE product_url IS NOT NULL AND product_url != ""')
unique_before = cursor.fetchone()[0]

duplicate_before = total_before - unique_before
print(f"Before cleanup: {total_before} rows, {unique_before} unique URLs, {duplicate_before} duplicates")

cursor.execute('''
    DELETE FROM products
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM products
        WHERE product_url IS NOT NULL AND product_url != ''
        GROUP BY product_url
    )
    AND product_url IS NOT NULL AND product_url != ''
''')
deleted_duplicates = cursor.rowcount
conn.commit()

cursor.execute('DELETE FROM products WHERE product_url IS NULL OR product_url = ""')
null_deleted = cursor.rowcount
conn.commit()

cursor.execute('SELECT COUNT(*) FROM products')
total_after = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(DISTINCT product_url) FROM products WHERE product_url IS NOT NULL AND product_url != ""')
unique_after = cursor.fetchone()[0]

print(f"Deleted duplicates: {deleted_duplicates}")
print(f"Deleted invalid/missing URLs: {null_deleted}")
print(f"After cleanup: {total_after} rows, {unique_after} unique URLs")
print(f"Duplicates remaining: {total_after - unique_after}")
conn.close()
