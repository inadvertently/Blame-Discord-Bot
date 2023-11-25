

def xor(value: str, key=5):
    chars = list(value)
    value = ""
    for char in chars:
        h = (ord(char)^key)
        value += format(h, "x")
    return value
    

    