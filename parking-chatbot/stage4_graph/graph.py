"""
Stage 4: LangGraph Orchestration
=================================
Graph structure (one invoke = one user turn):

  [chatbot_node]
       |
       +-- reservation collected? --> [admin_node]
       |                                  |
       |                                  +-- approved? --> [write_node] --> END
       |                                  |
       |                                  +-- rejected? --> END
       |
       +-- normal response ----------> END

The outer while-loop in run_parking_graph() handles reading the next
user message. LangGraph processes each message atomically.
"""

from typing import TypedDict, Optional, Annotated
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from stage1_rag.chatbot import ParkingChatbot
from stage2_hitl.admin_agent import AdminAgent
from stage3_mcp.reservation_writer import ReservationWriter


# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------

class ParkingState(TypedDict):
    messages: Annotated[list, add_messages]   # full conversation history
    reservation_data: dict                     # filled when user confirms booking
    admin_approved: Optional[bool]             # set after admin decision
    admin_note: str                            # admin's note/reason


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_parking_graph(chatbot: Optional[ParkingChatbot] = None):
    """
    Compile and return the LangGraph application.

    Args:
        chatbot: Optional pre-built ParkingChatbot (useful for testing).
                 If None, a new instance is created (loads ChromaDB).
    """
    _chatbot = chatbot or ParkingChatbot()
    _admin = AdminAgent()
    _writer = ReservationWriter()

    # -----------------------------------------------------------------------
    # Node 1: RAG chatbot — handles user message and reservation data collection
    # -----------------------------------------------------------------------
    def chatbot_node(state: ParkingState) -> dict:
        last_msg = state["messages"][-1]
        user_text = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

        response_text, reservation_data = _chatbot.respond(user_text)

        return {
            "messages": [AIMessage(content=response_text)],
            "reservation_data": reservation_data,
            "admin_approved": None,
            "admin_note": "",
        }

    # -----------------------------------------------------------------------
    # Node 2: Human-in-the-loop admin approval
    # -----------------------------------------------------------------------
    def admin_node(state: ParkingState) -> dict:
        approved, note = _admin.request_approval(state["reservation_data"])
        user_msg = _admin.format_user_message(state["reservation_data"], approved, note)
        return {
            "messages": [AIMessage(content=user_msg)],
            "admin_approved": approved,
            "admin_note": note,
        }

    # -----------------------------------------------------------------------
    # Node 3: Write confirmed reservation to file
    # -----------------------------------------------------------------------
    def write_node(state: ParkingState) -> dict:
        data = state["reservation_data"]
        approval_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        success = _writer.write_reservation(
            name=data["name"],
            surname=data["surname"],
            car_number=data["car_number"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            approval_time=approval_time,
        )
        msg = (
            "Reservation saved successfully! We look forward to welcoming you."
            if success
            else "There was an error saving your reservation. Please contact us."
        )
        return {"messages": [AIMessage(content=msg)]}

    # -----------------------------------------------------------------------
    # Routing functions
    # -----------------------------------------------------------------------
    def route_chatbot(state: ParkingState) -> str:
        """Go to admin approval if reservation data was collected, else end turn."""
        if state.get("reservation_data"):
            return "admin_approval"
        return END

    def route_admin(state: ParkingState) -> str:
        """Write to file if approved, else end turn."""
        if state.get("admin_approved"):
            return "write_reservation"
        return END

    # -----------------------------------------------------------------------
    # Build graph
    # -----------------------------------------------------------------------
    builder = StateGraph(ParkingState)

    builder.add_node("chatbot", chatbot_node)
    builder.add_node("admin_approval", admin_node)
    builder.add_node("write_reservation", write_node)

    builder.set_entry_point("chatbot")

    builder.add_conditional_edges(
        "chatbot",
        route_chatbot,
        {"admin_approval": "admin_approval", END: END},
    )
    builder.add_conditional_edges(
        "admin_approval",
        route_admin,
        {"write_reservation": "write_reservation", END: END},
    )
    builder.add_edge("write_reservation", END)

    return builder.compile()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_parking_graph():
    """Run the full parking pipeline interactively via the console."""
    print("=" * 55)
    print("  Parking Reservation System  (Full Pipeline)")
    print("  Type 'quit' or 'exit' to stop.")
    print("=" * 55)

    app = build_parking_graph()

    state: ParkingState = {
        "messages": [],
        "reservation_data": {},
        "admin_approved": None,
        "admin_note": "",
    }

    print("\nBot: Hello! How can I help you today?\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Bot: Goodbye!")
            break

        # Inject the new user message and invoke one turn
        state["messages"] = [HumanMessage(content=user_input)]
        result = app.invoke(state)

        # Print all AI messages produced this turn
        for msg in result.get("messages", []):
            if isinstance(msg, AIMessage):
                print(f"\nBot: {msg.content}\n")

        # Carry forward non-message state for the next turn
        state["reservation_data"] = result.get("reservation_data", {})
        state["admin_approved"] = result.get("admin_approved")
        state["admin_note"] = result.get("admin_note", "")


if __name__ == "__main__":
    run_parking_graph()
