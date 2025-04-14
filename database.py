import sqlite3
from sqlite3 import Error

def create_connection():
    """Create a database connection"""
    try:
        conn = sqlite3.connect('benefithub.db')
        conn.row_factory = sqlite3.Row
        print("Successfully connected to SQLite database")
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_tables(conn):
    """Create necessary tables"""
    try:
        cursor = conn.cursor()
        
        # Create Categories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            icon TEXT NOT NULL,
            scheme_count INTEGER NOT NULL
        )
        ''')

        # Create Schemes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            apply_link TEXT,
            eligibility TEXT,
            benefits TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')

        conn.commit()
        return True
    except Error as e:
        print(f"Error creating tables: {e}")
        return False

def insert_categories(conn, categories):
    """Insert categories into database"""
    try:
        cursor = conn.cursor()
        cursor.executemany('''
        INSERT OR REPLACE INTO categories (name, title, icon, scheme_count)
        VALUES (?, ?, ?, ?)
        ''', categories)
        conn.commit()
        return True
    except Error as e:
        print(f"Error inserting categories: {e}")
        return False

def insert_schemes(conn, schemes):
    """Insert schemes into database"""
    try:
        cursor = conn.cursor()
        cursor.executemany('''
        INSERT INTO schemes (category_id, title, description, apply_link, eligibility, benefits)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', schemes)
        conn.commit()
        return True
    except Error as e:
        print(f"Error inserting schemes: {e}")
        return False