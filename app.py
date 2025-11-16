"""
Flask web application for SBT eligibility checking.
"""

from flask import Flask, render_template, request, jsonify
import json
from sbt_checker import check_sbt_eligibility

app = Flask(__name__)


@app.route('/')
def index():
    """Serve the main form page."""
    return render_template('index.html')


@app.route('/check', methods=['POST'])
def check():
    """Process patient data and return SBT eligibility result."""
    try:
        # Get JSON data from request
        form_data = request.get_json()
        
        if not form_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Construct patient JSON from form data
        patient_json = {
            'CPMRN': form_data.get('CPMRN', ''),
            'name': form_data.get('name', ''),
            'lastName': form_data.get('lastName', ''),
            'hospitalName': form_data.get('hospitalName', ''),
            'unitName': form_data.get('unitName', ''),
            'bedNo': form_data.get('bedNo', ''),
            'orders': {
                'active': {
                    'medications': []
                }
            },
            'vitals': []
        }
        
        # Add active medications
        medications = form_data.get('medications', [])
        for med_name in medications:
            if med_name and med_name.strip():
                patient_json['orders']['active']['medications'].append({
                    'name': med_name.strip()
                })
        
        # Add latest vital
        latest_vital = form_data.get('latestVital', {})
        if latest_vital:
            vital_entry = {
                'timestamp': latest_vital.get('timestamp'),
                'daysFiO2': latest_vital.get('daysFiO2'),
                'daysVentPEEP': latest_vital.get('daysVentPEEP')
            }
            patient_json['vitals'].append(vital_entry)
        
        # Add other vitals since 12am
        vitals = form_data.get('vitals', [])
        for vital in vitals:
            vital_entry = {
                'timestamp': vital.get('timestamp')
            }
            if 'daysVentBreathSequence' in vital:
                vital_entry['daysVentBreathSequence'] = vital.get('daysVentBreathSequence')
            if 'daysHR' in vital:
                vital_entry['daysHR'] = vital.get('daysHR')
            patient_json['vitals'].append(vital_entry)
        
        # Check SBT eligibility
        result = check_sbt_eligibility(patient_json)
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({'message': 'Patient does not meet SBT eligibility criteria'}), 200
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)

