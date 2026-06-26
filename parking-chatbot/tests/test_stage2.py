"""
Stage 2 tests: AdminAgent (console input mocked with unittest.mock.patch).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch
from stage2_hitl.admin_agent import AdminAgent


SAMPLE = {
    "name": "John",
    "surname": "Doe",
    "car_number": "ABC-123",
    "start_date": "2026-07-01",
    "end_date": "2026-07-05",
}


@pytest.fixture
def agent():
    return AdminAgent()


class TestAdminApproval:
    @patch("builtins.input", side_effect=["approve", ""])
    def test_approve_returns_true(self, _mock, agent):
        approved, note = agent.request_approval(SAMPLE)
        assert approved is True

    @patch("builtins.input", side_effect=["reject", "No spaces available"])
    def test_reject_returns_false(self, _mock, agent):
        approved, note = agent.request_approval(SAMPLE)
        assert approved is False
        assert "No spaces available" in note

    @patch("builtins.input", side_effect=["approve", "Looks good!"])
    def test_approve_carries_note(self, _mock, agent):
        approved, note = agent.request_approval(SAMPLE)
        assert approved is True
        assert note == "Looks good!"

    @patch("builtins.input", side_effect=["bad", "approve", ""])
    def test_invalid_then_approve(self, _mock, agent):
        """Entering an invalid decision first, then 'approve' should still work."""
        approved, _ = agent.request_approval(SAMPLE)
        assert approved is True


class TestFormatUserMessage:
    def test_approval_message_contains_approved(self, agent):
        msg = agent.format_user_message(SAMPLE, True, "All good")
        assert "APPROVED" in msg

    def test_approval_message_contains_car(self, agent):
        msg = agent.format_user_message(SAMPLE, True, "OK")
        assert "ABC-123" in msg

    def test_rejection_message_contains_rejected(self, agent):
        msg = agent.format_user_message(SAMPLE, False, "Full")
        assert "REJECTED" in msg

    def test_rejection_message_contains_reason(self, agent):
        msg = agent.format_user_message(SAMPLE, False, "Facility closed")
        assert "Facility closed" in msg
