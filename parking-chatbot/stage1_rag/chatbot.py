from stage1_rag.vector_store import get_or_build_vector_store
from stage1_rag.rag_chain import create_rag_chain
from stage1_rag.guardrails import Guardrails
from data.parking_db import ParkingDatabase


class ParkingChatbot:
    """
    Stage 1 chatbot: RAG-powered info + interactive reservation data collection.

    Conversation states:
        chat              -> default: answer questions via RAG
        collecting_name   -> ask for first name
        collecting_surname -> ask for last name
        collecting_car    -> ask for car registration number
        collecting_start  -> ask for start date
        collecting_end    -> ask for end date
        confirm           -> show summary and ask yes/no
    """

    def __init__(self):
        self.guardrails = Guardrails()
        self.db = ParkingDatabase()
        self._state = "chat"
        self._reservation_data: dict = {}

        print("[Chatbot] Loading vector store (first run downloads ~80MB model)...")
        vector_store = get_or_build_vector_store()
        self._rag_chain = create_rag_chain(vector_store)
        print("[Chatbot] Ready.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def respond(self, user_input: str) -> tuple[str, dict]:
        """
        Process one user message.

        Returns:
            (response_text, reservation_data)
            reservation_data is non-empty only when the user confirms a booking.
        """
        # --- guardrails input check ---
        is_safe, warning = self.guardrails.check_input(user_input)
        if not is_safe:
            return warning, {}

        # --- reservation collection flow ---
        if self._state == "collecting_name":
            self._reservation_data["name"] = user_input.strip()
            self._state = "collecting_surname"
            return "What is your surname (last name)?", {}

        if self._state == "collecting_surname":
            self._reservation_data["surname"] = user_input.strip()
            self._state = "collecting_car"
            return "What is your vehicle registration number (car number)?", {}

        if self._state == "collecting_car":
            self._reservation_data["car_number"] = user_input.strip().upper()
            self._state = "collecting_start"
            return "Please enter the reservation start date (YYYY-MM-DD):", {}

        if self._state == "collecting_start":
            self._reservation_data["start_date"] = user_input.strip()
            self._state = "collecting_end"
            return "Please enter the reservation end date (YYYY-MM-DD):", {}

        if self._state == "collecting_end":
            self._reservation_data["end_date"] = user_input.strip()
            self._state = "confirm"
            d = self._reservation_data
            summary = (
                f"\nReservation Summary:\n"
                f"  Name      : {d['name']} {d['surname']}\n"
                f"  Car Number: {d['car_number']}\n"
                f"  Period    : {d['start_date']} to {d['end_date']}\n\n"
                f"Do you confirm? (yes / no)"
            )
            return summary, {}

        if self._state == "confirm":
            if user_input.strip().lower() in ("yes", "y"):
                self._state = "chat"
                completed = self._reservation_data.copy()
                self._reservation_data = {}
                return (
                    "Your reservation request has been submitted for admin approval. "
                    "You will be notified once confirmed.",
                    completed,
                )
            else:
                self._state = "chat"
                self._reservation_data = {}
                return "Reservation cancelled. How else can I help you?", {}

        # --- detect reservation intent ---
        if self.guardrails.is_reservation_intent(user_input):
            self._state = "collecting_name"
            return "I'd be happy to help with a reservation! What is your first name?", {}

        # --- default: RAG answer (with optional dynamic data prefix) ---
        dynamic_ctx = self._build_dynamic_context(user_input)
        query = f"{dynamic_ctx}\n\nUser question: {user_input}" if dynamic_ctx else user_input

        response = self._rag_chain.invoke(query)
        response = self.guardrails.filter_output(response)
        return response, {}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_dynamic_context(self, query: str) -> str:
        """Prepend live SQLite data to the query when relevant."""
        lower = query.lower()
        parts = []

        if any(kw in lower for kw in ("price", "cost", "rate", "how much")):
            prices = self.db.get_prices()
            parts.append(
                "Current prices: "
                + ", ".join(f"{p['rate_type']}: ${p['amount']}" for p in prices)
            )

        if any(kw in lower for kw in ("available", "availability", "space", "spot")):
            avail = self.db.get_availability()
            parts.append(
                f"Available spaces today: {avail['available']} / {avail['total']}"
            )

        if any(kw in lower for kw in ("hour", "open", "close", "working")):
            hours = self.db.get_working_hours()
            parts.append(
                "Working hours: "
                + "; ".join(f"{h['day']}: {h['open']}-{h['close']}" for h in hours)
            )

        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_chatbot():
    """Run the Stage 1 chatbot in an interactive console loop."""
    print("=" * 55)
    print("  Welcome to the Parking Reservation Chatbot")
    print("  Type 'quit' or 'exit' to stop.")
    print("=" * 55)

    bot = ParkingChatbot()
    print("\nBot: Hello! How can I help you today? You can ask\n"
          "     about our parking facility or make a reservation.\n")

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

        response, reservation_data = bot.respond(user_input)
        print(f"\nBot: {response}\n")

        if reservation_data:
            print(f"[INFO] Reservation ready for admin: {reservation_data}")


if __name__ == "__main__":
    run_chatbot()
