import os
import json
import time
import random
import threading
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, Response

app = Flask(__name__, static_folder='.')

DB_FILE = 'safety_data.db'

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            zone TEXT,
            event_type TEXT,
            severity TEXT,
            confidence REAL,
            individuals TEXT,
            action_taken TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_incident(incident):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO incidents (timestamp, zone, event_type, severity, confidence, individuals, action_taken, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        incident['timestamp'], incident['zone'], incident['event_type'], 
        incident['severity'], incident['confidence'], incident['individuals'], 
        incident['action_taken'], incident['status']
    ))
    conn.commit()
    conn.close()

# --- AI Simulator Background Task ---
ZONES = ["Warehouse A - Sector 4", "Loading Dock B - Bay 2", "Assembly Line 1 - Packaging", "Chemical Storage Facility C", "Pedestrian Walkway - Main Gate"]
EMPLOYEES = ["John Smith (ID: 1042)", "Sarah Jenkins (ID: 2931)", "Michael Chang (ID: 8841)", "Emily Rodriguez (ID: 4120)", "David Kim (ID: 7721)", "Unknown Contractor"]
EVENT_TYPES = ["Missing Hard Hat", "Missing Safety Glasses", "Forklift Proximity Violation", "Liquid Spill Detected", "Improper Lifting Posture", "Unauthorized Access"]
SEVERITIES = ["low", "medium", "high", "critical"]

def simulate_ai_camera_feed():
    while True:
        time.sleep(random.randint(15, 35)) # Trigger event every 15-35 seconds
        
        event_type = random.choice(EVENT_TYPES)
        zone = random.choice(ZONES)
        
        event = {
            "timestamp": datetime.now().isoformat() + "Z",
            "zone": zone,
            "event_type": event_type,
            "severity": random.choice(SEVERITIES),
            "confidence": round(random.uniform(0.75, 0.99), 2),
            "individuals": random.choice(EMPLOYEES),
            "action_taken": "Logged via AI Vision System.",
            "status": "Open"
        }
        
        # Realistic actions based on event
        if event_type == "Forklift Proximity Violation":
            event["severity"] = "critical"
            event["action_taken"] = "PA System Warning Triggered: 'Pedestrian in forklift path.' Supervisor alerted."
        elif event_type == "Liquid Spill Detected":
            event["severity"] = "high"
            event["action_taken"] = "Maintenance dispatch ticket #4921 automatically created."
        elif event_type == "Improper Lifting Posture":
            event["severity"] = "medium"
            event["action_taken"] = "Ergonomics warning logged. Scheduled for weekly training review."
        elif event_type == "Missing Hard Hat":
            event["severity"] = "high"
            event["action_taken"] = "SMS alert sent to Floor Manager."
            
        insert_incident(event)
        print(f"[AI ENGINE] New event detected: {event['event_type']} in {event['zone']} (Confidence: {event['confidence']})")

# --- Routes ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory('.', 'dashboard.html')

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM incidents ORDER BY id DESC LIMIT 50')
    rows = c.fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in rows])

@app.route('/api/incidents/<int:incident_id>/resolve', methods=['POST'])
def resolve_incident(incident_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE incidents SET status = 'Closed' WHERE id = ?", (incident_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/export/csv')
def export_csv():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM incidents ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    
    csv_data = "ID,Timestamp,Zone,Event_Type,Severity,Confidence,Individuals,Status\n"
    for r in rows:
        csv_data += f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]},{r[6]},{r[8]}\n"
        
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=safety_report.csv"}
    )

if __name__ == '__main__':
    init_db()
    # Start the AI simulator thread
    ai_thread = threading.Thread(target=simulate_ai_camera_feed, daemon=True)
    ai_thread.start()
    
    print("Starting SafetyMonitor Backend on port 9091...")
    app.run(host='0.0.0.0', port=9091)
