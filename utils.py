
def write_output_to_file(total_tokens):
    for i, line in enumerate(total_tokens):
        if not line:
            total_tokens[i] = ''
            continue
        output_tokens = str(i + 1) + '.\t'
        for token in line:
            output_tokens += str(token) + ' '
        output_tokens = output_tokens[:-1]
        total_tokens[i] = output_tokens.replace("'", '') + '\n'
    with open('tokens.txt', 'w') as output_file:
        output_file.writelines(total_tokens)


def write_errors_to_file(lexical_errors):
    if not lexical_errors:
        lexical_errors = ['There is no lexical error.']
    else:
        lexical_errors = [lexical_errors[k] for k in sorted(lexical_errors)]
        for i, item in enumerate(lexical_errors):
            error = str(item[0][0]) + '.\t'
            for (line, lexeme, message) in item:
                lexeme = lexeme.replace('\n', '')
                error += f'({lexeme}, {message}) '
            error = error[:-1]
            lexical_errors[i] = error + '\n'
    with open('lexical_errors.txt', 'w') as error_file:
        error_file.writelines(lexical_errors)


def write_symbols_to_file(symbol_table):
    symbols_string = []
    for i, symbol in enumerate(symbol_table):
        symbol_line = f'{i + 1}.\t{symbol}'
        symbols_string.append(symbol_line + '\n')
    with open('symbol_table.txt', 'w') as symbol_file:
        symbol_file.writelines(symbols_string)


def save_token(comment_lexeme, lexeme, comment_activated, tokens, token_type):
    if token_type != 'whitespace' and not comment_activated:
        if not token_type == "COMMENT":
            tokens.append((token_type, comment_lexeme + lexeme))
    elif comment_activated:
        comment_lexeme += lexeme
    if not comment_activated:
        comment_lexeme = ""
    return comment_lexeme


class PanicException(Exception):
    def __init__(self, pointer, lexeme, message='Invalid syntax'):
        super(PanicException, self).__init__(message)
        self.message = message
        self.pointer = pointer
        self.lexeme = lexeme

