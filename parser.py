from assets import *
from anytree import Node, RenderTree

class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.syntax_errors = []
        self.first_dict = self.get_first_dict()
        self.follow_dict = self.get_follow_dict()
        self.grammar_tuples = self.get_grammar_tuple()
        self.predict_list = self.get_predict_list()
        self.parse_table = self.get_parse_table(
                                            self.grammar_tuples,
                                            self.first_dict,
                                            self.follow_dict,
                                            self.predict_list)
        start_symbol = self.grammar_tuples[0][0]
        self.non_terminals = self.first_dict.keys()
        self.stack = [start_symbol]
        self.root_node = Node(start_symbol)
        self.last_node = self.root_node
        self.indexes_stack = []
        self.node_stack = []

    def parse(self):
        advance_input = True
        while True:
            invalid_token = True  # whitespace and comment are not valid tokens
            if advance_input:
                while invalid_token:
                    lexeme, token_type, line_no = self.scanner.get_next_token()
                    if token_type in ['KEYWORD', 'SYMBOL'] or not token_type:
                        lookahead = lexeme
                        invalid_token = False
                    elif token_type in ['WHITESPACE', 'COMMENT']:
                        pass
                    else:
                        invalid_token = False
                        lookahead = token_type
                # print('lookahead = '+lookahead, end=' ')
            # if not self.stack:
            #     break
            stack_top = self.stack[-1]
            # print('- stack top = '+ stack_top, end='\t')
            if stack_top in self.non_terminals:
                rules = self.next_state(stack_top, lookahead)
                if rules == 'synch':
                    self.syntax_errors.append('#' + str(line_no) + ' : syntax_error, missing ' + self.stack[-1])
                    self.stack.pop(-1)
                elif rules == '':
                    self.syntax_errors.append('#' + str(line_no) + ' : syntax_error, illegal ' + lookahead)
                    advance_input = True
                elif rules == 'ε':
                    self.stack.pop(-1)
                    advance_input = False
                else:
                    print(rules)
                    tmp = []
                    stack_len = len(self.stack)
                    if self.indexes_stack and stack_len < self.indexes_stack[-1]:
                        self.last_node = self.node_stack.pop(-1)
                        self.indexes_stack.pop(-1)
                    self.stack.pop(-1) 
                    for rule in rules:
                        if rule in self.non_terminals or rule == EOF:
                            tmp.append(Node(rule, parent=self.last_node))
                    self.stack.extend(reversed(rules))
                    # print(f'tmp = {tmp}')
                    advance_input = False
                    if not tmp:
                        continue
                    self.last_node = tmp.pop(0)
                    self.indexes_stack.extend(range(stack_len, stack_len + len(tmp)))
                    self.node_stack.extend(reversed(tmp))
            elif stack_top == lookahead and stack_top == EOF:
                print('successfully parsed!')
                return
            elif stack_top == lookahead:
                self.stack.pop(-1)
                advance_input = True
            else:
                self.syntax_errors.append('#' + str(line_no) + ' : syntax_error, missing ' + self.stack[-1])
                self.stack.pop(-1)


    def parse_tree_to_string(self):
        res = ''
        for pre, fill, node in RenderTree(self.root_node):
            res += f"{pre}{node.name}\n"
        return res

    def write_parse_tree_to_file(self):
        parse_tree = self.parse_tree_to_string()
        with open('parse_tree.txt', 'w') as parse_tree_file:
            parse_tree_file.writelines(parse_tree)

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
                    if not terminal in parse_table[non_terminal]:
                        parse_table[non_terminal][terminal] = SYNCH
        return parse_table

    def next_state(self, non_terminal, terminal):
        try:
            return self.parse_table[non_terminal][terminal]
        except:
            return ''

    # TODO: remove! (JUST FOR TESTS) 
    def print_and_save_parse_table(self, parse_table):
        import pandas as pd
        df = pd.DataFrame(parse_table).T
        df.fillna('', inplace=True)
        with open('parse_table.txt', 'w') as parse_table_file:
            parse_table_file.writelines(df.to_string())
        print(df)


    def write_syntax_errors_to_file(self):
        res = []
        if len(self.syntax_errors) == 0:
            with open('syntax_errors.txt', 'w') as file:
                file.writelines('There is no syntax error.')
                return
        for i in self.syntax_errors:
            res.append(i + '\n')
        with open('syntax_errors.txt', 'w') as file:
            file.writelines(res)

