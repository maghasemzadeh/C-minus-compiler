import string


class PanicException(Exception):
    pass


LETTER = set(string.ascii_letters)
DIGIT = set(string.digits)
WHITE_SPACE = set(string.whitespace)
SYMBOL = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '=='}
KEYWORDS = {'if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return'}
