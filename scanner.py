from assets import *
import string
from asset import KEYWORDS
from utils import *
import sys


class Scanner:
    def __init__(self, input_path, symbol_table):
        self.total_tokens = []
        self.lexical_errors = {}
        self.lines = []
        self.symbol_table = symbol_table
        self.comment_activated = False
        self.comment_lexeme = ""
        self.comment_start_line = sys.maxsize

        with open(input_path, 'r') as input_file:
            self.lines = input_file.readlines()
        self.line_number = 0
        self.line = self.lines[0]
        self.pointer = 0
        self.tokens_in_line = []


    def get_next_token(self):
        if self.pointer >= len(self.line):
            self.line_number += 1
            if self.line_number >= len(self.lines):
                if self.comment_activated:
                    lexeme = self.comment_lexeme[:7] + '...' if len(self.comment_lexeme) > 7 else self.comment_lexeme
                    # todo check here?
                    self.lexical_errors[self.comment_start_line + 1] = [(self.comment_start_line + 1, lexeme, 'Unclosed comment')]
                return '$'
            self.line = self.lines[self.line_number]
            self.pointer = 0
            self.total_tokens.append(self.tokens_in_line)
            self.tokens_in_line = []

        try:
            self.pointer, lexeme, token_type, self.comment_activated = self.get_next_token_in_line(self.line + '\n',
                                                                                              self.pointer,
                                                                                              self.comment_activated,
                                                                                              self.symbol_table)
            self.comment_lexeme = save_token(self.comment_lexeme, lexeme, self.comment_activated, self.tokens_in_line, token_type)
            if self.comment_activated:
                self.comment_start_line = min(self.comment_start_line, self.line_number)
            return lexeme, token_type

        except PanicException as pe:
            if self.lexical_errors.__contains__(self.line_number + 1):
                self.lexical_errors[self.line_number + 1].append((self.line_number + 1, pe.lexeme, pe.message))
            else:
                self.lexical_errors[self.line_number + 1] = [(self.line_number + 1, pe.lexeme, pe.message)]
            self.pointer = pe.pointer
            return self.get_next_token()

    def show_results(self):
        lexeme = ''
        while lexeme != '$':
            # print(lexeme)
            lexeme = self.get_next_token()

        write_symbols_to_file(self.symbol_table)
        write_output_to_file(self.total_tokens)
        write_errors_to_file(self.lexical_errors)

    def get_next_token_in_line(self, line, pointer, comment_activated, symbol_table):
        cur_char = line[pointer]
        if comment_activated:
            pointer, lexeme, token_type, comment_activated = self.comment_dfa(pointer, line, comment_activated)
        elif cur_char in DIGIT:
            pointer, lexeme, token_type = self.num_dfa(pointer, line)
        elif cur_char in LETTER:
            pointer, lexeme, token_type = self.keyword_identifier_dfa(pointer, line)
            symbol_table[lexeme] = []
        elif cur_char == '/':
            pointer, lexeme, comment_activated, token_type = self.comment_dfa(pointer, line, comment_activated)
        elif cur_char == '=':
            pointer, lexeme, token_type = self.eq_symbol_dfa(pointer, line)
        elif cur_char == '*':
            pointer, lexeme, token_type = self.star_symbol_dfa(pointer, line)
        elif cur_char in SYMBOL:
            pointer, lexeme, token_type = self.symbol_dfa(pointer, line)
        elif cur_char in WHITE_SPACE:
            pointer, lexeme, token_type = self.whitespace_dfa(pointer, line)
        else:
            raise PanicException(pointer + 1, line[pointer], 'Invalid input')
        return pointer, lexeme, token_type, comment_activated

    def next_iter(self, pointer, line, lexeme):
        pointer += 1
        cur_char = line[pointer]
        lexeme += cur_char
        return pointer, cur_char, lexeme

    def num_dfa(self, pointer, line):
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
            else:
                lexeme += cur_char
                raise PanicException(pointer + 1, lexeme, 'Invalid number')

    def keyword_identifier_dfa(self, pointer, line):
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

    def eq_symbol_dfa(self, pointer, line):
        token_type = 'SYMBOL'
        other = VALID_CHARS.difference({'='})
        lexeme = line[pointer]
        pointer, cur_char, lexeme = self.next_iter(pointer, line, lexeme)
        if cur_char == '=':
            return pointer + 1, lexeme, token_type
        else:
            return pointer, lexeme[:-1], token_type
        # raise PanicException(pointer + 1, lexeme, 'Invalid input')

    def star_symbol_dfa(self, pointer, line):
        token_type = 'SYMBOL'
        other = VALID_CHARS.difference({'/'})
        lexeme = line[pointer]
        pointer, cur_char, lexeme = self.next_iter(pointer, line, lexeme)
        if cur_char == '/':
            raise PanicException(pointer + 1, lexeme, 'Unmatched comment')
        else:
            return pointer, lexeme[:-1], token_type
        # raise PanicException(pointer + 1, lexeme, 'Invalid input')

    def symbol_dfa(self, pointer, line):
        return pointer + 1, line[pointer], 'SYMBOL'

    def comment_dfa(self, pointer, line, comment_activated):
        token_type = 'COMMENT'
        if comment_activated:
            return *self.comment_paragraph_dfa(pointer, line, ''), token_type
        lexeme = line[pointer]
        pointer, cur_char, lexeme = self.next_iter(pointer, line, lexeme)
        if cur_char == '/':
            return *self.comment_line_dfa(pointer, line, lexeme), False, token_type
        elif cur_char == '*':
            return *self.comment_paragraph_dfa(pointer, line, lexeme), token_type
        raise PanicException(pointer + 1, lexeme, 'Invalid input')  # ino nagoftan!

    def whitespace_dfa(self, pointer, line):
        lexeme = line[pointer]
        type_of_token = 'whitespace'
        pointer += 1
        return pointer, lexeme, type_of_token

    def comment_line_dfa(self, pointer, line, lexeme):
        other_new_line = set(string.printable).difference({'\n'})
        pointer, cur_char, lexeme = self.next_iter(pointer, line, lexeme)
        while pointer < len(line) - 1 and cur_char in other_new_line:
            pointer, cur_char, lexeme = self.next_iter(pointer, line, lexeme)
        return pointer + 1, lexeme[:-1]

    def comment_paragraph_dfa(self, pointer, line, lexeme):
        other_star = set(string.printable).difference({'*'})
        pointer, cur_char, lexeme = self.next_iter(pointer, line, lexeme)
        while True:
            while pointer < len(line) - 1 and cur_char in other_star:
                pointer, cur_char, lexeme = self.next_iter(pointer, line, lexeme)
            while pointer < len(line) - 1 and cur_char == '*':
                pointer, cur_char, lexeme = self.next_iter(pointer, line, lexeme)
            if cur_char == '/':
                return pointer + 1, lexeme, False
            return pointer + 1, lexeme, True
