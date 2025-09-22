import sqlite3

def setup_chat():
    conn = sqlite3.connect('tractors.db')
    c = conn.cursor()

    # Recreate the table with the new message_type column
    c.execute("DROP TABLE IF EXISTS messages")
    c.execute('''
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        recipient_id INTEGER NOT NULL,
        message_type TEXT NOT NULL DEFAULT 'text', -- Can be 'text', 'image', or 'file'
        message_text TEXT NOT NULL,
        is_deleted INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users (id),
        FOREIGN KEY (recipient_id) REFERENCES users (id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Messages table has been recreated with message_type functionality.")

if __name__ == "__main__":
    setup_chat()