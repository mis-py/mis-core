import re


def regexp_match(input_text, regexp):
    # pattern = re.compile(r"off[0-9]+\s-\s[a-zA-Z]+\s-\s[a-zA-Z]+\s-\s[A-Za-z0-9]+", re.IGNORECASE)
    pattern = re.compile(regexp, re.IGNORECASE)
    return pattern.match(input_text)
