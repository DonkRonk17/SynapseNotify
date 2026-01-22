#!/usr/bin/env python3
"""
Comprehensive Test Suite for SynapseNotify v1.0

Tests cover:
- Alert creation and storage
- Alert retrieval and filtering
- Mark read and clear operations
- Synapse message parsing
- Edge cases and validation

Run: python test_synapsenotify.py

Author: Atlas (Team Brain)
For: Logan Smith / Metaphy LLC
Date: January 22, 2026
"""

import unittest
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from synapsenotify import SynapseNotify, Alert, Priority


class TestSynapseNotifyCore(unittest.TestCase):
    """Test core SynapseNotify functionality."""
    
    def setUp(self):
        """Set up test fixtures with isolated alerts directory."""
        self.test_dir = tempfile.mkdtemp()
        self.alerts_dir = Path(self.test_dir) / "alerts"
        self.notifier = SynapseNotify(alerts_dir=self.alerts_dir, enable_bell=False)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test SynapseNotify initializes correctly."""
        self.assertIsNotNone(self.notifier)
        self.assertTrue(self.alerts_dir.exists())
    
    def test_create_alert_basic(self):
        """Test basic alert creation."""
        alert = self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="FORGE",
            subject="Test Message",
            content="This is a test message",
            source_file="/path/to/message.json",
            priority="NORMAL"
        )
        
        self.assertIsNotNone(alert)
        self.assertEqual(alert.to_agent, "ATLAS")
        self.assertEqual(alert.from_agent, "FORGE")
        self.assertEqual(alert.subject, "Test Message")
        self.assertFalse(alert.read)
    
    def test_create_alert_normalizes_agent_names(self):
        """Test that agent names are normalized."""
        alert = self.notifier.create_alert(
            to_agent="CURSOR_FORGE",
            from_agent="CLI_CLIO",
            subject="Test",
            content="Test",
            source_file="/test.json"
        )
        
        self.assertEqual(alert.to_agent, "FORGE")
        self.assertEqual(alert.from_agent, "CLIO")
    
    def test_create_alert_saves_to_file(self):
        """Test that alerts are saved to disk."""
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="FORGE",
            subject="Test",
            content="Test content",
            source_file="/test.json"
        )
        
        alert_file = self.alerts_dir / "ATLAS_alerts.json"
        self.assertTrue(alert_file.exists())
        
        with open(alert_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['agent'], "ATLAS")
        self.assertEqual(len(data['alerts']), 1)
    
    def test_get_alerts_empty(self):
        """Test getting alerts when none exist."""
        alerts = self.notifier.get_alerts("ATLAS")
        self.assertEqual(len(alerts), 0)
    
    def test_get_alerts_returns_created_alerts(self):
        """Test getting alerts after creation."""
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="FORGE",
            subject="First",
            content="First message",
            source_file="/first.json"
        )
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="CLIO",
            subject="Second",
            content="Second message",
            source_file="/second.json"
        )
        
        alerts = self.notifier.get_alerts("ATLAS")
        
        self.assertEqual(len(alerts), 2)
        # Check both subjects exist (order may vary due to timestamp precision)
        subjects = {a.subject for a in alerts}
        self.assertIn("First", subjects)
        self.assertIn("Second", subjects)
    
    def test_get_alerts_unread_only(self):
        """Test filtering for unread alerts only."""
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="FORGE",
            subject="Unread",
            content="Test",
            source_file="/unread.json"
        )
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="CLIO",
            subject="Will be read",
            content="Test",
            source_file="/read.json"
        )
        
        # Mark one as read
        alerts = self.notifier.get_alerts("ATLAS")
        self.notifier.mark_read("ATLAS", alerts[0].id)
        
        # Get unread only
        unread = self.notifier.get_alerts("ATLAS", unread_only=True)
        
        self.assertEqual(len(unread), 1)
        self.assertEqual(unread[0].subject, "Unread")
    
    def test_get_alerts_by_priority(self):
        """Test filtering alerts by priority."""
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="FORGE",
            subject="Critical",
            content="Test",
            source_file="/critical.json",
            priority="CRITICAL"
        )
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="CLIO",
            subject="Normal",
            content="Test",
            source_file="/normal.json",
            priority="NORMAL"
        )
        
        critical = self.notifier.get_alerts("ATLAS", priority="CRITICAL")
        
        self.assertEqual(len(critical), 1)
        self.assertEqual(critical[0].subject, "Critical")
    
    def test_get_alert_count(self):
        """Test alert count functionality."""
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="FORGE",
            subject="Test1",
            content="Test",
            source_file="/test1.json"
        )
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="CLIO",
            subject="Test2",
            content="Test",
            source_file="/test2.json"
        )
        
        count = self.notifier.get_alert_count("ATLAS")
        self.assertEqual(count, 2)


class TestSynapseNotifyOperations(unittest.TestCase):
    """Test alert operations (mark read, clear)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.alerts_dir = Path(self.test_dir) / "alerts"
        self.notifier = SynapseNotify(alerts_dir=self.alerts_dir, enable_bell=False)
        
        # Create some test alerts
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="FORGE",
            subject="First",
            content="First message",
            source_file="/first.json"
        )
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="CLIO",
            subject="Second",
            content="Second message",
            source_file="/second.json"
        )
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_mark_read_single(self):
        """Test marking a single alert as read."""
        alerts = self.notifier.get_alerts("ATLAS")
        alert_id = alerts[0].id
        
        count = self.notifier.mark_read("ATLAS", alert_id)
        
        self.assertEqual(count, 1)
        
        # Verify alert is marked read
        updated_alerts = self.notifier.get_alerts("ATLAS")
        read_alert = next(a for a in updated_alerts if a.id == alert_id)
        self.assertTrue(read_alert.read)
    
    def test_mark_read_all(self):
        """Test marking all alerts as read."""
        count = self.notifier.mark_read("ATLAS")
        
        self.assertEqual(count, 2)
        
        # All should be read
        unread = self.notifier.get_alerts("ATLAS", unread_only=True)
        self.assertEqual(len(unread), 0)
    
    def test_clear_alerts_all(self):
        """Test clearing all alerts."""
        count = self.notifier.clear_alerts("ATLAS")
        
        self.assertEqual(count, 2)
        
        # Should be empty
        alerts = self.notifier.get_alerts("ATLAS")
        self.assertEqual(len(alerts), 0)
    
    def test_clear_alerts_keep_unread(self):
        """Test clearing only read alerts."""
        # Mark one as read
        alerts = self.notifier.get_alerts("ATLAS")
        self.notifier.mark_read("ATLAS", alerts[0].id)
        
        # Clear with keep_unread
        count = self.notifier.clear_alerts("ATLAS", keep_unread=True)
        
        self.assertEqual(count, 1)
        
        # One unread should remain
        remaining = self.notifier.get_alerts("ATLAS")
        self.assertEqual(len(remaining), 1)
        self.assertFalse(remaining[0].read)


class TestSynapseNotifyMessageParsing(unittest.TestCase):
    """Test parsing Synapse message files."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.alerts_dir = Path(self.test_dir) / "alerts"
        self.messages_dir = Path(self.test_dir) / "messages"
        self.messages_dir.mkdir(parents=True, exist_ok=True)
        self.notifier = SynapseNotify(alerts_dir=self.alerts_dir, enable_bell=False)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_test_message(self, filename: str, to: list, from_agent: str, subject: str) -> Path:
        """Helper to create a test Synapse message file."""
        message_path = self.messages_dir / filename
        
        message = {
            "schema_version": "1.0",
            "msg_id": f"test_{filename}",
            "from": from_agent,
            "to": to,
            "priority": "NORMAL",
            "subject": subject,
            "body": {
                "announcement": f"This is {subject}",
                "content": "Test content here"
            }
        }
        
        with open(message_path, 'w', encoding='utf-8') as f:
            json.dump(message, f)
        
        return message_path
    
    def test_parse_single_recipient(self):
        """Test parsing message with single recipient."""
        msg_path = self._create_test_message(
            "test1.json",
            to=["ATLAS"],
            from_agent="FORGE",
            subject="Single Recipient"
        )
        
        alerts = self.notifier.create_alerts_from_synapse_message(msg_path)
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].to_agent, "ATLAS")
        self.assertEqual(alerts[0].from_agent, "FORGE")
    
    def test_parse_multiple_recipients(self):
        """Test parsing message with multiple recipients."""
        msg_path = self._create_test_message(
            "test2.json",
            to=["ATLAS", "CLIO", "NEXUS"],
            from_agent="FORGE",
            subject="Multiple Recipients"
        )
        
        alerts = self.notifier.create_alerts_from_synapse_message(msg_path)
        
        self.assertEqual(len(alerts), 3)
        agents = {a.to_agent for a in alerts}
        self.assertEqual(agents, {"ATLAS", "CLIO", "NEXUS"})
    
    def test_parse_team_brain_broadcast(self):
        """Test parsing message to TEAM_BRAIN (broadcast)."""
        msg_path = self._create_test_message(
            "broadcast.json",
            to=["TEAM_BRAIN"],
            from_agent="FORGE",
            subject="Broadcast Message"
        )
        
        alerts = self.notifier.create_alerts_from_synapse_message(msg_path)
        
        # Should create alerts for all known agents
        self.assertGreater(len(alerts), 1)
        agents = {a.to_agent for a in alerts}
        self.assertIn("ATLAS", agents)
        self.assertIn("FORGE", agents)
        self.assertIn("CLIO", agents)
    
    def test_parse_handles_cc(self):
        """Test that CC recipients also get alerts."""
        message_path = self.messages_dir / "cc_test.json"
        
        message = {
            "from": "FORGE",
            "to": ["ATLAS"],
            "cc": ["CLIO", "NEXUS"],
            "subject": "With CC",
            "body": "Test"
        }
        
        with open(message_path, 'w') as f:
            json.dump(message, f)
        
        alerts = self.notifier.create_alerts_from_synapse_message(message_path)
        
        self.assertEqual(len(alerts), 3)
        agents = {a.to_agent for a in alerts}
        self.assertEqual(agents, {"ATLAS", "CLIO", "NEXUS"})
    
    def test_no_duplicate_alerts(self):
        """Test that parsing same message twice doesn't create duplicates."""
        msg_path = self._create_test_message(
            "nodupe.json",
            to=["ATLAS"],
            from_agent="FORGE",
            subject="No Duplicates"
        )
        
        # Parse twice
        alerts1 = self.notifier.create_alerts_from_synapse_message(msg_path)
        alerts2 = self.notifier.create_alerts_from_synapse_message(msg_path)
        
        # Should only have 1 alert total
        all_alerts = self.notifier.get_alerts("ATLAS")
        self.assertEqual(len(all_alerts), 1)


class TestSynapseNotifyEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.alerts_dir = Path(self.test_dir) / "alerts"
        self.notifier = SynapseNotify(alerts_dir=self.alerts_dir, enable_bell=False)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_invalid_priority_defaults_to_normal(self):
        """Test that invalid priority defaults to NORMAL."""
        alert = self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="FORGE",
            subject="Test",
            content="Test",
            source_file="/test.json",
            priority="INVALID"
        )
        
        self.assertEqual(alert.priority, "NORMAL")
    
    def test_long_content_truncated(self):
        """Test that long content is truncated for preview."""
        long_content = "x" * 200
        
        alert = self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="FORGE",
            subject="Test",
            content=long_content,
            source_file="/test.json"
        )
        
        self.assertLessEqual(len(alert.preview), 100)
        self.assertTrue(alert.preview.endswith("..."))
    
    def test_dict_content_extracts_announcement(self):
        """Test that dict content extracts announcement field."""
        content = {
            "announcement": "This is the announcement",
            "other_field": "Other data"
        }
        
        alert = self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="FORGE",
            subject="Test",
            content=content,
            source_file="/test.json"
        )
        
        self.assertEqual(alert.preview, "This is the announcement")
    
    def test_get_alerts_nonexistent_agent(self):
        """Test getting alerts for agent with no alert file."""
        alerts = self.notifier.get_alerts("NONEXISTENT")
        self.assertEqual(len(alerts), 0)
    
    def test_mark_read_nonexistent_agent(self):
        """Test marking read for agent with no alerts."""
        count = self.notifier.mark_read("NONEXISTENT")
        self.assertEqual(count, 0)
    
    def test_clear_alerts_nonexistent_agent(self):
        """Test clearing alerts for agent with no alerts."""
        count = self.notifier.clear_alerts("NONEXISTENT")
        self.assertEqual(count, 0)
    
    def test_check_and_report_no_alerts(self):
        """Test check_and_report with no alerts."""
        report = self.notifier.check_and_report("ATLAS", bell=False)
        self.assertIn("No new messages", report)
    
    def test_check_and_report_with_alerts(self):
        """Test check_and_report with alerts."""
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="FORGE",
            subject="Important Message",
            content="Test content",
            source_file="/test.json",
            priority="HIGH"
        )
        
        report = self.notifier.check_and_report("ATLAS", bell=False)
        
        self.assertIn("NEW MESSAGE(S)", report)
        self.assertIn("FORGE", report)
        self.assertIn("Important Message", report)
        self.assertIn("HIGH PRIORITY", report)
    
    def test_get_all_agents_status(self):
        """Test getting status across all agents."""
        self.notifier.create_alert(
            to_agent="ATLAS",
            from_agent="FORGE",
            subject="Test",
            content="Test",
            source_file="/test1.json"
        )
        self.notifier.create_alert(
            to_agent="CLIO",
            from_agent="FORGE",
            subject="Test",
            content="Test",
            source_file="/test2.json"
        )
        
        status = self.notifier.get_all_agents_status()
        
        self.assertEqual(status.get("ATLAS", 0), 1)
        self.assertEqual(status.get("CLIO", 0), 1)
        self.assertEqual(status.get("NEXUS", 0), 0)


class TestAlertDataclass(unittest.TestCase):
    """Test Alert dataclass functionality."""
    
    def test_alert_to_dict(self):
        """Test Alert.to_dict() conversion."""
        alert = Alert(
            id="test123",
            timestamp="2026-01-22T12:00:00",
            from_agent="FORGE",
            to_agent="ATLAS",
            subject="Test",
            preview="Preview text",
            source_file="/test.json",
            priority="HIGH",
            read=False
        )
        
        d = alert.to_dict()
        
        self.assertEqual(d['id'], "test123")
        self.assertEqual(d['from_agent'], "FORGE")
        self.assertEqual(d['to_agent'], "ATLAS")
        self.assertEqual(d['priority'], "HIGH")
    
    def test_alert_from_dict(self):
        """Test Alert.from_dict() conversion."""
        data = {
            "id": "test456",
            "timestamp": "2026-01-22T12:00:00",
            "from_agent": "CLIO",
            "to_agent": "NEXUS",
            "subject": "Roundtrip Test",
            "preview": "Test preview",
            "source_file": "/test.json",
            "priority": "NORMAL",
            "read": True
        }
        
        alert = Alert.from_dict(data)
        
        self.assertEqual(alert.id, "test456")
        self.assertEqual(alert.from_agent, "CLIO")
        self.assertEqual(alert.to_agent, "NEXUS")
        self.assertTrue(alert.read)


def run_tests():
    """Run all tests with nice output."""
    print("=" * 70)
    print("TESTING: SynapseNotify v1.0")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSynapseNotifyCore))
    suite.addTests(loader.loadTestsFromTestCase(TestSynapseNotifyOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestSynapseNotifyMessageParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestSynapseNotifyEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestAlertDataclass))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("=" * 70)
    print(f"RESULTS: {result.testsRun} tests")
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"[OK] Passed: {passed}")
    if result.failures:
        print(f"[X] Failed: {len(result.failures)}")
    if result.errors:
        print(f"[!] Errors: {len(result.errors)}")
    print("=" * 70)
    
    # Print pass rate
    if result.testsRun > 0:
        pass_rate = (passed / result.testsRun) * 100
        print(f"Pass Rate: {pass_rate:.1f}%")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
