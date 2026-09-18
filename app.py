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
ZONES = ["Zone A (Heavy Machinery)", "Zone B (Fabrication)", "Zone C (Office)", "Zone D (Loading Dock)"]
EVENT_TYPES = ["ppe_violation", "slip_near_miss", "fire_hazard", "unauthorized_loitering", "vehicle_proximity", "fatigue_detected"]
SEVERITIES = ["low", "medium", "high", "critical"]

def simulate_ai_camera_feed():
    while True:
        time.sleep(random.randint(10, 25)) # Trigger event every 10-25 seconds
        
        event = {
            "timestamp": datetime.now().isoformat() + "Z",
            "zone": random.choice(ZONES),
            "event_type": random.choice(EVENT_TYPES),
            "severity": random.choice(SEVERITIES),
            "confidence": round(random.uniform(0.65, 0.99), 2),
            "individuals": f"Emp-{random.randint(1000, 9999)}",
            "action_taken": "Logged via AI Simulator",
            "status": "Open"
        }
        
        # Add special features logic
        if event["event_type"] == "fatigue_detected":
            event["action_taken"] = "Predictive Fatigue Warning Issued. Supervisor Notified."
        elif event["event_type"] == "vehicle_proximity":
            event["severity"] = "critical"
            event["action_taken"] = "Gen-AI Voice Coach activated: 'Please step back from the forklift lane.'"
        
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
    
    print("Starting SafetyMonitor Backend on port 5001...")
    app.run(host='0.0.0.0', port=5001)
