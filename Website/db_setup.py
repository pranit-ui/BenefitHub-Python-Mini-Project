import sqlite3
import os

def create_database():
    # Remove existing database if it exists
    if os.path.exists('documents.db'):
        os.remove('documents.db')
    
    conn = sqlite3.connect('documents.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY,
                  name TEXT,
                  email TEXT,
                  category TEXT)''')
    
    # Create documents table
    c.execute('''CREATE TABLE IF NOT EXISTS documents
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  doc_type TEXT,
                  file_path TEXT,
                  status TEXT DEFAULT 'pending',
                  feedback TEXT,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()