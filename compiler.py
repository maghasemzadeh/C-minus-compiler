from asset import *
from scanner import *



def write_output_to_file(total_tokens):
    for i, line in enumerate(total_tokens):
        output_tokens = str(i + 1) + '.\t\t'
        for token in line:
            output_tokens += str(token) + ' '
        total_tokens[i] = output_tokens.replace("'", '') + '\n'
    with open('tokens.txt', 'w') as output_file:
        output_file.writelines(total_tokens)

def write_errors_to_file(lexical_errors):
    for i, (line, lexeme, message) in enumerate(lexical_errors):
        error = str(line) + '.\t' + f'({lexeme}, {message})'
        lexical_errors[i] = error + '\n'
    with open('lexical_errors.txt', 'w') as error_file:
        error_file.writelines(lexical_errors)

def write_symbols_to_file(symbol_table):
    symbols_string = []
    for i, symbol in enumerate(symbol_table):
        symbol_line = f'{i}.\t{symbol}'
        symbols_string.append(symbol_line + '\n')
    with open('symbol_table.txt', 'w') as symbol_file:
        symbol_file.writelines(symbols_string)


def get_next_token(line, pointer, comment_activated):
    cur_char = line[pointer]
    if comment_activated:
        print('comment ', end='')
        pointer, lexeme, token_type, comment_activated = comment_dfa(pointer, line, comment_activated)
        print('done')
    elif cur_char in DIGIT:
        print('num ', end='')
        pointer, lexeme, token_type = num_dfa(pointer, line)
        print('done')
    elif cur_char in LETTER:
        print('keyword ', end='')
        pointer, lexeme, token_type = keyword_identifier_dfa(pointer, line)
        symbol_table[lexeme] = []
        print('done')
    elif cur_char == '/':
        print('comment ', end='')
        pointer, lexeme, comment_activated, token_type = comment_dfa(pointer, line, comment_activated)
        print('done')
    elif cur_char == '=':
        print('eq_symbol ', end='')
        pointer, lexeme, token_type = eq_symbol_dfa(pointer, line)
        print('done')
    elif cur_char == '*':
        print('star_symbol ', end='')
        pointer, lexeme, token_type = star_symbol_dfa(pointer, line)
        print('done')
    elif cur_char in SYMBOL:
        print('symbol ', end='')
        pointer, lexeme, token_type = symbol_dfa(pointer, line)
        print('done')
    elif cur_char in WHITE_SPACE:
        print('whitespace ', end='')
        pointer, lexeme, token_type = whitespace_dfa(pointer, line)
        print('done')
    else:
        raise PanicException(pointer + 1, line[pointer], 'Invalid input')
    return pointer, lexeme, token_type, comment_activated

def save_token(comment_lexeme, lexeme, comment_activated, tokens):
    if token_type != 'whitespace' and not comment_activated:
        tokens.append((token_type, comment_lexeme + lexeme))
        print(token_type, lexeme)
    elif comment_activated:
        comment_lexeme += lexeme
    if not comment_activated:
        comment_lexeme = ""

if __name__ == "__main__":
    
    symbol_table = {}
    total_tokens = []
    lexical_errors = []
    lines = []

    with open('input.txt', 'r') as input_file:
        lines = input_file.readlines()

    comment_activated = False
    comment_lexeme = ""
    for line_number, line in enumerate(lines):
        pointer = 0
        tokens = []
        while pointer < len(line):
            try:
                pointer, lexeme, token_type, comment_activated = get_next_token(line + '\n', pointer, comment_activated)
                save_token(comment_lexeme, lexeme, comment_activated, tokens)
            except PanicException as pe:
                lexical_errors.append((line_number+1, pe.lexeme, pe.message))
                pointer = pe.pointer
        total_tokens.append(tokens)


    write_symbols_to_file(symbol_table)
    write_output_to_file(total_tokens)
    write_errors_to_file(lexical_errors)
