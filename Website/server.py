from flask import Flask, request, jsonify, send_from_directory
from flask_mail import Mail, Message
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Email configuration
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USERNAME = 'officialbenefithub@gmail.com',  # Replace with your email
    MAIL_PASSWORD = 'askuhignagobodsi'      # Replace with your app password
)
mail = Mail(app)

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def home():
    return send_from_directory('.', 'website.html')

@app.route('/user-dashboard.html')  # Changed to match the href in website.html
def user_dashboard():
    return send_from_directory('.', 'user-dashboard.html')

@app.route('/admin-dashboard.html')  # Changed to match the link
def admin_dashboard():
    return send_from_directory('.', 'admin-dashboard.html')

# Add new route for handling application status updates
@app.route('/update_application_status', methods=['POST'])
def update_application_status():
    try:
        data = request.json
        user_id = data['id']
        status = data['status']
        reason = data.get('reason', '')

        conn = sqlite3.connect('documents.db')
        c = conn.cursor()
        
        # Update status
        c.execute('UPDATE documents SET status = ?, feedback = ? WHERE user_id = ?',
                 (status, reason, user_id))
        
        # Get user email, name and category
        c.execute('SELECT email, name, category FROM users WHERE id = ?', (user_id,))
        email, name, category = c.fetchone()
        
        conn.commit()
        conn.close()

        # Send email notification
        subject = f'BenefitHub: Your Application Status Update'
        body = f'''Dear {name},

We are writing to inform you that your application for benefits has been {status}.

Application Details:
- Application ID: {user_id}
- Category: {category}
'''

        if status == 'approved':
            body += '''
Congratulations! You are now eligible for the benefits. Our team will contact you shortly with further instructions on how to proceed.
'''
        elif status == 'rejected':
            body += f'''
We regret to inform you that your application could not be approved at this time.

Reason for rejection: {reason}

If you believe this decision was made in error or if you have additional documentation to support your application, please feel free to reapply with the updated information.
'''

        body += '''

Thank you for using BenefitHub.

Best regards,
The BenefitHub Team
'''

        msg = Message(
            subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
            body=body
        )
        mail.send(msg)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Email error: {str(e)}")  # Add detailed error logging
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/submit_documents', methods=['POST'])
def submit_documents():
    try:
        name = request.form['name']
        email = request.form['email']
        category = request.form['category']
        
        conn = sqlite3.connect('documents.db')
        c = conn.cursor()
        
        # Insert user
        c.execute('INSERT INTO users (name, email, category) VALUES (?, ?, ?)',
                 (name, email, category))
        user_id = c.lastrowid
        
        # Handle file uploads
        files = request.files
        for doc_type in ['aadhaar', 'income', 'work']:
            if doc_type in files:
                file = files[doc_type]
                if file.filename:
                    filename = secure_filename(f"{user_id}_{doc_type}_{file.filename}")
                    filepath = os.path.join('uploads', filename)  # Store relative path
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    
                    c.execute('''INSERT INTO documents 
                                (user_id, doc_type, file_path) 
                                VALUES (?, ?, ?)''',
                             (user_id, doc_type, filepath))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Documents uploaded successfully'})
    except Exception as e:
        print('Error:', str(e))  # Debug print
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get_applications', methods=['GET'])
def get_applications():
    try:
        conn = sqlite3.connect('documents.db')
        c = conn.cursor()
        
        # Only get pending applications
        c.execute('''
            SELECT DISTINCT u.id, u.name, u.email, u.category
            FROM users u
            JOIN documents d ON u.id = d.user_id
            WHERE d.status IS NULL OR d.status = 'pending'
        ''')
        
        applications = {}
        for row in c.fetchall():
            user_id, name, email, category = row
            
            c.execute('''
                SELECT doc_type, file_path, status
                FROM documents
                WHERE user_id = ?
            ''', (user_id,))
            
            documents = {}
            for doc in c.fetchall():
                doc_type, file_path, status = doc
                filename = os.path.basename(file_path)
                documents[doc_type] = f'/uploads/{filename}'
            
            applications[user_id] = {
                'id': user_id,
                'name': name,
                'email': email,
                'category': category,
                'documents': documents,
                'status': 'pending'
            }
        
        conn.close()
        return jsonify(list(applications.values()))
    except Exception as e:
        print('Error in get_applications:', str(e))
        return jsonify({'error': str(e)}), 500

# Add this route after your existing routes
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Add this route to serve PDF files
@app.route('/pdfs/<path:filename>')
def serve_pdf(filename):
    try:
        return send_from_directory('pdfs', filename, as_attachment=True)
    except Exception as e:
        print(f"Error serving PDF: {str(e)}")
        return f"Error: {str(e)}", 404

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, port=3000)