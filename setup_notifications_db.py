import sqlite3

def setup_notifications():
    conn = sqlite3.connect('tractors.db')
    c = conn.cursor()

    # Create the notifications table
    c.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, -- The user who will RECEIVE the notification
        message TEXT NOT NULL,
        link TEXT, -- A URL to go to when the notification is clicked
        is_read INTEGER NOT NULL DEFAULT 0, -- 0 for unread, 1 for read
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Notifications table is set up successfully.")

if __name__ == "__main__":
    setup_notifications()