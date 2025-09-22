import sqlite3

def setup_database():
    conn = sqlite3.connect('tractors.db')
    c = conn.cursor()

    # Drop tables if they already exist to start fresh
    c.execute("DROP TABLE IF EXISTS tractors")
    c.execute("DROP TABLE IF EXISTS services")

    # Create tractors table (without the phone column initially)
    c.execute('''
    CREATE TABLE tractors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        model TEXT NOT NULL,
        rent INTEGER NOT NULL,
        location TEXT
    )
    ''')

    # Create services table
    c.execute('''
    CREATE TABLE services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner TEXT NOT NULL,
        model TEXT NOT NULL,
        date TEXT NOT NULL,
        service_type TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()
    print("Database 'tractors.db' created successfully with initial tables.")

if __name__ == "__main__":
    setup_database()