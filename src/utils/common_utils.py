
def cast_to_int(string: str) -> int:
    try:
        return int(string)
    except ValueError:
        return -1
