import string

LETTER = set(string.ascii_letters)
DIGIT = set(string.digits)
WHITE_SPACE = set(string.whitespace)
SYMBOL = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<'}
KEYWORDS = {'if', 'else', 'void', 'int', 'while', 'break', 'switch', 'default', 'case', 'return'}
VALID_CHARS = LETTER.union(DIGIT).union(WHITE_SPACE).union(SYMBOL)

EPSILON = 'ε'
SYNCH = 'synch'
EOF = '$'