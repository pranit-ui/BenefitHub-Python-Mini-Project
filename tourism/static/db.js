const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('iitb_scheme.db');

// Create tables
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        dob TEXT NOT NULL,
        gender TEXT NOT NULL,
        aadhaar TEXT UNIQUE NOT NULL,
        mobile TEXT NOT NULL,
        email TEXT NOT NULL,
        state TEXT NOT NULL,
        city TEXT NOT NULL,
        pincode TEXT NOT NULL,
        previous_travel INTEGER,
        preferred_states TEXT,
        travel_purpose TEXT,
        special_categories TEXT,
        transport_mode TEXT,
        upi_id TEXT,
        gov_benefits INTEGER,
        aadhaar_doc TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        document_type TEXT,
        file_path TEXT,
        uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )`);
});

module.exports = db;