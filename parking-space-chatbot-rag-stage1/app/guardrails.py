BLOCKED = ['password','admin','all reservations']

def is_safe(text:str)->bool:
    t=text.lower()
    return not any(x in t for x in BLOCKED)
