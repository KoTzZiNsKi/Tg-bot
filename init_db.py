import sqlite3

conn = sqlite3.connect("questions.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    option1 TEXT NOT NULL,
    option2 TEXT NOT NULL,
    option3 TEXT NOT NULL,
    answer TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("✅ База данных создана и готова.")
