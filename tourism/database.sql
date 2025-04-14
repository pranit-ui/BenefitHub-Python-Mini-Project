CREATE DATABASE iitb_scheme;
USE iitb_scheme;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    aadhaar VARCHAR(12) NOT NULL UNIQUE,
    mobile VARCHAR(10) NOT NULL,
    email VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,  -- Changed from district
    pincode VARCHAR(6) NOT NULL,
    previous_travel BOOLEAN,
    preferred_states TEXT,
    travel_purpose VARCHAR(50),
    special_categories TEXT,
    transport_mode VARCHAR(50),
    upi_id VARCHAR(50),
    gov_benefits BOOLEAN,
    aadhaar_doc VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    document_type VARCHAR(50),
    file_path VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);