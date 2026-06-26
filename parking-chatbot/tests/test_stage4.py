"""
Stage 4 tests: LangGraph pipeline (chatbot mocked to avoid LLM/ChromaDB calls).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage


def make_mock_chatbot(response_text="Hello!", reservation_data=None):
    """Return a mock ParkingChatbot that returns a fixed response."""
    mock = MagicMock()
    mock.respond.return_value = (response_text, reservation_data or {})
    return mock


class TestGraphBuilds:
    def test_graph_compiles(self):
        """Graph should compile without errors when a mock chatbot is injected."""
        from stage4_graph.graph import build_parking_graph
        app = build_parking_graph(chatbot=make_mock_chatbot())
        assert app is not None

    def test_graph_has_chatbot_node(self):
        from stage4_graph.graph import build_parking_graph
        app = build_parking_graph(chatbot=make_mock_chatbot())
        node_names = list(app.get_graph().nodes.keys())
        assert "chatbot" in node_names

    def test_graph_has_admin_node(self):
        from stage4_graph.graph import build_parking_graph
        app = build_parking_graph(chatbot=make_mock_chatbot())
        node_names = list(app.get_graph().nodes.keys())
        assert "admin_approval" in node_names

    def test_graph_has_write_node(self):
        from stage4_graph.graph import build_parking_graph
        app = build_parking_graph(chatbot=make_mock_chatbot())
        node_names = list(app.get_graph().nodes.keys())
        assert "write_reservation" in node_names


class TestGraphExecution:
    def test_normal_chat_turn_returns_ai_message(self):
        """A non-reservation message should produce an AIMessage and end the turn."""
        from stage4_graph.graph import build_parking_graph
        app = build_parking_graph(
            chatbot=make_mock_chatbot("Our hours are 06:00-23:00.")
        )
        state = {
            "messages": [HumanMessage(content="What are the hours?")],
            "reservation_data": {},
            "admin_approved": None,
            "admin_note": "",
        }
        result = app.invoke(state)
        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        assert len(ai_messages) >= 1
        assert "06:00" in ai_messages[-1].content

    @patch("stage2_hitl.admin_agent.AdminAgent.request_approval", return_value=(False, "Full"))
    def test_reservation_rejected_ends_without_write(self, _mock_admin):
        """When admin rejects, write_node must NOT be reached."""
        import os
        test_file = "_test_stage4_write.txt"
        if os.path.exists(test_file):
            os.remove(test_file)

        from stage4_graph.graph import build_parking_graph
        from stage3_mcp.reservation_writer import ReservationWriter

        writer = ReservationWriter(file_path=test_file)
        reservation = {
            "name": "Tom", "surname": "Test",
            "car_number": "TT-000",
            "start_date": "2026-07-01", "end_date": "2026-07-02",
        }
        chatbot = make_mock_chatbot("Submitted!", reservation)
        app = build_parking_graph(chatbot=chatbot)

        state = {
            "messages": [HumanMessage(content="yes")],
            "reservation_data": {},
            "admin_approved": None,
            "admin_note": "",
        }
        app.invoke(state)

        # File should be empty (only header) since reservation was rejected
        entries = writer.read_all()
        assert entries == []

        if os.path.exists(test_file):
            os.remove(test_file)
