from app.rag import ask_question
from app.guardrails import is_safe

while True:
    question = input('User: ')
    if question.lower() == 'exit':
        break

    if not is_safe(question):
        print('Blocked request.')
        continue

    print('\nBot:', ask_question(question))
