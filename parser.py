from assets import *

class Parser:
    def __init__(self, parse_table, start_symbol, scanner, non_terminals):
        self.stack = [start_symbol]
        self.parse_table = parse_table
        self.scanner = scanner
        self.non_terminals = non_terminals
        self.syntax_errors = []
        self.first_dict = self.get_first_dict()
        self.follow_dict = self.get_follow_dict()
        self.grammar_tuple = self.get_grammar_tuple()
        self.predict_list = self.get_predict_list()
        self.parse_table = self.get_parse_table(
                                            self.grammar_tuple,
                                            self.first_dict,
                                            self.follow_dict,
                                            self.predict_list)
        

    def parse(self):
        advance_input = True
        while True:
            if advance_input:
                lookahead, token_type, line_no = self.scanner.get_next_token()
            stack_top = self.stack[-1]
            if stack_top in self.non_terminals:
                rules = self.parse_table[stack_top][lookahead]
                if rules == 'synch':
                    self.syntax_errors.append('#' + line_no + ' : syntax_error, missing ' + self.stack[-1])
                    self.stack.pop(-1)
                    # pass  # todo exception, pop stack[-1]
                elif rules == '':
                    self.syntax_errors.append('#' + line_no + ' : syntax_error, illegal ' + lookahead)
                    advance_input = True
                    # pass # todo exception, skip lookahead
                else:
                    for r in range(len(rules), -1, -1):
                        self.stack.append(rules[r])
                    advance_input = False
            elif stack_top == lookahead and stack_top == '$':
                return 'successfully parsed!'
            elif stack_top == lookahead:
                self.stack.pop(-1)
                advance_input = True
            else:
                self.syntax_errors.append('#' + line_no + ' : syntax_error, missing' + self.stack[-1])
                self.stack.pop(-1)
                # pass # todo exception, pop stack[-1]


    def get_first_dict(self, path='Firsts.csv'):
        res = {}
        with open(path, 'r') as first_file:
            for line in first_file.readlines():
                words = line.strip().split(' ')
                res[words[0]] = words[1:]
        return res

    def get_follow_dict(self, path='Follows.csv'):
        res = {}
        with open(path, 'r') as follow_file:
            for line in follow_file.readlines():
                words = line.strip().split(' ')
                res[words[0]] = words[1:]
        return res

    def get_predict_list(self, path='Predicts.csv'):
        res = []
        with open(path, 'r') as predict_file:
            for line in predict_file.readlines():
                words = line.strip().split(' ')
                res.append(words) 
        return res

    def get_grammar_tuple(self, path='Grammar.csv'):
        res = []
        with open(path, 'r') as grammar_file:
            for line in grammar_file.readlines():
                words = line.strip().split(' ')
                res.append((words[0], words[1:])) 
        return res

    def get_parse_table(self, grammar, first, follow, predict):
        parse_table = {nt:{} for nt in first.keys()}
        for (non_terminal, grammars), predicts in zip(grammar, predict):
            for terminal in predicts:
                parse_table[non_terminal][terminal] = grammars
        for non_terminal, firsts in first.items():
            if EPSILON in firsts:
                for terminal in follow[non_terminal]:
                    parse_table[non_terminal][terminal] = EPSILON
            else:
                for terminal in follow[non_terminal]:
                    parse_table[non_terminal][terminal] = SYNCH
        return parse_table

    def next_state(self, non_terminal, terminal):
        try:
            return self.parse_table[non_terminal][terminal]
        except:
            return ''

    # TODO: remove! (JUST FOR TESTS) 
    def print_parse_table(self, parse_table):
        import pandas as pd
        df = pd.DataFrame(parse_table).T
        df.fillna(0, inplace=True)
        print(df)


    def write_syntax_errors(self):
        res = []
        if len(self.syntax_errors) == 0:
            with open('symbol_table.txt', 'w') as file:
                file.writelines('there is no syntax errors.')
                return
        for i in self.syntax_errors:
            res.append(i + '\n')
        with open('syntax_errors.txt', 'w') as file:
            file.writelines(res)

