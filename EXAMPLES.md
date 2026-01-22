# SynapseNotify - Usage Examples

10 real-world examples with expected output.

---

## Example 1: Basic Session Start Check

**Scenario:** ATLAS starts a new session and checks for pending alerts.

**Command:**
```bash
python synapsenotify.py check ATLAS
```

**Expected Output (No Alerts):**
```
[OK] No new messages for ATLAS
```

**Expected Output (With Alerts):**
```
============================================================
[!] 2 NEW MESSAGE(S) FOR ATLAS
============================================================

[!] HIGH PRIORITY:
  From: FORGE - Code Review Required
  Preview: Please review the TokenTracker changes before mer...

[i] NORMAL MESSAGES:
  From: CLIO - Ubuntu Tests Complete

============================================================
Run: synapsenotify read <agent> - to mark all as read
Run: synapsenotify clear <agent> - to clear alerts
============================================================
```

---

## Example 2: Create Alert from Synapse Message

**Scenario:** SynapseWatcher detected a new message, now create alerts.

**Command:**
```bash
python synapsenotify.py alert D:\BEACON_HQ\MEMORY_CORE_V2\03_INTER_AI_COMMS\THE_SYNAPSE\active\forge_message.json
```

**Expected Output:**
```
[OK] Alert created for ATLAS from FORGE: Code Review Required
[OK] Alert created for CLIO from FORGE: Code Review Required
[OK] Created 2 alert(s) from forge_message.json
```

---

## Example 3: Get Alert Count

**Scenario:** Quickly check how many unread alerts without full report.

**Command:**
```bash
python synapsenotify.py count FORGE
```

**Expected Output:**
```
3
```

---

## Example 4: List All Alerts

**Scenario:** See detailed list of all alerts including read ones.

**Command:**
```bash
python synapsenotify.py list ATLAS --all
```

**Expected Output:**
```
Alerts for ATLAS:

  [NEW] [HIGH] From FORGE: Code Review Required
       ID: abc123def456 | 2026-01-22T11:55:00
       File: /path/to/message.json

  [READ] [NORMAL] From CLIO: Tests Complete
       ID: xyz789abc123 | 2026-01-22T10:30:00
       File: /path/to/another.json
```

---

## Example 5: Mark Single Alert as Read

**Scenario:** Mark a specific alert as read by ID.

**Command:**
```bash
python synapsenotify.py read ATLAS abc123def456
```

**Expected Output:**
```
[OK] Marked 1 alert(s) as read for ATLAS
```

---

## Example 6: Mark All Alerts as Read

**Scenario:** Mark all alerts as read after reviewing.

**Command:**
```bash
python synapsenotify.py read ATLAS
```

**Expected Output:**
```
[OK] Marked 3 alert(s) as read for ATLAS
```

---

## Example 7: Clear All Alerts

**Scenario:** Clear all alerts after processing.

**Command:**
```bash
python synapsenotify.py clear ATLAS
```

**Expected Output:**
```
[OK] Cleared 3 alert(s) for ATLAS
```

---

## Example 8: Clear Only Read Alerts

**Scenario:** Keep unread alerts but clear old read ones.

**Command:**
```bash
python synapsenotify.py clear ATLAS --keep
```

**Expected Output:**
```
[OK] Cleared 2 alert(s) for ATLAS
```

---

## Example 9: Check Status Across All Agents

**Scenario:** Dashboard view of which agents have pending alerts.

**Command:**
```bash
python synapsenotify.py status
```

**Expected Output (Alerts Pending):**
```
Agents with pending alerts:

  FORGE: 3 unread
  ATLAS: 1 unread
  CLIO: 2 unread
```

**Expected Output (No Alerts):**
```
[OK] No pending alerts for any agent
```

---

## Example 10: Python API Integration

**Scenario:** Integrate SynapseNotify into an agent's startup script.

**Script:**
```python
#!/usr/bin/env python3
"""Agent session start script with SynapseNotify integration."""

import sys
sys.path.insert(0, r'C:\Users\logan\OneDrive\Documents\AutoProjects\SynapseNotify')
from synapsenotify import SynapseNotify

AGENT_NAME = "ATLAS"

def main():
    print(f"=== {AGENT_NAME} Session Start ===")
    print()
    
    # Initialize notifier
    notifier = SynapseNotify(enable_bell=True)
    
    # Check for alerts
    count = notifier.get_alert_count(AGENT_NAME)
    
    if count > 0:
        # Show full report
        report = notifier.check_and_report(AGENT_NAME, bell=True)
        print(report)
        
        # Get alerts by priority
        critical = notifier.get_alerts(AGENT_NAME, priority="CRITICAL")
        high = notifier.get_alerts(AGENT_NAME, priority="HIGH")
        
        if critical:
            print("\n[!!!] CRITICAL ALERTS REQUIRE IMMEDIATE ATTENTION!")
            for alert in critical:
                print(f"      {alert.from_agent}: {alert.subject}")
        
        if high:
            print("\n[!] High priority alerts should be addressed first.")
        
        # Prompt user
        print("\n[!] Review THE_SYNAPSE messages before continuing.")
        input("Press Enter after reviewing messages...")
        
        # Mark as read
        notifier.mark_read(AGENT_NAME)
        print("[OK] Alerts marked as read.")
    else:
        print(f"[OK] No pending messages for {AGENT_NAME}")
        print("[OK] Ready to begin session.")
    
    print()
    print("=== Session Ready ===")

if __name__ == "__main__":
    main()
```

**Expected Output (With High Priority Alert):**
```
=== ATLAS Session Start ===

============================================================
[!] 2 NEW MESSAGE(S) FOR ATLAS
============================================================

[!] HIGH PRIORITY:
  From: FORGE - Urgent Code Review
  Preview: Need this reviewed before the 5PM deadline...

[i] NORMAL MESSAGES:
  From: CLIO - Test Results

============================================================
Run: synapsenotify read <agent> - to mark all as read
Run: synapsenotify clear <agent> - to clear alerts
============================================================

[!] High priority alerts should be addressed first.

[!] Review THE_SYNAPSE messages before continuing.
Press Enter after reviewing messages...

[OK] Alerts marked as read.

=== Session Ready ===
```

---

## All Examples Tested ✅

These examples have been verified to work correctly with SynapseNotify v1.0.
