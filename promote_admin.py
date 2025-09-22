import sqlite3

def promote_user_to_admin():
    username = input("Enter the username to promote to admin: ")

    conn = sqlite3.connect('tractors.db')
    c = conn.cursor()

    # Find the user first
    user = c.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    if user:
        # Update the user's is_admin flag to 1 (True)
        c.execute('UPDATE users SET is_admin = 1 WHERE username = ?', (username,))
        conn.commit()
        print("Success! User '{}' has been promoted to an admin.".format(username))
    else:
        print("Error: User '{}' not found.".format(username))

    conn.close()

if __name__ == "__main__":
    promote_user_to_admin()
    