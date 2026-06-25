from app.rag import retrieve_answer

def test_answer():
    assert retrieve_answer('price')

def test_answer_type():
    assert isinstance(retrieve_answer('location'), str)
