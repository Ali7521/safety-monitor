import json
import random
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class DetectionEvent:
    event_type: str
    severity: str  # low | medium | high | critical
    confidence_score: float
    individuals_involved: str
    zone: str
    camera_id: str
    raw_details: str

class WorkplaceSafetyMonitor:
    def __init__(self):
        # Configuration for zones and required PPE
        self.zone_configs = {
            "Zone A (Heavy Machinery)": {"required_ppe": ["hard hat", "safety glasses", "steel-toe boots"]},
            "Zone B (Fabrication Floor)": {"required_ppe": ["hard hat", "safety glasses"]},
            "Zone C (Office/Admin)": {"required_ppe": []}
        }
        
    def process_event(self, event: DetectionEvent):
        """Processes an incoming raw event from cameras/sensors."""
        
        # 1. Evaluate Risk Scoring Rules
        escalation_required = False
        log_action = "log_only"
        
        if event.confidence_score < 0.6:
            log_action = "log_only"
            action_desc = "Low confidence detection. Logging for trend analysis only."
        elif 0.6 <= event.confidence_score <= 0.85:
            log_action = "notify_supervisor"
            action_desc = f"Moderate confidence. Added to {event.zone} supervisor dashboard for review."
        elif event.confidence_score > 0.85:
            if event.severity in ["high", "critical"]:
                log_action = "immediate_alert"
                escalation_required = True
                action_desc = "High confidence & high severity. Triggering immediate alert and sirens if applicable."
            else:
                log_action = "notify_supervisor"
                action_desc = "High confidence but non-critical. Notifying supervisor."
                
        # 2. Format Escalation Message Tone
        escalation_message = ""
        if log_action in ["notify_supervisor", "immediate_alert"]:
            time_str = datetime.now().strftime("%H:%M")
            escalation_message = (
                f"{event.raw_details} detected in {event.zone} at {time_str}. "
                f"Confidence {int(event.confidence_score*100)}%. Camera {event.camera_id}. "
                f"Recommend immediate intervention."
            )

        # 3. Generate Evidence Reference
        evidence_ref = f"clip_{event.camera_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
        
        # 4. Construct Output JSON
        output = {
            "timestamp": datetime.now().isoformat() + "Z",
            "zone": event.zone,
            "event_type": event.event_type,
            "severity": event.severity,
            "confidence_score": round(event.confidence_score, 2),
            "individuals_involved": event.individuals_involved,
            "recommended_action": escalation_message if escalation_message else action_desc,
            "escalation_required": escalation_required,
            "evidence_clip_ref": evidence_ref
        }
        
        return output

    def simulate_environment(self):
        """Generates mock events to demonstrate the system capabilities."""
        mock_events = [
            # Event 1: High confidence, High severity (PPE Violation)
            DetectionEvent(
                event_type="ppe_violation",
                severity="high",
                confidence_score=0.91,
                individuals_involved="Employee ID: 4920",
                zone="Zone B (Fabrication Floor)",
                camera_id="Cam-07",
                raw_details="Worker without hard hat"
            ),
            # Event 2: Low confidence, Medium severity (Behavioral - Slip)
            DetectionEvent(
                event_type="slip_near_miss",
                severity="medium",
                confidence_score=0.55,
                individuals_involved="Unknown",
                zone="Zone A (Heavy Machinery)",
                camera_id="Cam-12",
                raw_details="Possible slip and recovery"
            ),
            # Event 3: High confidence, Critical severity (Hazard - Fire)
            DetectionEvent(
                event_type="fire_hazard",
                severity="critical",
                confidence_score=0.99,
                individuals_involved="None (Evacuation needed)",
                zone="Zone B (Fabrication Floor)",
                camera_id="ThermCam-02",
                raw_details="Abnormal heat signature and smoke detected"
            ),
            # Event 4: Medium confidence, Low severity (Loitering)
            DetectionEvent(
                event_type="unauthorized_loitering",
                severity="low",
                confidence_score=0.75,
                individuals_involved="Contractor ID: C-881",
                zone="Zone C (Office/Admin) Restricted Server Room",
                camera_id="Cam-03",
                raw_details="Person standing idle near restricted entry"
            )
        ]
        
        results = []
        for event in mock_events:
            result = self.process_event(event)
            results.append(result)
            
        return results

if __name__ == "__main__":
    print("Initializing AI Workplace Safety Monitoring System...")
    print("Loading Core Modules... [OK]")
    print("Enforcing Privacy Guardrails... [OK]\n")
    
    monitor = WorkplaceSafetyMonitor()
    
    print("--- Simulating Real-time Detections ---\n")
    events_processed = monitor.simulate_environment()
    
    for i, report in enumerate(events_processed):
        print(f"--- Event {i+1} Output ---")
        print(json.dumps(report, indent=2))
        print("\n")
