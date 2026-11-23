import json
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from agent import process_request


class ReminderAgentTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 23, 10, 0, 0)

    def test_create_request_with_explicit_date_and_time(self):
        result = process_request("Remind me to call Alex tomorrow at 3pm", self.now)
        self.assertEqual(result["intent"], "create_reminder")
        self.assertEqual(result["task"], "call Alex")
        self.assertEqual(result["datetime"], "2026-11-24T15:00:00")
        self.assertIsNone(result["reason"])

    def test_reschedule_request_preserves_intent(self):
        result = process_request("Reschedule dentist appointment to Friday at 09:30", self.now)
        self.assertEqual(result["intent"], "reschedule_reminder")
        self.assertEqual(result["datetime"], "2026-11-27T09:30:00")

    def test_snooze_duration_is_relative_to_reference_time(self):
        result = process_request("Snooze my meeting for 10 minutes", self.now)
        self.assertEqual(result["intent"], "snooze_reminder")
        self.assertEqual(result["task"], "my meeting")
        self.assertEqual(result["datetime"], "2026-11-23T10:10:00")

    def test_missing_task_requires_clarification(self):
        result = process_request("Remind me tomorrow at 3pm", self.now)
        self.assertEqual(result["intent"], "clarification_required")
        self.assertEqual(result["task"], "")
        self.assertIsNone(result["datetime"])

    def test_missing_time_requires_clarification(self):
        result = process_request("Remind me to submit the report tomorrow", self.now)
        self.assertEqual(result["intent"], "clarification_required")
        self.assertIn("both a date and a time", result["reason"])

    def test_invalid_calendar_date_requires_clarification(self):
        result = process_request("Remind me to call Sam on 2026-02-30 at 2pm", self.now)
        self.assertEqual(result["intent"], "clarification_required")
        self.assertIn("date is invalid", result["reason"])
        self.assertEqual(result["task"], "call Sam")

    def test_invalid_clock_is_not_included_in_extracted_task(self):
        result = process_request("Remind me to file taxes on 2026-04-15 at 25:99", self.now)
        self.assertEqual(result["intent"], "clarification_required")
        self.assertEqual(result["task"], "file taxes")

    def test_unsupported_operation_does_not_claim_success(self):
        result = process_request("Delete my appointment reminder tomorrow at 3pm", self.now)
        self.assertEqual(result["intent"], "clarification_required")
        self.assertEqual(result["status"], "needs_clarification")
        self.assertIsNone(result["datetime"])

    def test_response_is_json_serializable_with_all_fields(self):
        result = process_request("Remind me to pay rent on 2026-12-01 at 8:00", self.now)
        decoded = json.loads(json.dumps(result))
        self.assertEqual(set(decoded), {"intent", "task", "datetime", "status", "reason"})


if __name__ == "__main__":
    unittest.main()
