#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('master_products.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM products')
total = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM products WHERE platform != "Daraz"')
non_daraz = cursor.fetchone()[0]

cursor.execute('SELECT platform, COUNT(*) FROM products GROUP BY platform ORDER BY COUNT(*) DESC')
platforms = cursor.fetchall()

print(f'🎯 100K TARGET PROGRESS:')
print(f'Total products: {total:,} / 100,000 ({(total/100000)*100:.1f}%)')
print(f'Non-Daraz products: {non_daraz:,} ({(non_daraz/total)*100:.1f}% of total)')
print(f'Remaining needed: {100000-total:,}')
print(f'\n🏪 PLATFORM BREAKDOWN:')
for p in platforms:
    print(f'   {p[0]}: {p[1]:,} products ({(p[1]/total)*100:.1f}%)')

conn.close()