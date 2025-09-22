import sqlite3

def view_all_users():
    print("--- Registered Users ---")
    try:
        conn = sqlite3.connect('tractors.db')
        c = conn.cursor()

        users = c.execute('SELECT id, username, is_admin FROM users').fetchall()

        if not users:
            print("No users found in the database.")
            print("Please register an account on the website first.")
        else:
            for user in users:
                admin_status = "(Admin)" if user[2] == 1 else ""
                # Using .format() for older Python compatibility if needed
                print("ID: {}, Username: {} {}".format(user[0], user[1], admin_status))

        conn.close()
    except sqlite3.Error as e:
        print("Database error: {}".format(e))
    print("------------------------")

if __name__ == "__main__":
    view_all_users()