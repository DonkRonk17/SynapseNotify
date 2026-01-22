# SynapseNotify - Agent Quick Start Guides

Individual quick start guides for each Team Brain agent.

---

## Table of Contents

1. [FORGE Quick Start](#forge-quick-start)
2. [ATLAS Quick Start](#atlas-quick-start)
3. [CLIO Quick Start](#clio-quick-start)
4. [IRIS Quick Start](#iris-quick-start)
5. [NEXUS Quick Start](#nexus-quick-start)
6. [PORTER Quick Start](#porter-quick-start)
7. [BOLT Quick Start](#bolt-quick-start)
8. [GEMINI Quick Start](#gemini-quick-start)
9. [Universal Integration Template](#universal-integration-template)
10. [Troubleshooting](#troubleshooting)

---

## FORGE Quick Start

**Agent Type:** Orchestrator (Cursor IDE)  
**Primary Role:** Task coordination, code review, planning  
**Bell Support:** ❌ (IDE environment)

### Session Start Routine

Add this to every FORGE session beginning:

```python
from synapsenotify import SynapseNotify

# Initialize
notifier = SynapseNotify()

# Check for alerts
print(notifier.check_and_report("FORGE"))

# Check for CRITICAL alerts specifically
critical = notifier.get_alerts("FORGE", priority="CRITICAL")
if critical:
    print("\n[!!!] CRITICAL ALERTS - Address FIRST!")
    for alert in critical:
        print(f"      From {alert.from_agent}: {alert.subject}")
```

### Expected Output

**No alerts:**
```
[OK] No new messages for FORGE
```

**With alerts:**
```
============================================================
[!] 3 NEW MESSAGE(S) FOR FORGE
============================================================

[!] HIGH PRIORITY:
  From: ATLAS - Code Review for TokenTracker
  Preview: Tests passing, ready for review...

[i] NORMAL MESSAGES:
  From: CLIO - Ubuntu Tests Complete
  From: IRIS - Desktop Phase 2A Done

============================================================
```

### After Reading Messages

```python
# After reviewing messages in THE_SYNAPSE
notifier.mark_read("FORGE")
```

### Clear Old Alerts

```python
# Clear all after addressing
notifier.clear_alerts("FORGE")
```

---

## ATLAS Quick Start

**Agent Type:** Executor / Builder (Cursor IDE)  
**Primary Role:** Tool creation, testing, automation  
**Bell Support:** ❌ (IDE environment)

### Session Start Routine

Add to every ATLAS session:

```python
from synapsenotify import SynapseNotify

def atlas_startup():
    notifier = SynapseNotify()
    
    # Get count first
    count = notifier.get_alert_count("ATLAS")
    
    if count > 0:
        # Full report
        print(notifier.check_and_report("ATLAS"))
        
        # Check for tool requests (usually HIGH priority)
        high_priority = notifier.get_alerts("ATLAS", priority="HIGH")
        if high_priority:
            print("\n[!] Tool requests or urgent tasks detected!")
        
        return True  # Has work
    else:
        print("[OK] No pending messages for ATLAS")
        return False  # Ready for new work

has_work = atlas_startup()
```

### One-Line Check

```bash
python -c "from synapsenotify import SynapseNotify; print(SynapseNotify().check_and_report('ATLAS'))"
```

### After Completing Tasks

```python
# Mark as read
notifier.mark_read("ATLAS")

# Or clear entirely
notifier.clear_alerts("ATLAS")
```

---

## CLIO Quick Start

**Agent Type:** CLI / Terminal (Linux)  
**Primary Role:** Backend, testing, Ubuntu operations  
**Bell Support:** ✅

### Installation

```bash
# Clone to projects
cd ~/projects
git clone https://github.com/DonkRonk17/SynapseNotify.git

# Create alias
echo 'alias syncheck="python3 ~/projects/SynapseNotify/synapsenotify.py check CLIO"' >> ~/.bashrc
echo 'alias synclear="python3 ~/projects/SynapseNotify/synapsenotify.py clear CLIO"' >> ~/.bashrc
source ~/.bashrc
```

### Session Start

```bash
# Simple check (will beep if alerts!)
syncheck
```

**Or full script:**
```bash
#!/bin/bash
# clio_session.sh

echo "╔════════════════════════════════════════╗"
echo "║       CLIO Session Start               ║"
echo "╚════════════════════════════════════════╝"
echo ""

python3 ~/projects/SynapseNotify/synapsenotify.py check CLIO
```

### After Work

```bash
# Clear alerts
synclear
```

### Terminal Bell

The bell will automatically sound when you have unread alerts. If you don't hear it:

```bash
# Test bell
python3 ~/projects/SynapseNotify/synapsenotify.py bell
```

---

## IRIS Quick Start

**Agent Type:** Desktop Developer (Cursor IDE)  
**Primary Role:** BCH Desktop, Electron/Tauri  
**Bell Support:** ❌ (IDE environment)

### Session Start

```python
from synapsenotify import SynapseNotify

# Simple one-liner
print(SynapseNotify().check_and_report("IRIS"))
```

### Full Integration

```python
from synapsenotify import SynapseNotify

def iris_session_start():
    notifier = SynapseNotify()
    
    # Check for alerts
    report = notifier.check_and_report("IRIS")
    print(report)
    
    # Look for BCH-related alerts
    alerts = notifier.get_alerts("IRIS", unread_only=True)
    bch_alerts = [a for a in alerts if "BCH" in a.subject or "desktop" in a.subject.lower()]
    
    if bch_alerts:
        print(f"\n[i] {len(bch_alerts)} BCH-related alert(s)")
    
    return notifier.get_alert_count("IRIS")

alert_count = iris_session_start()
```

---

## NEXUS Quick Start

**Agent Type:** Multi-Platform (VS Code/CLI)  
**Primary Role:** Cross-platform operations  
**Bell Support:** ✅ (CLI mode only)

### Session Start

```python
from synapsenotify import SynapseNotify
import platform

# Enable bell only in CLI environments
is_cli = platform.system() != "Windows" or "TERM" in os.environ
notifier = SynapseNotify(enable_bell=is_cli)

print(notifier.check_and_report("NEXUS"))
```

### CLI Mode

```bash
python synapsenotify.py check NEXUS
```

### IDE Mode

```python
from synapsenotify import SynapseNotify
print(SynapseNotify(enable_bell=False).check_and_report("NEXUS"))
```

---

## PORTER Quick Start

**Agent Type:** Mobile Developer  
**Primary Role:** BCH Mobile (React Native)  
**Bell Support:** ❌

### Session Start

```python
from synapsenotify import SynapseNotify

# Simple check
notifier = SynapseNotify(enable_bell=False)
print(notifier.check_and_report("PORTER"))
```

### Mobile-Focused Check

```python
def porter_startup():
    notifier = SynapseNotify()
    alerts = notifier.get_alerts("PORTER", unread_only=True)
    
    # Filter for mobile-related
    mobile_alerts = [a for a in alerts if any(kw in a.subject.lower() 
                    for kw in ["mobile", "react native", "ios", "android", "bch"])]
    
    if mobile_alerts:
        print(f"[!] {len(mobile_alerts)} mobile-related alert(s):")
        for alert in mobile_alerts:
            print(f"    {alert.from_agent}: {alert.subject}")
    elif alerts:
        print(notifier.check_and_report("PORTER"))
    else:
        print("[OK] No pending messages for PORTER")

porter_startup()
```

---

## BOLT Quick Start

**Agent Type:** CLI Executor (Free Tier)  
**Primary Role:** Task execution via Cline/Grok  
**Bell Support:** ✅

### CLI Check

```bash
python synapsenotify.py check BOLT
```

### Automated Check

```python
from synapsenotify import SynapseNotify

notifier = SynapseNotify(enable_bell=True)  # Bell enabled
report = notifier.check_and_report("BOLT")
print(report)
```

### Task-Focused

```python
# Look for task assignments
alerts = notifier.get_alerts("BOLT", unread_only=True)
tasks = [a for a in alerts if "task" in a.subject.lower() or a.priority in ["HIGH", "CRITICAL"]]

if tasks:
    print(f"[!] {len(tasks)} task(s) assigned to BOLT")
```

---

## GEMINI Quick Start

**Agent Type:** Extension (Backup)  
**Primary Role:** Orchestrator backup  
**Bell Support:** ❌

### Session Start

```python
from synapsenotify import SynapseNotify

# Simple check
print(SynapseNotify().check_and_report("GEMINI"))
```

### Clear After Session

```python
# Clear all
notifier.clear_alerts("GEMINI")
```

---

## Universal Integration Template

**Copy and customize for any agent:**

```python
#!/usr/bin/env python3
"""
Agent Session Start Template
Replace AGENT_NAME with your agent name (FORGE, ATLAS, CLIO, etc.)
"""

import sys
sys.path.insert(0, r'C:\Users\logan\OneDrive\Documents\AutoProjects\SynapseNotify')
from synapsenotify import SynapseNotify

AGENT_NAME = "YOUR_AGENT_NAME"  # <-- CHANGE THIS

def session_start():
    """Standard session start routine."""
    print(f"=== {AGENT_NAME} Session Start ===\n")
    
    # Initialize notifier
    notifier = SynapseNotify()
    
    # Check for alerts
    count = notifier.get_alert_count(AGENT_NAME)
    
    if count > 0:
        # Show full report
        report = notifier.check_and_report(AGENT_NAME)
        print(report)
        
        # Prompt to check THE_SYNAPSE
        print("\n[!] Read messages in THE_SYNAPSE before continuing.")
        
        return True  # Has alerts
    else:
        print(f"[OK] No pending messages for {AGENT_NAME}")
        print("[OK] Ready to begin work.")
        return False  # No alerts

def session_end():
    """Standard session end routine."""
    notifier = SynapseNotify()
    
    # Clear read alerts
    notifier.clear_alerts(AGENT_NAME, keep_unread=True)
    
    print(f"\n[OK] {AGENT_NAME} session complete.")

if __name__ == "__main__":
    has_alerts = session_start()
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'synapsenotify'"

**Solution:** Add the path:
```python
import sys
sys.path.insert(0, r'C:\Users\logan\OneDrive\Documents\AutoProjects\SynapseNotify')
from synapsenotify import SynapseNotify
```

### "FileNotFoundError: AGENT_ALERTS directory"

**Solution:** The directory will be created automatically on first use. If not:
```bash
mkdir -p "D:\BEACON_HQ\MEMORY_CORE_V2\03_INTER_AI_COMMS\AGENT_ALERTS"
```

### Bell not working

**Solution 1:** Check terminal support:
```bash
python synapsenotify.py bell
```

**Solution 2:** Enable manually:
```python
notifier = SynapseNotify(enable_bell=True)
```

### Alerts not showing

**Solution:** Ensure alerts were created. Check manually:
```bash
python synapsenotify.py alert /path/to/synapse/message.json
```

### Duplicate alerts

**SynapseNotify prevents duplicates** based on source file path. If you see duplicates, the source files are different.

---

## Need Help?

- **Post in THE_SYNAPSE:** `D:\BEACON_HQ\MEMORY_CORE_V2\03_INTER_AI_COMMS\THE_SYNAPSE\active\`
- **Contact ATLAS** for tool issues
- **GitHub Issues:** https://github.com/DonkRonk17/SynapseNotify/issues

---

**Generated by:** Atlas (Team Brain)  
**Date:** January 22, 2026
