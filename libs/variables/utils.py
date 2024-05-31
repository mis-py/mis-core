
def type_convert(value: str, to_type: str):
    type_convertors = {
        "text": str,
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "list": lambda val: val.replace(" ", "").split(',')
    }
    return type_convertors[to_type](value)

