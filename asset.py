import string


class PanicException(Exception):
    def __init__(self, line, pointer, lexeme, message='Invalid syntax'):
        super(PanicException, self).__init__(message)
        self.message = message
        self.pointer = pointer
        self.lexeme = lexeme
        self.line = line


LETTER = set(string.ascii_letters)
DIGIT = set(string.digits)
WHITE_SPACE = set(string.whitespace)
SYMBOL = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '=='}
KEYWORDS = {'if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return'}
