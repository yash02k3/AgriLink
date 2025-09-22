import sqlite3

def setup_bookings():
    conn = sqlite3.connect('tractors.db')
    c = conn.cursor()

    # Create the bookings table if it doesn't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tractor_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        booking_status TEXT NOT NULL DEFAULT 'Confirmed', -- e.g., Confirmed, Pending, Cancelled
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tractor_id) REFERENCES tractors (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Bookings table is set up successfully.")

if __name__ == "__main__":
    setup_bookings()