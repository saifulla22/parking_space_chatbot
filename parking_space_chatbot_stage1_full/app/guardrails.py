BLOCKED_WORDS = ['password','database','all reservations','admin credentials']

def is_safe(question):
    q = question.lower()
    return not any(word in q for word in BLOCKED_WORDS)
