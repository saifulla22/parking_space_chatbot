from pathlib import Path

def retrieve_answer(question:str)->str:
    text = Path('data/parking_info.txt').read_text()
    return f'Based on parking information: {text[:200]}'
