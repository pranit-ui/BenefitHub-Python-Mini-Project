from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from sqlite3 import Error

class Database:
    @staticmethod
    def get_connection():
        try:
            connection = sqlite3.connect('benefithub.db')
            connection.row_factory = sqlite3.Row
            return connection
        except Error as e:
            print(f"Error connecting to SQLite: {e}")
            return None

class User(UserMixin):
    def __init__(self, id, username, email=None):
        self.id = id
        self.username = username
        self.email = email

    @staticmethod
    def get(user_id):
        conn = Database.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                if user:
                    return User(user['id'], user['username'], user['email'])
            except Error as e:
                print(f"Error: {e}")
            finally:
                cursor.close()
                conn.close()
        return None

    @staticmethod
    def create(username, password, email):
        conn = Database.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
                    (username, generate_password_hash(password), email)
                )
                conn.commit()
                user_id = cursor.lastrowid
                return User(user_id, username, email)
            except Error as e:
                print(f"Error: {e}")
                return None
            finally:
                cursor.close()
                conn.close()
        return None

    @staticmethod
    def authenticate(username, password):
        conn = Database.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT id, username, password_hash, email FROM users WHERE username = ?', (username,))
                user = cursor.fetchone()
                if user and check_password_hash(user['password_hash'], password):
                    return User(user['id'], user['username'], user['email'])
            except Error as e:
                print(f"Error: {e}")
            finally:
                cursor.close()
                conn.close()
        return None

    # Add these methods to the User class

    @staticmethod
    def get_by_email(email):
        conn = Database.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT id, username, email FROM users WHERE email = %s', (email,))
                user = cursor.fetchone()
                if user:
                    return User(user[0], user[1], user[2])
            except Error as e:
                print(f"Error: {e}")
            finally:
                cursor.close()
                conn.close()
        return None

    @staticmethod
    def create_google_user(username, email, google_id):
        conn = Database.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (username, email, google_id) VALUES (%s, %s, %s)',
                    (username, email, google_id)
                )
                conn.commit()
                user_id = cursor.lastrowid
                return User(user_id, username, email)
            except Error as e:
                print(f"Error: {e}")
                return None
            finally:
                cursor.close()
                conn.close()
        return None