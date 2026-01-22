# SynapseNotify - Integration Plan

## 🎯 INTEGRATION GOALS

This document outlines how SynapseNotify integrates with:
1. Team Brain agents (Forge, Atlas, Clio, Nexus, Bolt, Iris, Porter)
2. Existing Team Brain tools (SynapseWatcher, SynapseLink)
3. BCH (Beacon Command Hub) - future potential
4. Agent session workflows

---

## 📖 ABOUT THIS DOCUMENT

**Document Purpose:** Complete integration guide for deploying SynapseNotify across Team Brain

**Target Audience:** AI agents, automation developers

**Last Updated:** January 22, 2026

**Maintained By:** Atlas (Team Brain)

---

## 📦 BCH INTEGRATION

### Overview

SynapseNotify has **high BCH integration potential** as the notification layer for all agent communications.

**Current Status:** Not yet integrated with BCH  
**Planned Integration:** Phase 3 (BCH Notifications)

### BCH Integration Architecture

```
BCH Desktop/Mobile App
    │
    ├── Agent Notifications Panel
    │   ├── Badge count (unread per agent)
    │   ├── Priority indicators (color-coded)
    │   ├── Alert list view
    │   └── Mark read / clear buttons
    │
    ├── Push Notifications
    │   ├── Mobile push when agent gets message
    │   ├── Desktop notification popup
    │   └── Sound alerts for HIGH/CRITICAL
    │
    └── Admin Dashboard
        ├── All agents notification status
        ├── Message routing visualization
        └── Alert history and analytics
```

### Proposed BCH Commands

```
# Check alerts for an agent
@synapsenotify check ATLAS

# Create manual alert
@synapsenotify alert FORGE "Code review needed"

# Clear alerts
@synapsenotify clear ATLAS
```

### Implementation Steps (Future)

1. **Phase 3:** Add SynapseNotify to BCH backend
2. **REST Endpoints:**
   - `GET /api/notifications/{agent}` - Get agent alerts
   - `POST /api/notifications/create` - Create alert
   - `DELETE /api/notifications/{agent}` - Clear alerts
3. **WebSocket Events:**
   - `notification:new` - Real-time alert push
   - `notification:read` - Mark read event
4. **UI Components:**
   - Notification badge in agent panel
   - Alert list drawer
   - Push notification triggers

---

## 🤖 AI AGENT INTEGRATION

### Integration Matrix

| Agent | Primary Use Case | Session Start Check | Bell Support | Priority |
|-------|-----------------|---------------------|--------------|----------|
| **FORGE** | Orchestration alerts | ✅ Required | ❌ (IDE) | HIGH |
| **ATLAS** | Build task alerts | ✅ Required | ❌ (IDE) | HIGH |
| **CLIO** | CLI notifications | ✅ Required | ✅ | MEDIUM |
| **IRIS** | Desktop alerts | ✅ Required | ❌ (IDE) | MEDIUM |
| **NEXUS** | Cross-platform | ✅ Required | ✅ (CLI mode) | MEDIUM |
| **PORTER** | Mobile alerts | Via BCH | ❌ | LOW |
| **BOLT** | Task notifications | ✅ Optional | ✅ | LOW |

### Agent-Specific Workflows

---

#### FORGE (Orchestrator)

**Primary Use Case:** Receive alerts when agents need review or have questions

**Integration Steps:**

1. **Session Start Check:**
```python
# Add to Forge session startup
from synapsenotify import SynapseNotify

def forge_startup():
    notifier = SynapseNotify()
    
    # Check for alerts
    count = notifier.get_alert_count("FORGE")
    
    if count > 0:
        print(notifier.check_and_report("FORGE"))
        
        # Check for CRITICAL alerts specifically
        critical = notifier.get_alerts("FORGE", priority="CRITICAL")
        if critical:
            print("\n[!!!] CRITICAL ALERTS - Address immediately!")
            for alert in critical:
                print(f"      From {alert.from_agent}: {alert.subject}")
    else:
        print("[OK] No pending messages for FORGE")

forge_startup()
```

2. **After Orchestration Session:**
```python
# Mark alerts as read after addressing
notifier.mark_read("FORGE")
```

**Typical FORGE Alerts:**
- Code reviews requested by ATLAS
- Questions from CLIO about implementations
- Status updates from other agents
- CRITICAL: Build failures or blockers

---

#### ATLAS (Executor / Builder)

**Primary Use Case:** Receive build instructions, tool requests, review feedback

**Integration Steps:**

1. **Session Start:**
```python
from synapsenotify import SynapseNotify

def atlas_session_start():
    notifier = SynapseNotify()
    report = notifier.check_and_report("ATLAS")
    print(report)
    
    # Get unread count
    count = notifier.get_alert_count("ATLAS")
    if count > 0:
        print(f"\n[!] {count} message(s) to review in THE_SYNAPSE")
        return True
    return False

has_alerts = atlas_session_start()
```

2. **End of Session:**
```python
# Clear alerts after processing
notifier.clear_alerts("ATLAS")
```

**Typical ATLAS Alerts:**
- Tool requests from FORGE
- Feedback on completed builds
- Priority changes
- Questions from other agents

---

#### CLIO (Linux / CLI Agent)

**Primary Use Case:** Terminal-based alerts with bell support

**Integration Steps:**

1. **Bash Alias:**
```bash
# Add to ~/.bashrc
alias syncheck='python3 ~/projects/SynapseNotify/synapsenotify.py check CLIO'
alias synclear='python3 ~/projects/SynapseNotify/synapsenotify.py clear CLIO'
```

2. **Session Start Script:**
```bash
#!/bin/bash
# clio_session_start.sh

echo "=== CLIO Session Start ==="
python3 ~/projects/SynapseNotify/synapsenotify.py check CLIO
```

3. **With Terminal Bell:**
```python
# Bell enabled by default for CLI agents
notifier = SynapseNotify(enable_bell=True)
notifier.check_and_report("CLIO", bell=True)  # Will beep if alerts
```

**Typical CLIO Alerts:**
- Test requests from ATLAS
- Ubuntu-specific tasks
- Backend work from IRIS
- Phase updates from FORGE

---

#### IRIS (Desktop Development)

**Primary Use Case:** BCH Desktop development alerts

**Integration:**
```python
from synapsenotify import SynapseNotify

# Session start
notifier = SynapseNotify()
print(notifier.check_and_report("IRIS"))

# Clear after reviewing
notifier.clear_alerts("IRIS")
```

**Typical IRIS Alerts:**
- Phase milestones from CLIO
- Desktop feature requests
- Review requests
- BCH coordination updates

---

#### NEXUS (Multi-Platform)

**Primary Use Case:** Cross-platform testing alerts

**Integration:**
```python
from synapsenotify import SynapseNotify
import platform

notifier = SynapseNotify(enable_bell=(platform.system() != "Windows"))

# Check alerts
report = notifier.check_and_report("NEXUS")
print(report)
```

---

## 🔗 INTEGRATION WITH OTHER TEAM BRAIN TOOLS

### With SynapseWatcher (CRITICAL!)

**This is the primary integration** - SynapseWatcher detects new messages and triggers SynapseNotify:

```python
# Enhanced SynapseWatcher callback
from synapsewatcher import SynapseWatcher
from synapsenotify import SynapseNotify

def on_new_synapse_message(message_path):
    """Called when SynapseWatcher detects new message."""
    
    # Create notifier
    notifier = SynapseNotify(enable_bell=True)
    
    # Parse message and create alerts for all recipients
    alerts = notifier.create_alerts_from_synapse_message(message_path)
    
    # Log
    if alerts:
        agents = set(a.to_agent for a in alerts)
        print(f"[SynapseNotify] Alerts created for: {', '.join(agents)}")

# Start watching with SynapseNotify callback
watcher = SynapseWatcher(
    synapse_path="D:/BEACON_HQ/MEMORY_CORE_V2/03_INTER_AI_COMMS/THE_SYNAPSE/active",
    callback=on_new_synapse_message
)
watcher.watch(daemon=True)
```

---

### With SynapseLink

**Use Case:** When sending a message, also create immediate alert

```python
from synapselink import quick_send
from synapsenotify import SynapseNotify

def send_and_notify(to_agents, subject, body, priority="NORMAL"):
    """Send Synapse message AND create immediate alerts."""
    
    # Send via SynapseLink
    result = quick_send(to_agents, subject, body, priority=priority)
    
    # Get the message file path from result
    message_path = result.get('file_path')
    
    if message_path:
        # Create alerts immediately (don't wait for SynapseWatcher)
        notifier = SynapseNotify()
        notifier.create_alerts_from_synapse_message(message_path)
    
    return result

# Usage
send_and_notify("ATLAS,CLIO", "Code Review", "Please review TokenTracker", priority="HIGH")
```

---

### With AgentHealth

**Use Case:** Log alert checks as health activity

```python
from agenthealth import AgentHealth
from synapsenotify import SynapseNotify

def session_start_with_health(agent_name):
    """Check alerts and log to health system."""
    
    health = AgentHealth()
    notifier = SynapseNotify()
    
    # Log session start
    health.start_session(agent_name)
    
    # Check alerts
    count = notifier.get_alert_count(agent_name)
    
    # Log alert check as activity
    health.log_activity(agent_name, "alert_check", {
        "unread_count": count,
        "status": "alerts_pending" if count > 0 else "no_alerts"
    })
    
    if count > 0:
        print(notifier.check_and_report(agent_name))
    
    return count

session_start_with_health("ATLAS")
```

---

### With TokenTracker

**Use Case:** Include alert checks in session cost tracking

```python
from tokentracker import TokenTracker
from synapsenotify import SynapseNotify

def tracked_session_start(agent_name, model):
    """Session start with both alert check and token tracking."""
    
    tracker = TokenTracker()
    notifier = SynapseNotify()
    
    # Check alerts (no token cost)
    report = notifier.check_and_report(agent_name)
    print(report)
    
    # Note: Alert checking uses no API tokens!
    # Just local file operations
    
    return notifier.get_alert_count(agent_name)
```

---

### With ToolRegistry

**Use Case:** Register SynapseNotify as available tool

```python
from toolregistry import ToolRegistry

registry = ToolRegistry()
registry.register_tool({
    "name": "SynapseNotify",
    "version": "1.0.0",
    "type": "communication",
    "description": "Push notification system for AI agents",
    "commands": ["check", "count", "list", "read", "clear", "alert", "status", "bell"],
    "path": "C:/Users/logan/OneDrive/Documents/AutoProjects/SynapseNotify",
    "dependencies": [],
    "agents": ["FORGE", "ATLAS", "CLIO", "NEXUS", "IRIS", "PORTER", "BOLT"]
})
```

---

## 🚀 ADOPTION ROADMAP

### Phase 1: Core Deployment (Day 1)

**Goal:** All agents can check alerts at session start

**Steps:**
1. ✅ Deploy SynapseNotify to GitHub
2. ☐ Create AGENT_ALERTS directory in Memory Core
3. ☐ Each agent adds session start check
4. ☐ Test alert creation/reading flow

**Success Criteria:**
- All agents can run `check` command
- Alerts persist between sessions
- No errors on empty alert state

---

### Phase 2: SynapseWatcher Integration (Week 1)

**Goal:** Automatic alert creation on new messages

**Steps:**
1. ☐ Update SynapseWatcher callback
2. ☐ Test message → alert flow
3. ☐ Enable terminal bell for CLI agents
4. ☐ Document combined workflow

**Success Criteria:**
- New Synapse messages automatically create alerts
- CLI agents hear bell on new alerts
- No duplicate alerts

---

### Phase 3: Full Team Adoption (Week 2)

**Goal:** All agents using SynapseNotify daily

**Steps:**
1. ☐ Agent-specific quick start guides distributed
2. ☐ Session start templates adopted
3. ☐ Feedback collected
4. ☐ Bug fixes applied

**Success Criteria:**
- 100% agent adoption
- No manual "check Synapse" prompting needed
- Positive feedback from agents

---

### Phase 4: BCH Integration (Future)

**Goal:** Mobile/desktop notifications via BCH

**Steps:**
1. ☐ Add notification API to BCH backend
2. ☐ Build notification UI components
3. ☐ Push notification integration
4. ☐ Cross-platform testing

**Success Criteria:**
- Logan sees agent alerts on mobile
- Real-time notification delivery
- Unified notification experience

---

## 📊 SUCCESS METRICS

### Adoption Metrics

| Metric | Target | Tracking |
|--------|--------|----------|
| Agents checking at session start | 100% | Session logs |
| Manual "check Synapse" prompts | 0/week | Logan observation |
| Average alert response time | < 5 min | Synapse timestamps |

### Technical Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Alert creation time | < 100ms | Benchmark |
| False positives | 0 | Bug reports |
| Duplicate alerts | 0 | Alert file analysis |

---

## 🛠️ TECHNICAL DETAILS

### Alert File Format

```json
{
  "agent": "ATLAS",
  "last_updated": "2026-01-22T12:00:00",
  "alert_count": 2,
  "unread_count": 1,
  "alerts": [
    {
      "id": "abc123",
      "timestamp": "2026-01-22T11:55:00",
      "from_agent": "FORGE",
      "to_agent": "ATLAS",
      "subject": "Review Required",
      "preview": "Please review...",
      "source_file": "/path/to/msg.json",
      "priority": "HIGH",
      "read": false
    }
  ]
}
```

### Import Paths

```python
# From SynapseNotify directory
from synapsenotify import SynapseNotify, Alert, Priority

# From another location
import sys
sys.path.insert(0, r'C:\Users\logan\OneDrive\Documents\AutoProjects\SynapseNotify')
from synapsenotify import SynapseNotify
```

---

## 📝 CREDITS

**Built by:** Atlas (Team Brain)  
**For:** Logan Smith / Metaphy LLC  
**Requested by:** Forge (Tool Request 2026-01-22)  
**Problem Statement:** "SynapseWatcher detects messages but cannot truly NOTIFY AI agents"  
**Part of:** Beacon HQ / Team Brain Ecosystem  
**Date:** January 22, 2026

---

**Last Updated:** January 22, 2026  
**Maintained By:** Atlas (Team Brain)
