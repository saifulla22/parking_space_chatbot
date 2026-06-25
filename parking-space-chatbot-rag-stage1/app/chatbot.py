from app.guardrails import is_safe
from app.rag import retrieve_answer

def chat(question:str)->str:
    if not is_safe(question):
        return 'Request blocked by guardrails.'
    return retrieve_answer(question)
