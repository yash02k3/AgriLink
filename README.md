🚜 Tractor Portal - Web Application
A full-featured web application built with Python and Flask that allows users to register, rent, and manage tractors. It includes a complete user authentication system, an admin panel, a dynamic crop guide, and a real-time chat feature for users and owners.

✨ Features
User Authentication: Secure user registration and login system with password hashing.

Tractor Listings: Users can register their tractors with details, images, and rental prices.

CRUD Operations: Logged-in users can Create, Read, Update, and Delete their own tractor listings.

Search & Filter: A simple search to filter tractors by location or model.

Admin Panel: A secure dashboard where an admin can view all users and delete any tractor listing on the site.

Dynamic Crop Guide: An informative guide on crops and their required equipment, which can be fully managed by an admin.

Booking & Cancellation System: Users can book tractors for specific dates and cancel their bookings up to 48 hours in advance.

Real-time Chat: A live chat system for users to communicate with tractor owners, complete with image and file sharing and a "delete for everyone" feature.

In-App Notifications: A real-time notification system alerts owners to new bookings and chat messages.

🛠️ Tech Stack
Backend: Python, Flask, Flask-SocketIO

Database: SQLite

Frontend: HTML, CSS, Bootstrap 5, JavaScript

Real-time Engine: Eventlet

🚀 Setup and Installation
To run this project locally, follow these steps:

1. Clone the Repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

2. Create a requirements.txt file
Before others can use your project, they need to know what packages to install. Create a file named requirements.txt and add the following lines to it:

Flask
Flask-SocketIO
eventlet
werkzeug

3. Create and Activate a Virtual Environment
# Create the environment
python3 -m venv venv
# Activate it (on macOS/Linux)
source venv/bin/activate


4. Install Dependencies
Install all the required packages from your new requirements.txt file.
pip install -r requirements.txt

5. Set Up the Database
Run the setup scripts in order to create and configure your tractors.db file.

python3 setup_db.py
python3 setup_users_db.py
python3 setup_crops_db.py
python3 setup_reviews_db.py
python3 setup_bookings_db.py
python3 setup_chat_db.py
python3 add_admin_column.py
python3 add_phone_column.py
python3 add_image_column.py

6. Create an Admin User
First, run the application, register a user for yourself, then stop the application. Then, run the promotion script.

# First, run the app to register a user
python3 app.py

# Then, run this script and enter the username you just created
python3 promote_admin.py

7. Run the Application

source venv/bin/activate && python3 app.py 

Open your web browser and go to http://127.0.0.1:5000.

## 📸 Screenshots

**Homepage:**
![Homepage](screenshots/homepage.png)

**Tractor Listings:**
![Listings](screenshots/listings.png)

**Crop Interface:**
![Chat](screenshots/crop.png)
