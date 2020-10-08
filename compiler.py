from asset import *
from scanner import *

symbol_table = {}


input_file = open('input.txt', 'r')
lines = input_file.readlines()
total_tokens = []

for line in lines:
    pointer = 0
    tokens = []
    while pointer < len(line):
        cur_char = line[pointer]
        if cur_char in DIGIT:
            pointer, lexeme, type_of_token = num_dfa(pointer, line)
        elif cur_char in LETTER:
            pointer, lexeme, type_of_token = keyword_identifier_dfa(pointer, line)
            symbol_table[lexeme] = []
        elif cur_char == '/':
            pointer, lexeme, type_of_token = comment_dfa(pointer, line)
        elif cur_char == '=':
            pointer, lexeme, type_of_token = eq_symbol_dfa(pointer, line)
        elif cur_char == '*':
            pointer, lexeme, type_of_token = star_symbol_dfa(pointer, line)
        elif cur_char in SYMBOL:
            pointer, lexeme, type_of_token = symbol_dfa(pointer, line)
        elif cur_char in WHITE_SPACE:
            pointer, lexeme, type_of_token = whitespace_dfa(pointer, line)
        else:
            #todo error
            pass

        if type_of_token and type_of_token != 'whitespace':
            tokens.append((type_of_token, lexeme))

    total_tokens.append(tokens)


# error_file = open('lexical_errors.txt', 'w')
# symbol_file = open('symbol_table.txt', 'w')
# output_file = open('tokens.txt', 'w')

for i, line in enumerate(total_tokens):
    output_tokens = str(i+1)+'.\t'
    for token in line:
        output_tokens += str(token)
    total_tokens[i] = output_tokens

with open('tokens.txt', 'w') as output_file:
    output_file.writelines(total_tokens)

input_file.close()
