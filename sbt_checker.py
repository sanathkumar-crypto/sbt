"""
SBT (Spontaneous Breathing Trial) Eligibility Checker

This module contains the logic to determine if a patient is eligible
for a Spontaneous Breathing Trial based on clinical criteria.
"""

from datetime import datetime, date, time
from typing import Optional, Dict, Any, List


def check_sbt_eligibility(patient_json: Dict[str, Any], check_date: Optional[date] = None) -> Optional[Dict[str, Any]]:
    """
    Check if a patient is eligible for SBT based on clinical criteria.
    
    Conditions:
    1. Latest vital has daysFiO2 < 60 AND daysVentPEEP < 10
    2. No active medication order with name = 'noradrenaline'
    3. No vital since 12am of check_date has daysVentBreathSequence = "csv" AND daysHR < 120
    
    Args:
        patient_json: Patient data as a dictionary
        check_date: Date to check (defaults to today)
    
    Returns:
        Task dictionary if eligible, None otherwise
    """
    if check_date is None:
        check_date = date.today()
    
    # Get vitals list
    vitals = patient_json.get('vitals', [])
    if not vitals:
        return None
    
    # Find latest vital by timestamp
    latest_vital = None
    latest_timestamp = None
    
    for vital in vitals:
        timestamp_str = vital.get('timestamp')
        if timestamp_str:
            try:
                # Parse timestamp (format: "2025-07-15T19:38:00")
                vital_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00') if 'Z' in timestamp_str else timestamp_str)
                if latest_timestamp is None or vital_timestamp > latest_timestamp:
                    latest_timestamp = vital_timestamp
                    latest_vital = vital
            except (ValueError, AttributeError):
                continue
    
    if latest_vital is None:
        return None
    
    # Condition 1: Check latest vital - daysFiO2 < 60 AND daysVentPEEP < 10
    days_fio2 = latest_vital.get('daysFiO2')
    days_vent_peep = latest_vital.get('daysVentPEEP')
    
    # Convert to numeric if they're strings
    try:
        days_fio2_num = float(days_fio2) if days_fio2 is not None else None
    except (ValueError, TypeError):
        days_fio2_num = None
    
    try:
        days_vent_peep_num = float(days_vent_peep) if days_vent_peep is not None else None
    except (ValueError, TypeError):
        days_vent_peep_num = None
    
    if days_fio2_num is None or days_fio2_num >= 60:
        return None
    
    if days_vent_peep_num is None or days_vent_peep_num >= 10:
        return None
    
    # Condition 2: Check no active medication order with name = 'noradrenaline'
    orders = patient_json.get('orders', {})
    active_medications = orders.get('active', {}).get('medications', [])
    
    has_noradrenaline = False
    for medication in active_medications:
        med_name = medication.get('name', '').lower() if medication.get('name') else ''
        if 'noradrenaline' in med_name:
            has_noradrenaline = True
            break
    
    if has_noradrenaline:
        return None
    
    # Condition 3: Check no vital since 12am of check_date has daysVentBreathSequence = "csv" AND daysHR < 120
    check_datetime_start = datetime.combine(check_date, time.min)  # 12:00 AM of check_date
    
    for vital in vitals:
        timestamp_str = vital.get('timestamp')
        if not timestamp_str:
            continue
        
        try:
            vital_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00') if 'Z' in timestamp_str else timestamp_str)
            
            # Only check vitals from 12am of check_date onwards
            if vital_timestamp < check_datetime_start:
                continue
            
            days_vent_breath_sequence = vital.get('daysVentBreathSequence')
            days_hr = vital.get('daysHR')
            
            # Check if daysVentBreathSequence = "csv"
            if days_vent_breath_sequence == "csv":
                # Check if daysHR < 120
                try:
                    days_hr_num = float(days_hr) if days_hr is not None else None
                    if days_hr_num is not None and days_hr_num < 120:
                        # Found a vital that violates condition 3
                        return None
                except (ValueError, TypeError):
                    pass
        except (ValueError, AttributeError):
            continue
    
    # All conditions met - generate task JSON
    patient_name = patient_json.get('name', '')
    patient_lastname = patient_json.get('lastName', '')
    full_name = f"{patient_name} {patient_lastname}".strip() if patient_name or patient_lastname else ''
    
    task = {
        'createdBy': 'SBT agent',
        'CPMRN': patient_json.get('CPMRN', ''),
        'patientName': full_name,
        'hospital': patient_json.get('hospitalName', ''),
        'unit': patient_json.get('unitName', ''),
        'BedNumber': patient_json.get('bedNo', ''),
        'createdAt': datetime.now().isoformat(),
        'Urgency': 'Low',
        'Message': 'Please order a SBT for this patient as patient is not on noradrenaline, and fio2 is less than 0.6 with a peep less than 10'
    }
    
    return task

