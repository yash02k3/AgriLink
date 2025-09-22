import sqlite3

def setup_reviews():
    conn = sqlite3.connect('tractors.db')
    c = conn.cursor()

    # Create the reviews table if it doesn't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tractor_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tractor_id) REFERENCES tractors (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Reviews table is set up successfully.")

if __name__ == "__main__":
    setup_reviews()