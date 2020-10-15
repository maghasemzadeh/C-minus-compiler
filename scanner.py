from asset import *
import string


def next_iter(pointer, line, lexeme):
    pointer += 1
    cur_char = line[pointer]
    lexeme += cur_char
    return pointer, cur_char, lexeme


def num_dfa(pointer, line):
    token_type = 'NUM'
    lexeme = line[pointer]
    other = WHITE_SPACE.union(SYMBOL).union('/')
    while True:
        pointer += 1
        cur_char = line[pointer]
        if cur_char in DIGIT:
            lexeme += cur_char
        elif cur_char in other:
            return pointer, lexeme, token_type
        elif cur_char in VALID_CHARS:
            lexeme += cur_char
            raise PanicException(pointer + 1, lexeme, 'Invalid number')
        else:
            return pointer, lexeme, token_type


def keyword_identifier_dfa(pointer, line):
    lexeme = line[pointer]
    other = WHITE_SPACE.union(SYMBOL).union('/')
    while True:
        pointer += 1
        cur_char = line[pointer]
        if cur_char in DIGIT.union(LETTER):
            lexeme += cur_char
        elif cur_char in other:
            if lexeme in KEYWORDS:
                type_of_token = 'KEYWORD'
            else:
                type_of_token = 'ID'
            return pointer, lexeme, type_of_token
        else:
            lexeme += cur_char
            raise PanicException(pointer + 1, lexeme, 'Invalid input')


def eq_symbol_dfa(pointer, line):
    token_type = 'SYMBOL'
    other = VALID_CHARS.difference({'='})
    lexeme = line[pointer]
    pointer, cur_char, lexeme = next_iter(pointer, line, lexeme)
    if cur_char == '=':
        return pointer + 1, lexeme, token_type
    else:
        return pointer, lexeme[:-1], token_type
    # raise PanicException(pointer + 1, lexeme, 'Invalid input')


def star_symbol_dfa(pointer, line):
    token_type = 'SYMBOL'
    other = VALID_CHARS.difference({'/'})
    lexeme = line[pointer]
    pointer, cur_char, lexeme = next_iter(pointer, line, lexeme)
    if cur_char == '/':
        raise PanicException(pointer + 1, lexeme, 'Unmatched comment')
    else:
        return pointer, lexeme[:-1], token_type
    # raise PanicException(pointer + 1, lexeme, 'Invalid input')


def symbol_dfa(pointer, line):
    return pointer + 1, line[pointer], 'SYMBOL'


def comment_dfa(pointer, line, comment_activated):
    token_type = 'COMMENT'
    if comment_activated:
        return *comment_paragraph_dfa(pointer, line, ''), token_type
    lexeme = line[pointer]
    pointer, cur_char, lexeme = next_iter(pointer, line, lexeme)
    if cur_char == '/':
        return *comment_line_dfa(pointer, line, lexeme), False, token_type
    elif cur_char == '*':
        return *comment_paragraph_dfa(pointer, line, lexeme), token_type
    raise PanicException(pointer + 1, lexeme, 'Invalid input')  # ino nagoftan!


def whitespace_dfa(pointer, line):
    lexeme = line[pointer]
    type_of_token = 'whitespace'
    pointer += 1
    return pointer, lexeme, type_of_token


def comment_line_dfa(pointer, line, lexeme):
    other_new_line = set(string.printable).difference({'\n'})
    pointer, cur_char, lexeme = next_iter(pointer, line, lexeme)
    while pointer < len(line) - 1 and cur_char in other_new_line:
        pointer, cur_char, lexeme = next_iter(pointer, line, lexeme)
    return pointer + 1, lexeme[:-1]


def comment_paragraph_dfa(pointer, line, lexeme):
    other_star = set(string.printable).difference({'*'})
    pointer, cur_char, lexeme = next_iter(pointer, line, lexeme)
    while True:
        while pointer < len(line) - 1 and cur_char in other_star:
            pointer, cur_char, lexeme = next_iter(pointer, line, lexeme)
        while pointer < len(line) - 1 and cur_char == '*':
            pointer, cur_char, lexeme = next_iter(pointer, line, lexeme)
        if cur_char == '/':
            return pointer + 1, lexeme, False
        return pointer + 1, lexeme, True
