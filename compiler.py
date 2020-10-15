from asset import KEYWORDS
from scanner import get_next_token
from utils import *
import sys





if __name__ == "__main__":

    symbol_table = {}
    for sym in KEYWORDS:
        symbol_table[sym] = []
    total_tokens = []
    lexical_errors = {}
    lines = []

    with open('input.txt', 'r') as input_file:
        lines = input_file.readlines()

    comment_activated = False
    comment_lexeme = ""
    comment_start_line = sys.maxsize
    for line_number, line in enumerate(lines):
        pointer = 0
        tokens = []
        while pointer < len(line):
            try:
                pointer, lexeme, token_type, comment_activated = get_next_token(line + '\n', pointer, comment_activated, symbol_table)
                comment_lexeme = save_token(comment_lexeme, lexeme, comment_activated, tokens, token_type)
                if comment_activated:
                    comment_start_line = min(comment_start_line, line_number)
            except PanicException as pe:
                if lexical_errors.__contains__(line_number + 1):
                    lexical_errors[line_number + 1].append((line_number + 1, pe.lexeme, pe.message))
                else:
                    lexical_errors[line_number + 1] = [(line_number + 1, pe.lexeme, pe.message)]
                pointer = pe.pointer
        total_tokens.append(tokens)
    if comment_activated:
        lexeme = comment_lexeme[:7] + '...' if len(comment_lexeme) > 7 else comment_lexeme
        # todo check here?
        lexical_errors[comment_start_line + 1] = [(comment_start_line + 1, lexeme, 'Unclosed comment')]


    write_symbols_to_file(symbol_table)
    write_output_to_file(total_tokens)
    write_errors_to_file(lexical_errors)
