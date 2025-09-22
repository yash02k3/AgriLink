from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_change_me'
socketio = SocketIO(app)

DATABASE = 'tractors.db'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# A dictionary to keep track of online users
user_sids = {}

# --- IMPROVED DATABASE CONNECTION HANDLING ---
def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    """Closes the database again at the end of the request."""
    db = g.pop('db', None)
    if db is not None:  # <-- This is the corrected line
        db.close()

# Helper function to check for admin status
def is_admin():
    return session.get('is_admin', False)

# --- CONTEXT PROCESSOR ---
@app.context_processor
def inject_notifications():
    if 'user_id' in session:
        conn = get_db()
        count = conn.execute(
            'SELECT COUNT(id) FROM notifications WHERE user_id = ? AND is_read = 0', 
            (session['user_id'],)
        ).fetchone()[0]
        return dict(notification_count=count)
    return dict(notification_count=0)

# --- ALL YOUR FLASK ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user:
            flash('Username already exists.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register_user.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = (user['is_admin'] == 1)
            flash('You were successfully logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' not in session:
        flash('You must be logged in to register a tractor.', 'warning')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        model = request.form['model']
        rent = request.form['rent']
        location = request.form['location']
        phone = request.form['phone']
        user_id = session['user_id']
        image_file = request.files['image']
        filename = None
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn = get_db()
        conn.execute('INSERT INTO tractors (name, model, rent, location, phone, image_filename, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (name, model, rent, location, phone, filename, user_id))
        conn.commit()
        return render_template('success.html', message='Tractor Registered Successfully!')
    return render_template('register.html')

@app.route('/tractors')
def view_tractors():
    search_query = request.args.get('search', '')
    conn = get_db()
    query = """
        SELECT t.*, COALESCE(ROUND(AVG(r.rating), 1), 0) as avg_rating, COUNT(r.id) as review_count
        FROM tractors t LEFT JOIN reviews r ON t.id = r.tractor_id
    """
    params = []
    if search_query:
        query += " WHERE t.location LIKE ? OR t.model LIKE ?"
        params.extend(['%' + search_query + '%', '%' + search_query + '%'])
    query += " GROUP BY t.id"
    tractors = conn.execute(query, params).fetchall()
    return render_template('view_tractors.html', tractors=tractors, search_query=search_query)
    
@app.route('/tractor/<int:id>')
def tractor_detail(id):
    conn = get_db()
    tractor = conn.execute('SELECT * FROM tractors WHERE id = ?', (id,)).fetchone()
    reviews_query = "SELECT r.rating, r.comment, u.username FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.tractor_id = ? ORDER BY r.created_at DESC"
    reviews = conn.execute(reviews_query, (id,)).fetchall()
    today = datetime.today().strftime('%Y-%m-%d')
    bookings = conn.execute('SELECT start_date, end_date FROM bookings WHERE tractor_id = ? AND end_date >= ? ORDER BY start_date', (id, today)).fetchall()
    return render_template('tractor_detail.html', tractor=tractor, reviews=reviews, bookings=bookings)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_tractor(id):
    if 'user_id' not in session:
        flash('You must be logged in to edit.', 'warning')
        return redirect(url_for('login'))
    conn = get_db()
    tractor = conn.execute('SELECT * FROM tractors WHERE id = ?', (id,)).fetchone()
    if not tractor or tractor['user_id'] != session['user_id']:
        flash('You are not authorized to edit this tractor.', 'danger')
        return redirect(url_for('view_tractors'))
    if request.method == 'POST':
        name = request.form['name']
        model = request.form['model']
        rent = request.form['rent']
        location = request.form['location']
        phone = request.form['phone']
        conn.execute('UPDATE tractors SET name = ?, model = ?, rent = ?, location = ?, phone = ? WHERE id = ?',
                     (name, model, rent, location, phone, id))
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            if tractor['image_filename']:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], tractor['image_filename'])
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            conn.execute('UPDATE tractors SET image_filename = ? WHERE id = ?', (filename, id))
        conn.commit()
        return redirect(url_for('view_tractors'))
    return render_template('edit_tractor.html', tractor=tractor)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_tractor(id):
    if 'user_id' not in session:
        flash('You must be logged in to delete.', 'warning')
        return redirect(url_for('login'))
    conn = get_db()
    tractor = conn.execute('SELECT * FROM tractors WHERE id = ?', (id,)).fetchone()
    if tractor and (tractor['user_id'] == session['user_id'] or session.get('is_admin')):
        conn.execute('DELETE FROM tractors WHERE id = ?', (id,))
        conn.commit()
        flash('Tractor deleted successfully.', 'success')
    else:
        flash('You are not authorized to delete this tractor.', 'danger')
    if session.get('is_admin') and request.referrer and 'admin' in request.referrer:
        return redirect(url_for('admin_panel'))
    return redirect(url_for('view_tractors'))

@app.route('/book/<int:id>', methods=['POST'])
def book_tractor(id):
    if 'user_id' not in session:
        flash('You must be logged in to book a tractor.', 'warning')
        return redirect(url_for('login'))
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    if not start_date_str or not end_date_str:
        flash('Start date and end date are required.', 'danger')
        return redirect(url_for('tractor_detail', id=id))
    booking_user_id = session['user_id']
    conn = get_db()
    conflict_query = "SELECT * FROM bookings WHERE tractor_id = ? AND NOT (end_date < ? OR start_date > ?)"
    conflicts = conn.execute(conflict_query, (id, start_date_str, end_date_str)).fetchall()
    if conflicts:
        flash('Error: This tractor is already booked.', 'danger')
    else:
        conn.execute('INSERT INTO bookings (tractor_id, user_id, start_date, end_date) VALUES (?, ?, ?, ?)',
                     (id, booking_user_id, start_date_str, end_date_str))
        tractor_info = conn.execute('SELECT user_id, model FROM tractors WHERE id = ?', (id,)).fetchone()
        owner_id = tractor_info['user_id']
        tractor_model = tractor_info['model']
        if owner_id != booking_user_id:
            booking_user = conn.execute('SELECT username FROM users WHERE id = ?', (booking_user_id,)).fetchone()
            message = "Your '{}' has a new booking from {}.".format(tractor_model, booking_user['username'])
            link = url_for('tractor_detail', id=id)
            conn.execute('INSERT INTO notifications (user_id, message, link) VALUES (?, ?, ?)',
                         (owner_id, message, link))
        conn.commit()
        flash('Tractor successfully booked!', 'success')
    return redirect(url_for('tractor_detail', id=id))
    
@app.route('/my_bookings')
def my_bookings():
    if 'user_id' not in session:
        flash('You must be logged in to view your bookings.', 'warning')
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db()
    query = "SELECT b.id, b.start_date, b.end_date, t.model, t.user_id as owner_id FROM bookings b JOIN tractors t ON b.tractor_id = t.id WHERE b.user_id = ? ORDER BY b.start_date DESC"
    all_bookings = conn.execute(query, (user_id,)).fetchall()
    upcoming_bookings = []
    past_bookings = []
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    for booking in all_bookings:
        booking_dict = dict(booking)
        start_datetime = datetime.strptime(booking['start_date'], '%Y-%m-%d')
        booking_dict['cancellable'] = (start_datetime - now).total_seconds() > 48 * 3600
        if booking['start_date'] >= today_str:
            upcoming_bookings.append(booking_dict)
        else:
            past_bookings.append(booking_dict)
    return render_template('my_bookings.html', upcoming=upcoming_bookings, past=past_bookings)

@app.route('/cancel_booking/<int:id>', methods=['POST'])
def cancel_booking(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db()
    booking = conn.execute('SELECT * FROM bookings WHERE id = ? AND user_id = ?', (id, user_id)).fetchone()
    if not booking:
        flash('Booking not found or not authorized.', 'danger')
        return redirect(url_for('my_bookings'))
    start_datetime = datetime.strptime(booking['start_date'], '%Y-%m-%d')
    if (start_datetime - datetime.now()).total_seconds() <= 48 * 3600:
        flash('Cannot cancel within 48 hours of start date.', 'danger')
    else:
        conn.execute('DELETE FROM bookings WHERE id = ?', (id,))
        conn.commit()
        flash('Booking successfully cancelled.', 'success')
    return redirect(url_for('my_bookings'))

@app.route('/crop_guide')
def crop_guide():
    conn = get_db()
    crops = conn.execute('SELECT * FROM crops').fetchall()
    return render_template('crop_guide.html', crops=crops)
    
@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        flash('You must be logged in.', 'warning')
        return redirect(url_for('login'))
    user_id = session['user_id']
    conn = get_db()
    user_notifications = conn.execute('SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
    conn.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    return render_template('notifications.html', notifications=user_notifications)

@app.route('/admin')
def admin_panel():
    if not is_admin():
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    conn = get_db()
    all_tractors = conn.execute('SELECT t.*, u.username FROM tractors t LEFT JOIN users u ON t.user_id = u.id').fetchall()
    all_users = conn.execute('SELECT * FROM users').fetchall()
    all_crops = conn.execute('SELECT * FROM crops').fetchall()
    return render_template('admin_panel.html', tractors=all_tractors, users=all_users, crops=all_crops)

@app.route('/add_crop', methods=['GET', 'POST'])
def add_crop():
    if not is_admin():
        return redirect(url_for('home'))
    if request.method == 'POST':
        # ... (add crop logic)
        flash('New crop added!', 'success')
        return redirect(url_for('admin_panel'))
    return render_template('add_crop.html')

@app.route('/edit_crop/<int:id>', methods=['GET', 'POST'])
def edit_crop(id):
    if not is_admin():
        return redirect(url_for('home'))
    # ... (edit crop logic)
    return render_template('edit_crop.html', crop=crop)

@app.route('/delete_crop/<int:id>', methods=['POST'])
def delete_crop(id):
    if not is_admin():
        return redirect(url_for('home'))
    # ... (delete crop logic)
    return redirect(url_for('admin_panel'))

@app.route('/chat_with/<int:recipient_id>')
def chat_with(recipient_id):
    if 'user_id' not in session:
        flash('You must be logged in to chat.', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db()
    recipient = conn.execute('SELECT id, username FROM users WHERE id = ?', (recipient_id,)).fetchone()
    
    # NEW: Get the phone number from the first tractor the user registered
    owner_phone = conn.execute(
        'SELECT phone FROM tractors WHERE user_id = ? LIMIT 1', 
        (recipient_id,)
    ).fetchone()
    
    if not recipient:
        flash('User not found.', 'danger')
        return redirect(url_for('home'))
        
    recipient_phone_number = owner_phone['phone'] if owner_phone else None
    
    return render_template('chat.html', recipient=recipient, recipient_phone_number=recipient_phone_number)

# In app.py, replace your existing Socket.IO handlers with these three

@socketio.on('join')
def on_join(data):
    if 'user_id' not in session: return
    user1 = str(session['user_id'])
    user2 = str(data['recipient_id'])
    room = "_".join(sorted([user1, user2]))
    join_room(room)

    conn = get_db()
    # MODIFIED: Select new message_type column
    history_query = "SELECT id, sender_id, message_type, message_text, is_deleted FROM messages WHERE (sender_id = ? AND recipient_id = ?) OR (sender_id = ? AND recipient_id = ?) ORDER BY created_at ASC"
    messages = conn.execute(history_query, (user1, user2, user2, user1)).fetchall()

    history = [dict(row) for row in messages]
    emit('chat_history', {'history': history})

@socketio.on('send_message')
def on_send_message(data):
    if 'user_id' not in session: return

    sender_id = session['user_id']
    sender_username = session['username']
    recipient_id = int(data['recipient_id'])
    message_text = data['message_text']
    message_type = data.get('message_type', 'text') # Default to 'text'

    room = "_".join(sorted([str(sender_id), str(recipient_id)]))

    conn = get_db()
    cursor = conn.cursor()
    # MODIFIED: Insert the new message_type
    cursor.execute('INSERT INTO messages (sender_id, recipient_id, message_text, message_type) VALUES (?, ?, ?, ?)',
                 (sender_id, recipient_id, message_text, message_type))
    message_id = cursor.lastrowid
    conn.commit()

    emit('receive_message', {
        'id': message_id,
        'sender_id': sender_id,
        'sender_username': sender_username,
        'message_type': message_type,
        'message_text': message_text,
        'is_deleted': 0
    }, room=room, skip_sid=request.sid)

# NEW: Handler for deleting a message
@socketio.on('delete_message')
def on_delete_message(data):
    if 'user_id' not in session: return

    user_id = session['user_id']
    message_id = data['message_id']

    conn = get_db()
    # Security Check: Get the message and make sure the current user is the sender
    message = conn.execute('SELECT id, sender_id FROM messages WHERE id = ?', (message_id,)).fetchone()

    if message and message['sender_id'] == user_id:
        # Mark the message as deleted
        conn.execute('UPDATE messages SET is_deleted = 1 WHERE id = ?', (message_id,))
        conn.commit()

        # Notify everyone in the room that this message was deleted
        recipient_id = conn.execute('SELECT recipient_id FROM messages WHERE id = ?', (message_id,)).fetchone()['recipient_id']
        room = "_".join(sorted([str(user_id), str(recipient_id)]))
        emit('message_deleted', {'message_id': message_id}, room=room)
  
# Add this new route to your app.py file
@app.route('/upload_chat_file', methods=['POST'])
def upload_chat_file():
    if 'user_id' not in session:
        return {'error': 'Authorization required'}, 401

    if 'file' not in request.files:
        return {'error': 'No file part'}, 400

    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    if file:
        filename = secure_filename(file.filename)
        # Create the chat_uploads folder if it doesn't exist
        chat_upload_folder = os.path.join('static', 'chat_uploads')
        os.makedirs(chat_upload_folder, exist_ok=True)

        file_path = os.path.join(chat_upload_folder, filename)
        file.save(file_path)

        # Return the public URL path to the file
        return {'filePath': url_for('static', filename=f'chat_uploads/{filename}')}

    return {'error': 'File upload failed'}, 500
        
if __name__ == '__main__':
    socketio.run(app, debug=True)