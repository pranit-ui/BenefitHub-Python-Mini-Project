from flask import Blueprint, jsonify
from datetime import datetime

admin = Blueprint('admin', __name__)

@admin.route('/get_applications', methods=['GET'])
def get_applications():
    # Sample data for demonstration
    applications = [
        {
            'id': '12345',
            'name': 'John Doe',
            'category': 'Construction Worker',
            'documents': {
                'aadhaar': '/uploads/sample_aadhaar.jpg',
                'income': '/uploads/sample_income.jpg',
                'work': '/uploads/sample_work.jpg'
            },
            'status': 'pending',
            'date': datetime.now().strftime('%Y-%m-%d')
        }
    ]
    return jsonify(applications)

@admin.route('/approve_application', methods=['POST'])
def approve_application():
    # Add approval logic here
    return jsonify({'success': True})