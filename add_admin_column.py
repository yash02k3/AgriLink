import sqlite3

def add_admin_flag():
    conn = sqlite3.connect('tractors.db')
    c = conn.cursor()
    try:
        # Add an is_admin column. 0 = False, 1 = True. Default to 0.
        c.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0")
        print("Successfully added 'is_admin' column to 'users' table.")
    except sqlite3.OperationalError as e:
        print("Could not add column. It might already exist. Error: {}".format(e))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_admin_flag()