from flask import Flask, render_template, request, jsonify, send_from_directory
import json
from datetime import datetime
import os

app = Flask(__name__)

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/register')
def register():
    return send_from_directory('.', 'register.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.form.to_dict()
        
        # Handle multiple select values
        preferred_states = request.form.getlist('preferredStates[]')
        categories = request.form.getlist('categories[]')
        
        data['preferredStates'] = preferred_states
        data['categories'] = categories
        
        # Handle file upload
        if 'aadhaarDoc' in request.files:
            file = request.files['aadhaarDoc']
            if file:
                filename = f"{datetime.now().timestamp()}_{file.filename}"
                file.save(os.path.join('uploads', filename))
                data['aadhaarDoc'] = filename

        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        data['id'] = int(datetime.now().timestamp() * 1000)

        # Load existing registrations
        try:
            with open('registrations.json', 'r') as f:
                registrations = json.load(f)
        except FileNotFoundError:
            registrations = []

        # Add new registration
        registrations.append(data)

        # Save updated registrations
        with open('registrations.json', 'w') as f:
            json.dump(registrations, f, indent=2)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    # Create empty registrations.json if it doesn't exist
    if not os.path.exists('registrations.json'):
        with open('registrations.json', 'w') as f:
            json.dump([], f)
    
    app.run(debug=True, port=2000)