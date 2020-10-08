from asset import *
import string

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
    type_of_token = 'SYMBOL'
    other = set(string.printable).difference({'='})
    lexeme = line[pointer]
    pointer += 1
    cur_char = line[pointer]
    lexeme += cur_char
    if cur_char == '=':
        return pointer, lexeme, type_of_token
    elif cur_char in other:
        return pointer - 1, lexeme[:-1], type_of_token
    raise PanicException(pointer + 1, lexeme, 'Invalid input')


def star_symbol_dfa(pointer, line):
    type_of_token = 'SYMBOL'
    other = set(string.printable).difference({'/'})
    lexeme = line[pointer]
    pointer += 1
    cur_char = line[pointer]
    lexeme += cur_char
    if cur_char == '/':
        return pointer, lexeme, type_of_token
    elif cur_char in other:
        return pointer - 1, lexeme[:-1], type_of_token
    raise PanicException(pointer + 1, lexeme, 'Invalid input')


def symbol_dfa(pointer, line):
    pass


def comment_dfa(pointer, line):
    pass


def whitespace_dfa(pointer, line):
    pass
