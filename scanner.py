from asset import *


def num_dfa(pointer, line):
    type_of_token = 'num'
    lexeme = line[pointer]
    other = WHITE_SPACE.union(SYMBOL).union('/')
    while True:
        pointer += 1
        cur_char = line[pointer]
        if cur_char in DIGIT:
            lexeme += cur_char
        elif cur_char in other:
            return pointer, lexeme, type_of_token
        else:
            lexeme += cur_char
            raise PanicException(pointer + 1, lexeme, 'Invalid input')


def keyword_identifier_dfa(pointer, line):
    pass


def eq_symbol_dfa(pointer, line):
    pass


def star_symbol_dfa(pointer, line):
    pass


def symbol_dfa(pointer, line):
    pass


def comment_dfa(pointer, line):
    pass


def whitespace_dfa(pointer, line):
    pass
