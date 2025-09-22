import sqlite3

def add_phone_column():
    conn = sqlite3.connect('tractors.db')
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE tractors ADD COLUMN phone TEXT")
        print("Successfully added 'phone' column to the 'tractors' table.")
    except sqlite3.OperationalError as e:
        print("Could not add column. It might already exist. Error: {}".format(e))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_phone_column()