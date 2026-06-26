import re
from typing import Optional

# ---------------------------------------------------------------------------
# Patterns that should NEVER appear in model output
# ---------------------------------------------------------------------------
SENSITIVE_OUTPUT_PATTERNS = [
    r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",  # email addresses
    r"\b\d{3}[\-.\s]?\d{3}[\-.\s]?\d{4}\b",                   # phone numbers
    r"\bhf_[A-Za-z0-9]{10,}\b",                                 # HuggingFace tokens
    r"\bsk-[A-Za-z0-9]{20,}\b",                                 # OpenAI-style API keys
    r"\bpassword\s*[:=]\s*\S+",                                  # password assignments
    r"\bsecret\s*[:=]\s*\S+",                                   # secret assignments
]

# ---------------------------------------------------------------------------
# Topics the bot must refuse to discuss
# ---------------------------------------------------------------------------
BLOCKED_INPUT_TOPICS = [
    "other user",
    "other customer",
    "all reservations",
    "database credentials",
    "admin password",
    "system prompt",
    "internal data",
    "ignore previous",
    "ignore instructions",
    "act as",
]

# Keywords that signal a reservation intent
RESERVATION_KEYWORDS = [
    "book",
    "reserve",
    "reservation",
    "want to park",
    "need a spot",
    "parking space",
    "make a booking",
]

# Keywords that signal an information request
INFO_KEYWORDS = [
    "price",
    "cost",
    "rate",
    "how much",
    "open",
    "close",
    "hour",
    "working",
    "where",
    "location",
    "available",
    "availability",
    "contact",
    "rules",
]


class Guardrails:
    """Input/output safety filter for the parking chatbot."""

    def __init__(self):
        self._output_patterns = [
            re.compile(p, re.IGNORECASE) for p in SENSITIVE_OUTPUT_PATTERNS
        ]

    # ------------------------------------------------------------------
    # Input checks
    # ------------------------------------------------------------------

    def check_input(self, user_input: str) -> tuple[bool, Optional[str]]:
        """
        Validate user input for blocked topics / prompt injection.

        Returns:
            (True, None)          – input is safe
            (False, warning_msg)  – input is blocked
        """
        lower = user_input.lower()
        for topic in BLOCKED_INPUT_TOPICS:
            if topic in lower:
                return (
                    False,
                    "I\'m sorry, I can\'t help with that topic. "
                    "How can I assist you with our parking services?",
                )
        return True, None

    # ------------------------------------------------------------------
    # Output filters
    # ------------------------------------------------------------------

    def filter_output(self, response: str) -> str:
        """Redact any sensitive patterns from the model's response."""
        for pattern in self._output_patterns:
            response = pattern.sub("[REDACTED]", response)
        return response

    # ------------------------------------------------------------------
    # Intent detection
    # ------------------------------------------------------------------

    def is_reservation_intent(self, user_input: str) -> bool:
        """Return True if the user wants to make a reservation."""
        lower = user_input.lower()
        return any(kw in lower for kw in RESERVATION_KEYWORDS)

    def is_info_intent(self, user_input: str) -> bool:
        """Return True if the user is asking for facility information."""
        lower = user_input.lower()
        return any(kw in lower for kw in INFO_KEYWORDS)
