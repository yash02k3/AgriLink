import sqlite3

def setup_users():
    conn = sqlite3.connect('tractors.db')
    c = conn.cursor()

    # Create the users table if it doesn't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    # Add a user_id column to the tractors table if it doesn't exist
    try:
        c.execute("ALTER TABLE tractors ADD COLUMN user_id INTEGER")
        print("Successfully added 'user_id' column to 'tractors' table.")
    except sqlite3.OperationalError as e:
        print("Could not add user_id column. It might already exist. Error: {}".format(e))

    conn.commit()
    conn.close()
    print("Users table is set up.")

if __name__ == "__main__":
    setup_users()