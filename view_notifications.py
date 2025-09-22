import sqlite3

def view_all_notifications():
    print("--- Notifications in Database ---")
    try:
        conn = sqlite3.connect('tractors.db')
        c = conn.cursor()

        # Joins with users table to show who the notification is for
        query = """
            SELECT n.id, n.user_id, u.username, n.message, n.is_read
            FROM notifications n
            JOIN users u ON n.user_id = u.id
        """
        notifications = c.execute(query).fetchall()

        if not notifications:
            print("The 'notifications' table is empty.")
        else:
            for notification in notifications:
                status = "Read" if notification[4] == 1 else "UNREAD"
                print("ID: {}, For User: {} ({}), Message: '{}', Status: {}".format(
                    notification[0], notification[2], notification[1], notification[3], status
                ))

        conn.close()
    except sqlite3.Error as e:
        print("Database error: {}".format(e))
    print("-------------------------------")

if __name__ == "__main__":
    view_all_notifications()