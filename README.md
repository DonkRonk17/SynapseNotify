<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/e77d4c32-4334-45f5-80d9-9b2ade62a0a7" />

# 🔔 SynapseNotify v1.0

**Push Notification System for AI Agents**

True push notifications for Team Brain agents. When messages arrive in THE_SYNAPSE, SynapseNotify alerts agents automatically - no manual checking required!

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)
![Tests](https://img.shields.io/badge/tests-29%20passing-success.svg)

---

## 🚨 The Problem

When IRIS sends a message to FORGE via THE_SYNAPSE:

**Before SynapseNotify:**
1. IRIS sends message → Synapse file created
2. FORGE has no idea a message arrived
3. Logan must manually tell FORGE to "check Synapse"
4. FORGE finally reads the message (minutes/hours later)

**This defeats real-time coordination!**

---

## ✅ The Solution

**With SynapseNotify:**
1. IRIS sends message → Synapse file created
2. SynapseWatcher detects message → **Creates alert for FORGE**
3. FORGE session starts → **Automatically sees alert report**
4. Terminal bell rings (optional) for CLI agents
5. FORGE reads and responds immediately

**Real-time coordination achieved!**

---

## ✨ Features

- **File-Based Alerts** - Persistent alerts survive restarts
- **Session Start Check** - Agents see pending messages immediately
- **Terminal Bell** - Audio notification for CLI agents
- **Priority Support** - CRITICAL/HIGH/NORMAL/LOW filtering
- **Multi-Agent** - Works with all Team Brain agents
- **Broadcast Support** - TEAM_BRAIN messages reach everyone
- **No Duplicates** - Same message doesn't create multiple alerts
- **Zero Dependencies** - Pure Python standard library
- **Cross-Platform** - Windows, Linux, macOS

---

## 📦 Installation

### Option 1: Clone Repository
```bash
git clone https://github.com/DonkRonk17/SynapseNotify.git
cd SynapseNotify
python synapsenotify.py
```

### Option 2: Direct Download
```bash
curl -O https://raw.githubusercontent.com/DonkRonk17/SynapseNotify/main/synapsenotify.py
```

**Requirements:** Python 3.7+ (no external dependencies!)

---

## 🚀 Quick Start

### 1. Check Alerts at Session Start (Recommended)

**CLI:**
```bash
python synapsenotify.py check ATLAS
```

**Output:**
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
```

**Python API:**
```python
from synapsenotify import SynapseNotify

notifier = SynapseNotify()
report = notifier.check_and_report("ATLAS")
print(report)
```

### 2. Create Alert from Synapse Message

When SynapseWatcher detects a new message:

```bash
python synapsenotify.py alert /path/to/synapse_message.json
```

**Python API:**
```python
notifier = SynapseNotify()
notifier.create_alerts_from_synapse_message(message_path)
```

### 3. Clear Alerts After Reading

```bash
python synapsenotify.py clear ATLAS
```

---

## 💻 CLI Reference

```bash
# Check alerts at session start
synapsenotify.py check <agent>

# Get unread alert count
synapsenotify.py count <agent>

# List alerts (--all includes read)
synapsenotify.py list <agent> [--all]

# Mark alerts as read
synapsenotify.py read <agent> [alert_id]

# Clear alerts (--keep = keep unread)
synapsenotify.py clear <agent> [--keep]

# Create alerts from Synapse message
synapsenotify.py alert <message_file>

# Show all agents with pending alerts
synapsenotify.py status

# Test terminal bell
synapsenotify.py bell

# Sync TOOL_REQUEST_*.json to master log (for auto-prompt)
synapsenotify.py sync-requests

# Show pending tool requests
synapsenotify.py pending-requests
```

---

## 🐍 Python API

### Basic Usage

```python
from synapsenotify import SynapseNotify

# Initialize (uses default alerts directory)
notifier = SynapseNotify()

# Create alert manually
notifier.create_alert(
    to_agent="ATLAS",
    from_agent="FORGE",
    subject="Code Review Required",
    content="Please review the TokenTracker changes",
    source_file="/path/to/message.json",
    priority="HIGH"
)

# Check for alerts
alerts = notifier.get_alerts("ATLAS", unread_only=True)
for alert in alerts:
    print(f"From {alert.from_agent}: {alert.subject}")

# Mark as read
notifier.mark_read("ATLAS")

# Clear alerts
notifier.clear_alerts("ATLAS")
```

### Session Start Integration

Add to your agent's startup routine:

```python
from synapsenotify import SynapseNotify

def agent_session_start(agent_name):
    """Check for alerts at session start."""
    notifier = SynapseNotify()
    
    # Get alert count first
    count = notifier.get_alert_count(agent_name)
    
    if count > 0:
        # Print full report
        report = notifier.check_and_report(agent_name, bell=True)
        print(report)
        
        # Prompt to read original messages
        print("\n[!] Read the original messages in THE_SYNAPSE before continuing!")
        return True  # Has alerts
    
    print(f"[OK] No pending messages for {agent_name}")
    return False  # No alerts

# Usage
has_alerts = agent_session_start("ATLAS")
```

### SynapseWatcher Integration

Add to SynapseWatcher callback:

```python
from synapsenotify import SynapseNotify
from synapsewatcher import SynapseWatcher

def on_new_message(message_path):
    """Called when SynapseWatcher detects new message."""
    notifier = SynapseNotify()
    
    # Create alerts for all recipients
    alerts = notifier.create_alerts_from_synapse_message(message_path)
    
    print(f"[SynapseNotify] Created {len(alerts)} alert(s)")

# Set up watcher
watcher = SynapseWatcher(callback=on_new_message)
watcher.start()
```

---

## 👥 Supported Agents

| Agent | Type | Bell Support |
|-------|------|--------------|
| **FORGE** | Cursor IDE | ❌ (IDE) |
| **ATLAS** | Cursor IDE | ❌ (IDE) |
| **CLIO** | CLI/Terminal | ✅ |
| **NEXUS** | Multi-platform | ✅ (CLI mode) |
| **IRIS** | Cursor IDE | ❌ (IDE) |
| **PORTER** | Mobile | ❌ |
| **BOLT** | CLI | ✅ |
| **GEMINI** | Extension | ❌ |

---

## 📁 Alert Storage

Alerts are stored in JSON files per agent:

**Location:** `D:\BEACON_HQ\MEMORY_CORE_V2\03_INTER_AI_COMMS\AGENT_ALERTS\`

**Files:**
- `ATLAS_alerts.json`
- `FORGE_alerts.json`
- `CLIO_alerts.json`
- etc.

**Format:**
```json
{
  "agent": "ATLAS",
  "last_updated": "2026-01-22T12:00:00",
  "alert_count": 2,
  "unread_count": 1,
  "alerts": [
    {
      "id": "abc123def456",
      "timestamp": "2026-01-22T11:55:00",
      "from_agent": "FORGE",
      "to_agent": "ATLAS",
      "subject": "Code Review Required",
      "preview": "Please review the TokenTracker...",
      "source_file": "/path/to/message.json",
      "priority": "HIGH",
      "read": false
    }
  ]
}
```

---

## 🔗 Integration with SynapseWatcher

SynapseNotify is designed to work with SynapseWatcher:

```python
# synapse_monitor.py - Run in background
from synapsewatcher import SynapseWatcher
from synapsenotify import SynapseNotify

def handle_new_message(message_path):
    notifier = SynapseNotify()
    alerts = notifier.create_alerts_from_synapse_message(message_path)
    
    # Log for monitoring
    for alert in alerts:
        print(f"[ALERT] {alert.to_agent} <- {alert.from_agent}: {alert.subject}")

# Start watching
watcher = SynapseWatcher(
    synapse_path="D:/BEACON_HQ/MEMORY_CORE_V2/03_INTER_AI_COMMS/THE_SYNAPSE/active",
    callback=handle_new_message
)
watcher.watch(daemon=True)
```

---

## 🎯 Use Cases

### Case 1: Agent Session Start
```python
# Every agent session should start with:
from synapsenotify import SynapseNotify

notifier = SynapseNotify()
print(notifier.check_and_report("YOUR_AGENT"))
```

### Case 2: Monitoring Dashboard
```python
# See all agents with pending alerts
status = notifier.get_all_agents_status()
for agent, count in status.items():
    print(f"{agent}: {count} unread")
```

### Case 3: Priority Filtering
```python
# Only get CRITICAL alerts
critical = notifier.get_alerts("FORGE", priority="CRITICAL")
```

### Case 4: Automated Alert Clearing
```python
# Clear read alerts but keep unread
notifier.clear_alerts("ATLAS", keep_unread=True)
```

---

## 🐛 Troubleshooting

### Issue: "No alerts showing but messages exist"
**Solution:** Make sure SynapseWatcher is creating alerts via `create_alerts_from_synapse_message()`:
```bash
python synapsenotify.py alert /path/to/message.json
```

### Issue: "Bell not working"
**Solution:** Terminal bell depends on terminal emulator. Test with:
```bash
python synapsenotify.py bell
```

### Issue: "Alerts not persisting"
**Solution:** Check alerts directory permissions:
```bash
ls -la D:\BEACON_HQ\MEMORY_CORE_V2\03_INTER_AI_COMMS\AGENT_ALERTS\
```

### Issue: "Duplicate alerts"
**Solution:** SynapseNotify prevents duplicates based on source_file. If you see duplicates, the source files are different.

---

## 🛡️ Security Features

- ✅ **No code execution** - Only reads/writes JSON files
- ✅ **Path validation** - Source files paths are stored, not executed
- ✅ **Local only** - No network communication
- ✅ **Agent normalization** - Prevents injection via agent names

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a Pull Request

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/1b91b6c1-e3d2-4459-8c88-577b72d0db94" />


## 📝 Credits

**Built by:** Atlas (Team Brain)  
**For:** Logan Smith / Metaphy LLC  
**Requested by:** Forge (Tool Request 2026-01-22)  
**Problem:** "SynapseWatcher detects messages but cannot truly NOTIFY AI agents"  
**Part of:** Beacon HQ / Team Brain Ecosystem  
**Date:** January 22, 2026

---

## 🔄 Auto-Prompt Integration

SynapseNotify includes a **Tool Request Scanner** that syncs `TOOL_REQUEST_*.json` files from THE_SYNAPSE to `MASTER_TOOL_REQUEST_LOG.json`. This ensures the auto-prompt system (4 AM & 12 PM daily runs) finds and prioritizes tool requests.

### How It Works

1. Someone posts a `TOOL_REQUEST_*.json` file in THE_SYNAPSE
2. Auto-prompt runs `synapsenotify.py sync-requests` at startup
3. Tool request is added to `MASTER_TOOL_REQUEST_LOG.json` with status "PENDING"
4. Auto-prompt sees the PENDING request and builds it first (Priority 0)

### Manual Sync

```bash
# Sync tool requests from Synapse to master log
python synapsenotify.py sync-requests

# View pending tool requests
python synapsenotify.py pending-requests
```

### File Locations

- **Synapse Tool Requests:** `D:\BEACON_HQ\MEMORY_CORE_V2\03_INTER_AI_COMMS\THE_SYNAPSE\active\TOOL_REQUEST_*.json`
- **Master Log:** `D:\BEACON_HQ\MEMORY_CORE_V2\05_PROJECT_TRACKING\TOOL_REQUESTS\MASTER_TOOL_REQUEST_LOG.json`

---

## 🗺️ Roadmap

- [x] File-based alert system (v1.0)
- [x] Terminal bell support (v1.0)
- [ ] MCP Server for Cursor integration (v2.0)
- [ ] Desktop notifications via plyer (v2.1)
- [ ] BCH integration (v3.0)
- [ ] Webhook support for external systems (v3.1)

---

## 📞 Support

- **Issues:** https://github.com/DonkRonk17/SynapseNotify/issues
- **Synapse:** Post in THE_SYNAPSE/active/
- **Direct:** Message ATLAS

---

**Built with ❤️ by Team Brain - Solving the real-time AI coordination challenge!**
