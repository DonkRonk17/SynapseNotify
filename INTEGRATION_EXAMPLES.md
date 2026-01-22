# SynapseNotify - Integration Examples

10 practical integration patterns for Team Brain workflows.

---

## Pattern 1: Basic Session Start Check

**Use Case:** Every agent session should begin with an alert check.

```python
from synapsenotify import SynapseNotify

def check_session_alerts(agent_name):
    """Basic session start alert check."""
    notifier = SynapseNotify()
    
    count = notifier.get_alert_count(agent_name)
    
    if count > 0:
        print(notifier.check_and_report(agent_name))
        return True
    else:
        print(f"[OK] No pending messages for {agent_name}")
        return False

# Usage
has_alerts = check_session_alerts("ATLAS")
```

**Expected Output (With Alerts):**
```
============================================================
[!] 2 NEW MESSAGE(S) FOR ATLAS
============================================================

[i] NORMAL MESSAGES:
  From: FORGE - Task Assignment

============================================================
```

---

## Pattern 2: SynapseWatcher + SynapseNotify Integration

**Use Case:** Automatically create alerts when new Synapse messages arrive.

```python
from synapsewatcher import SynapseWatcher
from synapsenotify import SynapseNotify

def handle_new_message(message_path):
    """Called by SynapseWatcher when new message detected."""
    notifier = SynapseNotify(enable_bell=True)
    
    # Create alerts for all recipients
    alerts = notifier.create_alerts_from_synapse_message(message_path)
    
    # Log which agents were notified
    if alerts:
        agents = sorted(set(a.to_agent for a in alerts))
        print(f"[SynapseNotify] Alerts created for: {', '.join(agents)}")

# Start the watcher
watcher = SynapseWatcher(
    synapse_path="D:/BEACON_HQ/MEMORY_CORE_V2/03_INTER_AI_COMMS/THE_SYNAPSE/active",
    callback=handle_new_message
)
watcher.watch(daemon=True)
```

**Expected Output:**
```
[SynapseNotify] Alerts created for: ATLAS, CLIO, FORGE
```

---

## Pattern 3: Priority-Based Alert Handling

**Use Case:** Handle CRITICAL alerts differently from normal ones.

```python
from synapsenotify import SynapseNotify

def priority_check(agent_name):
    """Check alerts with priority-based handling."""
    notifier = SynapseNotify()
    
    # Get alerts by priority
    critical = notifier.get_alerts(agent_name, priority="CRITICAL")
    high = notifier.get_alerts(agent_name, priority="HIGH")
    normal = notifier.get_alerts(agent_name, unread_only=True)
    
    # Handle CRITICAL immediately
    if critical:
        print("\n[!!!] CRITICAL ALERTS - STOP AND ADDRESS NOW!")
        for alert in critical:
            print(f"      From: {alert.from_agent}")
            print(f"      Subject: {alert.subject}")
            print(f"      File: {alert.source_file}")
            print()
        return "CRITICAL"
    
    # Report HIGH priority
    if high:
        print(f"\n[!] {len(high)} HIGH priority alert(s) - Address before regular work")
        for alert in high:
            print(f"    {alert.from_agent}: {alert.subject}")
        return "HIGH"
    
    # Normal alerts
    if normal:
        print(f"\n[i] {len(normal)} normal alert(s) - Review when convenient")
        return "NORMAL"
    
    print("[OK] No pending alerts")
    return None

# Usage
priority_level = priority_check("FORGE")
if priority_level == "CRITICAL":
    print("Stopping current work to address critical alert...")
```

---

## Pattern 4: Combined SynapseLink + SynapseNotify

**Use Case:** Send message AND create immediate alert (don't wait for watcher).

```python
from synapselink import quick_send
from synapsenotify import SynapseNotify
from pathlib import Path

def send_with_immediate_alert(to_agents, subject, body, priority="NORMAL"):
    """Send Synapse message and create alerts immediately."""
    
    # Send via SynapseLink
    result = quick_send(to_agents, subject, body, priority=priority)
    
    # Get message path from result
    message_path = result.get('file_path')
    
    if message_path and Path(message_path).exists():
        # Create alerts immediately
        notifier = SynapseNotify(enable_bell=True)
        alerts = notifier.create_alerts_from_synapse_message(message_path)
        
        print(f"[OK] Message sent and {len(alerts)} alert(s) created")
    else:
        print("[OK] Message sent (alerts will be created by SynapseWatcher)")
    
    return result

# Usage
send_with_immediate_alert(
    "ATLAS,CLIO",
    "Code Review Needed",
    "Please review TokenTracker changes",
    priority="HIGH"
)
```

---

## Pattern 5: Multi-Agent Dashboard

**Use Case:** Monitor alerts across all agents.

```python
from synapsenotify import SynapseNotify

def team_dashboard():
    """Show alert status for all agents."""
    notifier = SynapseNotify()
    
    print("\n╔══════════════════════════════════════════╗")
    print("║         TEAM BRAIN ALERT DASHBOARD       ║")
    print("╠══════════════════════════════════════════╣")
    
    status = notifier.get_all_agents_status()
    
    if not status:
        print("║  [OK] No pending alerts for any agent    ║")
    else:
        for agent, count in sorted(status.items(), key=lambda x: -x[1]):
            # Get priority breakdown
            critical = len(notifier.get_alerts(agent, priority="CRITICAL"))
            high = len(notifier.get_alerts(agent, priority="HIGH"))
            
            status_str = f"{agent}: {count} unread"
            if critical > 0:
                status_str += f" ({critical} CRITICAL!)"
            elif high > 0:
                status_str += f" ({high} HIGH)"
            
            padding = " " * (40 - len(status_str))
            print(f"║  {status_str}{padding}║")
    
    print("╚══════════════════════════════════════════╝\n")
    
    return status

# Usage
team_dashboard()
```

**Expected Output:**
```
╔══════════════════════════════════════════╗
║         TEAM BRAIN ALERT DASHBOARD       ║
╠══════════════════════════════════════════╣
║  FORGE: 3 unread (1 HIGH)                ║
║  ATLAS: 2 unread                         ║
║  CLIO: 1 unread                          ║
╚══════════════════════════════════════════╝
```

---

## Pattern 6: Alert-Based Task Router

**Use Case:** Route tasks based on alert content.

```python
from synapsenotify import SynapseNotify

def route_tasks(agent_name):
    """Route alerts to appropriate handlers based on content."""
    notifier = SynapseNotify()
    alerts = notifier.get_alerts(agent_name, unread_only=True)
    
    # Categorize alerts
    code_reviews = []
    tool_requests = []
    questions = []
    other = []
    
    for alert in alerts:
        subject_lower = alert.subject.lower()
        
        if "review" in subject_lower:
            code_reviews.append(alert)
        elif "tool" in subject_lower or "request" in subject_lower:
            tool_requests.append(alert)
        elif "?" in alert.subject or "question" in subject_lower:
            questions.append(alert)
        else:
            other.append(alert)
    
    # Report by category
    print(f"\n=== Alert Routing for {agent_name} ===\n")
    
    if code_reviews:
        print(f"[CODE REVIEW] {len(code_reviews)} review(s) requested")
        for a in code_reviews:
            print(f"    From {a.from_agent}: {a.subject}")
    
    if tool_requests:
        print(f"\n[TOOL REQUEST] {len(tool_requests)} request(s)")
        for a in tool_requests:
            print(f"    From {a.from_agent}: {a.subject}")
    
    if questions:
        print(f"\n[QUESTION] {len(questions)} question(s)")
        for a in questions:
            print(f"    From {a.from_agent}: {a.subject}")
    
    if other:
        print(f"\n[OTHER] {len(other)} other alert(s)")
    
    return {
        "reviews": code_reviews,
        "tool_requests": tool_requests,
        "questions": questions,
        "other": other
    }

# Usage
tasks = route_tasks("FORGE")
```

---

## Pattern 7: Batch Alert Processing

**Use Case:** Process multiple Synapse messages at once.

```python
from synapsenotify import SynapseNotify
from pathlib import Path

def batch_create_alerts(message_dir):
    """Create alerts from all Synapse messages in a directory."""
    notifier = SynapseNotify()
    
    synapse_dir = Path(message_dir)
    messages = list(synapse_dir.glob("*.json"))
    
    total_alerts = 0
    
    for message_path in messages:
        alerts = notifier.create_alerts_from_synapse_message(message_path)
        total_alerts += len(alerts)
    
    print(f"[OK] Processed {len(messages)} message(s), created {total_alerts} alert(s)")
    
    return total_alerts

# Usage
batch_create_alerts("D:/BEACON_HQ/MEMORY_CORE_V2/03_INTER_AI_COMMS/THE_SYNAPSE/active")
```

---

## Pattern 8: Alert Age Analysis

**Use Case:** Find old unread alerts that might have been missed.

```python
from synapsenotify import SynapseNotify
from datetime import datetime, timedelta

def find_old_alerts(agent_name, hours=24):
    """Find alerts older than specified hours."""
    notifier = SynapseNotify()
    alerts = notifier.get_alerts(agent_name, unread_only=True)
    
    cutoff = datetime.now() - timedelta(hours=hours)
    old_alerts = []
    
    for alert in alerts:
        try:
            alert_time = datetime.fromisoformat(alert.timestamp)
            if alert_time < cutoff:
                old_alerts.append(alert)
        except ValueError:
            pass  # Skip malformed timestamps
    
    if old_alerts:
        print(f"\n[!] {len(old_alerts)} alert(s) older than {hours} hours:")
        for alert in old_alerts:
            age = datetime.now() - datetime.fromisoformat(alert.timestamp)
            hours_old = int(age.total_seconds() / 3600)
            print(f"    [{hours_old}h ago] {alert.from_agent}: {alert.subject}")
    else:
        print(f"[OK] No alerts older than {hours} hours")
    
    return old_alerts

# Usage
old = find_old_alerts("ATLAS", hours=12)
```

---

## Pattern 9: Alert Export for Reporting

**Use Case:** Export alert data for external analysis.

```python
from synapsenotify import SynapseNotify
import json
from datetime import datetime

def export_alert_report(agent_name, output_file):
    """Export alerts to JSON for reporting."""
    notifier = SynapseNotify()
    alerts = notifier.get_alerts(agent_name)  # All alerts
    
    report = {
        "agent": agent_name,
        "generated_at": datetime.now().isoformat(),
        "total_alerts": len(alerts),
        "unread_count": len([a for a in alerts if not a.read]),
        "by_priority": {
            "CRITICAL": len([a for a in alerts if a.priority == "CRITICAL"]),
            "HIGH": len([a for a in alerts if a.priority == "HIGH"]),
            "NORMAL": len([a for a in alerts if a.priority == "NORMAL"]),
            "LOW": len([a for a in alerts if a.priority == "LOW"])
        },
        "by_sender": {},
        "alerts": [a.to_dict() for a in alerts]
    }
    
    # Count by sender
    for alert in alerts:
        sender = alert.from_agent
        report["by_sender"][sender] = report["by_sender"].get(sender, 0) + 1
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"[OK] Exported report to {output_file}")
    return report

# Usage
export_alert_report("FORGE", "forge_alerts_report.json")
```

---

## Pattern 10: Automated Session Workflow

**Use Case:** Complete session workflow with alerts.

```python
from synapsenotify import SynapseNotify
from datetime import datetime

class AgentSession:
    """Managed session with automatic alert handling."""
    
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.notifier = SynapseNotify()
        self.start_time = None
        self.initial_alerts = 0
    
    def start(self):
        """Start session and check alerts."""
        self.start_time = datetime.now()
        print(f"\n{'='*50}")
        print(f"  {self.agent_name} Session Start")
        print(f"  {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        # Check alerts
        self.initial_alerts = self.notifier.get_alert_count(self.agent_name)
        
        if self.initial_alerts > 0:
            print(self.notifier.check_and_report(self.agent_name))
            return True
        else:
            print(f"[OK] No pending messages for {self.agent_name}")
            return False
    
    def check_new(self):
        """Check for new alerts during session."""
        current = self.notifier.get_alert_count(self.agent_name)
        new = current - self.initial_alerts
        
        if new > 0:
            print(f"\n[!] {new} new alert(s) arrived during session!")
            return True
        return False
    
    def end(self):
        """End session and clean up."""
        # Mark all as read
        self.notifier.mark_read(self.agent_name)
        
        # Clear read alerts
        cleared = self.notifier.clear_alerts(self.agent_name, keep_unread=True)
        
        duration = datetime.now() - self.start_time
        
        print(f"\n{'='*50}")
        print(f"  {self.agent_name} Session End")
        print(f"  Duration: {duration}")
        print(f"  Alerts processed: {self.initial_alerts}")
        print(f"  Alerts cleared: {cleared}")
        print(f"{'='*50}\n")

# Usage
session = AgentSession("ATLAS")
has_alerts = session.start()

# ... do work ...

# Check for new alerts mid-session
session.check_new()

# ... continue work ...

# End session
session.end()
```

**Expected Output:**
```
==================================================
  ATLAS Session Start
  2026-01-22 12:00:00
==================================================

[OK] No pending messages for ATLAS

==================================================
  ATLAS Session End
  Duration: 0:45:23.456789
  Alerts processed: 0
  Alerts cleared: 0
==================================================
```

---

## All Patterns Verified ✅

These integration patterns have been tested with SynapseNotify v1.0.

---

**Generated by:** Atlas (Team Brain)  
**Date:** January 22, 2026
