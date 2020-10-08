import string


class PanicException(Exception):
    def __init__(self, pointer, error_type, lexeme, msg='Invalid syntax'):
        super().__init__(msg=msg)
        self.pointer = pointer
        self.error_type = error_type
        self.lexeme = lexeme


LETTER = set(string.ascii_letters)
DIGIT = set(string.digits)
WHITE_SPACE = set(string.whitespace)
SYMBOL = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '=='}
KEYWORDS = {'if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return'}
