const express = require('express');
const multer = require('multer');
const path = require('path');
const db = require('./db');

const app = express();
const port = 3000;

// Middleware
app.use(express.static('.'));
app.use(express.json());

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: 'uploads/',
    filename: (req, file, cb) => {
        cb(null, Date.now() + path.extname(file.originalname));
    }
});
const upload = multer({ storage: storage });

// Handle form submission
app.post('/submit', upload.single('aadhaarDoc'), (req, res) => {
    const data = req.body;
    
    const stmt = db.prepare(`INSERT INTO users (
        full_name, dob, gender, aadhaar, mobile, email,
        state, city, pincode, previous_travel,
        preferred_states, travel_purpose, special_categories,
        transport_mode, upi_id, gov_benefits, aadhaar_doc
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`);

    try {
        stmt.run([
            data.fullName,
            data.dob,
            data.gender,
            data.aadhaar,
            data.mobile,
            data.email,
            data.state,
            data.city,
            data.pincode,
            data.previousTravel === 'yes' ? 1 : 0,
            data.preferredStates.join(', '),
            data.travelPurpose,
            data.categories ? data.categories.join(', ') : '',
            data.transport,
            data.upiId,
            data.govBenefits === 'yes' ? 1 : 0,
            req.file ? req.file.filename : null
        ]);

        res.json({ success: true });
    } catch (error) {
        res.json({ success: false, message: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});