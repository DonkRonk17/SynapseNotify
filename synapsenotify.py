#!/usr/bin/env python3
"""
SynapseNotify v1.0 - Push Notification System for AI Agents

True push notifications for Team Brain agents. When messages arrive in
THE_SYNAPSE, SynapseNotify can:
1. Write alerts to agent-specific files for session-start checking
2. Trigger terminal bells (audio) for CLI agents
3. Provide a simple API for agents to check their pending notifications

Zero dependencies - pure Python standard library.
Cross-platform - Windows, Linux, macOS.

Author: Atlas (Team Brain)
For: Logan Smith / Metaphy LLC
Requested by: Forge (Tool Request 2026-01-22)
License: MIT
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

__version__ = "1.0.0"


class Priority(Enum):
    """Alert priority levels."""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    """Represents a single notification alert."""
    id: str
    timestamp: str
    from_agent: str
    to_agent: str
    subject: str
    preview: str
    source_file: str
    priority: str
    read: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Alert':
        """Create from dictionary."""
        return cls(**data)


class SynapseNotify:
    """
    Push notification system for AI agents.
    
    Features:
    - Write alerts to agent-specific files
    - Read pending alerts at session start
    - Mark alerts as read/clear them
    - Terminal bell support for CLI agents
    - Priority-based filtering
    
    Example:
        >>> notifier = SynapseNotify()
        >>> # Check for alerts at session start
        >>> alerts = notifier.get_alerts("ATLAS")
        >>> for alert in alerts:
        ...     print(f"From {alert.from_agent}: {alert.subject}")
        >>> notifier.clear_alerts("ATLAS")
    """
    
    # Default alerts directory (can be overridden)
    DEFAULT_ALERTS_DIR = Path(r"D:\BEACON_HQ\MEMORY_CORE_V2\03_INTER_AI_COMMS\AGENT_ALERTS")
    
    # Known agents in Team Brain
    KNOWN_AGENTS = [
        "FORGE", "ATLAS", "CLIO", "NEXUS", "BOLT", "GEMINI",
        "IRIS", "PORTER", "LOGAN", "LOGAN_SMITH", "ALL", "TEAM_BRAIN"
    ]
    
    def __init__(self, alerts_dir: Optional[Path] = None, enable_bell: bool = True):
        """
        Initialize SynapseNotify.
        
        Args:
            alerts_dir: Directory for alert files (default: AGENT_ALERTS in Memory Core)
            enable_bell: Whether to trigger terminal bell on new alerts
        """
        self.alerts_dir = Path(alerts_dir) if alerts_dir else self.DEFAULT_ALERTS_DIR
        self.enable_bell = enable_bell
        self._ensure_alerts_dir()
    
    def _ensure_alerts_dir(self) -> None:
        """Create alerts directory if it doesn't exist."""
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_alert_file(self, agent: str) -> Path:
        """Get path to agent's alert file."""
        agent_clean = agent.upper().replace(" ", "_")
        return self.alerts_dir / f"{agent_clean}_alerts.json"
    
    def _load_alerts(self, agent: str) -> List[Alert]:
        """Load alerts from agent's file."""
        alert_file = self._get_alert_file(agent)
        
        if not alert_file.exists():
            return []
        
        try:
            with open(alert_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Alert.from_dict(a) for a in data.get('alerts', [])]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[WARNING] Error reading alerts for {agent}: {e}")
            return []
    
    def _save_alerts(self, agent: str, alerts: List[Alert]) -> None:
        """Save alerts to agent's file."""
        alert_file = self._get_alert_file(agent)
        
        data = {
            "agent": agent.upper(),
            "last_updated": datetime.now().isoformat(),
            "alert_count": len(alerts),
            "unread_count": len([a for a in alerts if not a.read]),
            "alerts": [a.to_dict() for a in alerts]
        }
        
        with open(alert_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _trigger_bell(self) -> None:
        """Trigger terminal bell if enabled."""
        if self.enable_bell:
            # Print bell character (works on most terminals)
            print('\a', end='', flush=True)
    
    def _safe_str(self, text: str) -> str:
        """Make string safe for Windows console output."""
        try:
            text.encode('cp1252')
            return text
        except UnicodeEncodeError:
            # Replace non-printable chars with ASCII equivalent
            return text.encode('ascii', 'replace').decode('ascii')
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        import hashlib
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _extract_preview(self, content: Union[str, Dict]) -> str:
        """Extract preview text from message content."""
        if isinstance(content, str):
            preview = content[:100]
        elif isinstance(content, dict):
            # Try to get announcement or first text field
            preview = content.get('announcement', 
                     content.get('message', 
                     content.get('summary', 
                     str(content)[:100])))
        else:
            preview = str(content)[:100]
        
        if len(preview) >= 100:
            preview = preview[:97] + "..."
        
        return preview
    
    def create_alert(
        self,
        to_agent: str,
        from_agent: str,
        subject: str,
        content: Union[str, Dict],
        source_file: str,
        priority: str = "NORMAL"
    ) -> Alert:
        """
        Create a new alert for an agent.
        
        Args:
            to_agent: Target agent (FORGE, ATLAS, CLIO, etc.)
            from_agent: Source agent who sent the message
            subject: Message subject/title
            content: Message content (for preview)
            source_file: Path to original Synapse message file
            priority: Alert priority (LOW, NORMAL, HIGH, CRITICAL)
        
        Returns:
            Created Alert object
        """
        # Normalize agent names
        to_agent = to_agent.upper().replace("CURSOR_", "").replace("CLI_", "")
        from_agent = from_agent.upper().replace("CURSOR_", "").replace("CLI_", "")
        
        # Validate priority
        try:
            priority = Priority(priority.upper()).value
        except ValueError:
            priority = Priority.NORMAL.value
        
        alert = Alert(
            id=self._generate_alert_id(),
            timestamp=datetime.now().isoformat(),
            from_agent=from_agent,
            to_agent=to_agent,
            subject=subject,
            preview=self._extract_preview(content),
            source_file=str(source_file),
            priority=priority,
            read=False
        )
        
        # Load existing alerts
        alerts = self._load_alerts(to_agent)
        
        # Check for duplicate (same source file)
        existing_ids = {a.source_file for a in alerts}
        if source_file in existing_ids:
            print(f"[INFO] Alert already exists for {source_file}")
            return alert
        
        # Add new alert
        alerts.append(alert)
        
        # Save
        self._save_alerts(to_agent, alerts)
        
        # Trigger bell
        self._trigger_bell()
        
        # Safe print (handle Windows console encoding)
        try:
            print(f"[OK] Alert created for {to_agent} from {from_agent}: {subject}")
        except UnicodeEncodeError:
            # Strip non-ASCII for console output
            safe_subject = subject.encode('ascii', 'replace').decode('ascii')
            print(f"[OK] Alert created for {to_agent} from {from_agent}: {safe_subject}")
        
        return alert
    
    def create_alerts_from_synapse_message(self, message_path: Path) -> List[Alert]:
        """
        Parse a Synapse message file and create alerts for all recipients.
        
        Args:
            message_path: Path to Synapse JSON message file
        
        Returns:
            List of created alerts
        """
        try:
            with open(message_path, 'r', encoding='utf-8') as f:
                msg = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"[ERROR] Failed to read message: {e}")
            return []
        
        # Extract recipients
        to_list = msg.get('to', [])
        if isinstance(to_list, str):
            to_list = [to_list]
        
        # Add CC recipients
        cc_list = msg.get('cc', [])
        if isinstance(cc_list, str):
            cc_list = [cc_list]
        to_list.extend(cc_list)
        
        # Get message details
        from_agent = msg.get('from', 'UNKNOWN')
        subject = msg.get('subject', 'No Subject')
        body = msg.get('body', msg.get('content', ''))
        priority = msg.get('priority', 'NORMAL')
        
        created_alerts = []
        
        for recipient in to_list:
            # Skip broadcast aliases for individual alerts
            if recipient.upper() in ['ALL', 'TEAM_BRAIN']:
                # Create alerts for all known agents
                for agent in ['FORGE', 'ATLAS', 'CLIO', 'NEXUS', 'IRIS', 'PORTER']:
                    alert = self.create_alert(
                        to_agent=agent,
                        from_agent=from_agent,
                        subject=subject,
                        content=body,
                        source_file=str(message_path),
                        priority=priority
                    )
                    created_alerts.append(alert)
            else:
                alert = self.create_alert(
                    to_agent=recipient,
                    from_agent=from_agent,
                    subject=subject,
                    content=body,
                    source_file=str(message_path),
                    priority=priority
                )
                created_alerts.append(alert)
        
        return created_alerts
    
    def get_alerts(
        self,
        agent: str,
        unread_only: bool = False,
        priority: Optional[str] = None
    ) -> List[Alert]:
        """
        Get alerts for an agent.
        
        Args:
            agent: Agent name to get alerts for
            unread_only: Only return unread alerts
            priority: Filter by priority level
        
        Returns:
            List of Alert objects
        """
        alerts = self._load_alerts(agent)
        
        if unread_only:
            alerts = [a for a in alerts if not a.read]
        
        if priority:
            alerts = [a for a in alerts if a.priority == priority.upper()]
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda a: a.timestamp, reverse=True)
        
        return alerts
    
    def get_alert_count(self, agent: str, unread_only: bool = True) -> int:
        """Get count of alerts for an agent."""
        alerts = self.get_alerts(agent, unread_only=unread_only)
        return len(alerts)
    
    def mark_read(self, agent: str, alert_id: Optional[str] = None) -> int:
        """
        Mark alerts as read.
        
        Args:
            agent: Agent name
            alert_id: Specific alert ID (None = mark all as read)
        
        Returns:
            Number of alerts marked as read
        """
        alerts = self._load_alerts(agent)
        count = 0
        
        for alert in alerts:
            should_mark = (alert_id is None) or (alert.id == alert_id)
            if should_mark and not alert.read:
                alert.read = True
                count += 1
                # If we were targeting a specific alert and found it, stop
                if alert_id is not None:
                    break
        
        self._save_alerts(agent, alerts)
        
        if count > 0:
            print(f"[OK] Marked {count} alert(s) as read for {agent}")
        
        return count
    
    def clear_alerts(self, agent: str, keep_unread: bool = False) -> int:
        """
        Clear alerts for an agent.
        
        Args:
            agent: Agent name
            keep_unread: If True, only clear read alerts
        
        Returns:
            Number of alerts cleared
        """
        alerts = self._load_alerts(agent)
        original_count = len(alerts)
        
        if keep_unread:
            alerts = [a for a in alerts if not a.read]
        else:
            alerts = []
        
        cleared_count = original_count - len(alerts)
        
        self._save_alerts(agent, alerts)
        
        if cleared_count > 0:
            print(f"[OK] Cleared {cleared_count} alert(s) for {agent}")
        
        return cleared_count
    
    def check_and_report(self, agent: str, bell: bool = True) -> str:
        """
        Check alerts and return a formatted report for session start.
        
        Args:
            agent: Agent name
            bell: Whether to trigger bell if alerts exist
        
        Returns:
            Formatted report string
        """
        alerts = self.get_alerts(agent, unread_only=True)
        
        if not alerts:
            return f"[OK] No new messages for {agent}"
        
        # Trigger bell if there are alerts
        if bell and self.enable_bell:
            self._trigger_bell()
        
        # Build report
        lines = []
        lines.append("=" * 60)
        lines.append(f"[!] {len(alerts)} NEW MESSAGE(S) FOR {agent}")
        lines.append("=" * 60)
        lines.append("")
        
        # Group by priority
        critical = [a for a in alerts if a.priority == 'CRITICAL']
        high = [a for a in alerts if a.priority == 'HIGH']
        normal = [a for a in alerts if a.priority in ['NORMAL', 'LOW']]
        
        if critical:
            lines.append("[!!!] CRITICAL MESSAGES:")
            for alert in critical:
                lines.append(f"  From: {alert.from_agent}")
                lines.append(f"  Subject: {self._safe_str(alert.subject)}")
                lines.append(f"  Preview: {self._safe_str(alert.preview)}")
                lines.append(f"  File: {alert.source_file}")
                lines.append("")
        
        if high:
            lines.append("[!] HIGH PRIORITY:")
            for alert in high:
                lines.append(f"  From: {alert.from_agent} - {self._safe_str(alert.subject)}")
                lines.append(f"  Preview: {self._safe_str(alert.preview[:50])}...")
                lines.append("")
        
        if normal:
            lines.append("[i] NORMAL MESSAGES:")
            for alert in normal:
                lines.append(f"  From: {alert.from_agent} - {self._safe_str(alert.subject)}")
            lines.append("")
        
        lines.append("=" * 60)
        lines.append("Run: synapsenotify read <agent> - to mark all as read")
        lines.append("Run: synapsenotify clear <agent> - to clear alerts")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def get_all_agents_status(self) -> Dict[str, int]:
        """Get alert count for all known agents."""
        status = {}
        for agent in self.KNOWN_AGENTS:
            if agent not in ['ALL', 'TEAM_BRAIN', 'LOGAN', 'LOGAN_SMITH']:
                count = self.get_alert_count(agent, unread_only=True)
                if count > 0:
                    status[agent] = count
        return status


class ToolRequestScanner:
    """
    Scans THE_SYNAPSE for TOOL_REQUEST_*.json files and syncs them
    to MASTER_TOOL_REQUEST_LOG.json for auto-prompt detection.
    """
    
    SYNAPSE_PATH = Path(r"D:\BEACON_HQ\MEMORY_CORE_V2\03_INTER_AI_COMMS\THE_SYNAPSE\active")
    TOOL_REQUEST_LOG = Path(r"D:\BEACON_HQ\MEMORY_CORE_V2\05_PROJECT_TRACKING\TOOL_REQUESTS\MASTER_TOOL_REQUEST_LOG.json")
    
    def scan_and_sync(self) -> int:
        """
        Scan Synapse for TOOL_REQUEST_*.json files and add to master log.
        
        Returns:
            Number of new pending requests added
        """
        # Find all TOOL_REQUEST_*.json files
        tool_request_files = list(self.SYNAPSE_PATH.glob("TOOL_REQUEST_*.json"))
        
        if not tool_request_files:
            print("[OK] No tool request files found in Synapse")
            return 0
        
        # Load master log
        try:
            with open(self.TOOL_REQUEST_LOG, 'r', encoding='utf-8') as f:
                master_log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create new log structure
            master_log = {
                "tracking_info": {
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "responsible_agents": ["ATLAS", "FORGE", "CLIO"],
                    "description": "Master tracking log for all tool requests"
                },
                "active_requests": [],
                "completed_requests": [],
                "statistics": {
                    "total_requests": 0,
                    "pending": 0,
                    "in_progress": 0,
                    "completed": 0,
                    "cancelled": 0
                }
            }
        
        # Get existing request IDs (from both active and completed)
        existing_msg_ids = set()
        for req in master_log.get('active_requests', []):
            existing_msg_ids.add(req.get('synapse_message_id', ''))
        for req in master_log.get('completed_requests', []):
            existing_msg_ids.add(req.get('synapse_message_id', ''))
        
        new_requests = 0
        
        for request_file in tool_request_files:
            try:
                with open(request_file, 'r', encoding='utf-8') as f:
                    request = json.load(f)
                
                msg_id = request.get('msg_id', request_file.stem)
                
                # Skip if already in log
                if msg_id in existing_msg_ids:
                    continue
                
                # Extract request details
                body = request.get('body', {})
                
                new_entry = {
                    "request_id": master_log['statistics'].get('total_requests', 0) + new_requests + 1,
                    "date_received": request.get('timestamp', datetime.now().isoformat()),
                    "requested_by": request.get('from', 'UNKNOWN'),
                    "synapse_message_id": msg_id,
                    "tool_name": body.get('tool_name', request.get('subject', 'Unknown Tool')),
                    "purpose": body.get('problem_statement', body.get('purpose', 'See Synapse message')),
                    "priority": request.get('priority', 'NORMAL'),
                    "details": str(body)[:500] if body else "See original Synapse message",
                    "use_cases": body.get('success_criteria', body.get('use_cases', [])),
                    "status": "PENDING",
                    "assigned_to": None,
                    "date_assigned": None,
                    "date_completed": None,
                    "github_url": None,
                    "notes": f"Auto-imported from Synapse: {request_file.name}",
                    "source_file": str(request_file)
                }
                
                # Add to active requests
                if 'active_requests' not in master_log:
                    master_log['active_requests'] = []
                master_log['active_requests'].append(new_entry)
                
                new_requests += 1
                print(f"[OK] Added PENDING tool request: {new_entry['tool_name']}")
                
            except Exception as e:
                print(f"[WARNING] Could not process {request_file.name}: {e}")
        
        # Update statistics
        if new_requests > 0:
            master_log['statistics']['total_requests'] = master_log['statistics'].get('total_requests', 0) + new_requests
            master_log['statistics']['pending'] = len([r for r in master_log.get('active_requests', []) if r.get('status') == 'PENDING'])
            master_log['tracking_info']['last_updated'] = datetime.now().isoformat()
            
            # Save updated log
            with open(self.TOOL_REQUEST_LOG, 'w', encoding='utf-8') as f:
                json.dump(master_log, f, indent=2, ensure_ascii=False)
            
            print(f"[OK] Synced {new_requests} new tool request(s) to MASTER_TOOL_REQUEST_LOG.json")
        else:
            print("[OK] All Synapse tool requests already in master log")
        
        return new_requests
    
    def get_pending_requests(self) -> List[Dict]:
        """Get all pending tool requests."""
        try:
            with open(self.TOOL_REQUEST_LOG, 'r', encoding='utf-8') as f:
                master_log = json.load(f)
            
            return [r for r in master_log.get('active_requests', []) if r.get('status') == 'PENDING']
        except:
            return []


def main():
    """CLI interface for SynapseNotify."""
    
    if len(sys.argv) < 2:
        print("""
SynapseNotify v1.0 - Push Notification System for AI Agents

USAGE:
  synapsenotify.py check <agent>              Check and report alerts for agent
  synapsenotify.py count <agent>              Get unread alert count
  synapsenotify.py list <agent> [--all]       List alerts (--all = include read)
  synapsenotify.py read <agent> [alert_id]    Mark alert(s) as read
  synapsenotify.py clear <agent> [--keep]     Clear alerts (--keep = keep unread)
  synapsenotify.py alert <file>               Create alerts from Synapse message
  synapsenotify.py status                     Show all agents with pending alerts
  synapsenotify.py bell                       Test terminal bell
  synapsenotify.py sync-requests              Sync TOOL_REQUEST_*.json to master log
  synapsenotify.py pending-requests           Show pending tool requests

EXAMPLES:
  # Check alerts at session start (recommended)
  python synapsenotify.py check ATLAS
  
  # Create alert from Synapse message file
  python synapsenotify.py alert message.json
  
  # Clear alerts after reading original messages
  python synapsenotify.py clear ATLAS
  
  # See which agents have pending alerts
  python synapsenotify.py status

AGENTS: FORGE, ATLAS, CLIO, NEXUS, BOLT, IRIS, PORTER, GEMINI

INTEGRATION:
  Add to agent session start:
  ```python
  from synapsenotify import SynapseNotify
  notifier = SynapseNotify()
  print(notifier.check_and_report("YOUR_AGENT"))
  ```
""")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    notifier = SynapseNotify()
    
    if command == "check":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: synapsenotify.py check <agent>")
            sys.exit(1)
        
        agent = sys.argv[2].upper()
        report = notifier.check_and_report(agent)
        print(report)
    
    elif command == "count":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: synapsenotify.py count <agent>")
            sys.exit(1)
        
        agent = sys.argv[2].upper()
        count = notifier.get_alert_count(agent)
        print(f"{count}")
    
    elif command == "list":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: synapsenotify.py list <agent> [--all]")
            sys.exit(1)
        
        agent = sys.argv[2].upper()
        unread_only = "--all" not in sys.argv
        
        alerts = notifier.get_alerts(agent, unread_only=unread_only)
        
        if not alerts:
            print(f"No {'unread ' if unread_only else ''}alerts for {agent}")
        else:
            print(f"\n{'Unread a' if unread_only else 'A'}lerts for {agent}:\n")
            for alert in alerts:
                status = "[NEW]" if not alert.read else "[READ]"
                print(f"  {status} [{alert.priority}] From {alert.from_agent}: {alert.subject}")
                print(f"       ID: {alert.id} | {alert.timestamp}")
                print(f"       File: {alert.source_file}")
                print()
    
    elif command == "read":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: synapsenotify.py read <agent> [alert_id]")
            sys.exit(1)
        
        agent = sys.argv[2].upper()
        alert_id = sys.argv[3] if len(sys.argv) > 3 else None
        
        count = notifier.mark_read(agent, alert_id)
        if count == 0:
            print(f"No alerts to mark as read for {agent}")
    
    elif command == "clear":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: synapsenotify.py clear <agent> [--keep]")
            sys.exit(1)
        
        agent = sys.argv[2].upper()
        keep_unread = "--keep" in sys.argv
        
        count = notifier.clear_alerts(agent, keep_unread=keep_unread)
        if count == 0:
            print(f"No alerts to clear for {agent}")
    
    elif command == "alert":
        if len(sys.argv) < 3:
            print("[ERROR] Usage: synapsenotify.py alert <message_file>")
            sys.exit(1)
        
        message_path = Path(sys.argv[2])
        if not message_path.exists():
            print(f"[ERROR] File not found: {message_path}")
            sys.exit(1)
        
        alerts = notifier.create_alerts_from_synapse_message(message_path)
        print(f"[OK] Created {len(alerts)} alert(s) from {message_path.name}")
    
    elif command == "status":
        status = notifier.get_all_agents_status()
        
        if not status:
            print("[OK] No pending alerts for any agent")
        else:
            print("\nAgents with pending alerts:\n")
            for agent, count in sorted(status.items(), key=lambda x: -x[1]):
                print(f"  {agent}: {count} unread")
            print()
    
    elif command == "bell":
        print("Testing terminal bell...")
        notifier._trigger_bell()
        print("[OK] Bell triggered (did you hear it?)")
    
    elif command == "sync-requests":
        scanner = ToolRequestScanner()
        count = scanner.scan_and_sync()
        if count > 0:
            print(f"\n[!] {count} new tool request(s) added to master log!")
            print("[!] Auto-prompt will now find these requests")
    
    elif command == "pending-requests":
        scanner = ToolRequestScanner()
        pending = scanner.get_pending_requests()
        
        if not pending:
            print("[OK] No pending tool requests")
        else:
            print(f"\n[!] {len(pending)} PENDING TOOL REQUEST(S):\n")
            for req in pending:
                print(f"  [{req.get('priority', 'NORMAL')}] {req.get('tool_name', 'Unknown')}")
                print(f"       From: {req.get('requested_by', 'Unknown')}")
                print(f"       Purpose: {req.get('purpose', 'N/A')[:80]}...")
                print(f"       ID: {req.get('synapse_message_id', 'N/A')}")
                print()
    
    else:
        print(f"[ERROR] Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
