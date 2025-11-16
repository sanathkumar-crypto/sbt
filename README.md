# SBT Eligibility Checker

A Python web application that evaluates patient data to determine eligibility for Spontaneous Breathing Trial (SBT).

## Setup

The virtual environment has already been created and dependencies installed. If you need to set it up again:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Application

### Option 1: Using the run script
```bash
./run.sh
```

### Option 2: Manual activation
```bash
source venv/bin/activate
python app.py
```

The application will start on `http://localhost:5050`

## Usage

1. Open your browser and navigate to `http://localhost:5050`
2. Paste the patient JSON data into the form
3. Click "Check Eligibility"
4. View the results - if eligible, the task JSON will be displayed

## Eligibility Criteria

The patient must meet ALL of the following conditions:

1. Latest vital record has:
   - `daysFiO2 < 60`
   - `daysVentPEEP < 10`

2. No active medication order with `name = 'noradrenaline'`

3. No vital record since 12am of the check date has:
   - `daysVentBreathSequence = "csv"` AND
   - `daysHR < 120`

If all conditions are met, a task JSON will be generated with patient information and a message recommending SBT.
