from assets import *
from anytree import Node, RenderTree


class Tree:
    def __init__(self, root):
        self.root_node = Node(root)
        self.last_node = self.root_node
        self.indexes_stack = []
        self.node_stack = []
        

    def add_node(self, node_name, is_terminal=False, **params):
        if is_terminal:
            node = Node(f"({params['token_type']}, {params['lexeme']})", parent=self.last_node)
        else:
            node = Node(node_name, parent=self.last_node)
        return node

    def pre_do(self, stack_len):
        if self.indexes_stack and stack_len == self.indexes_stack[-1]:
            self.last_node = self.node_stack.pop()
            self.indexes_stack.pop()

    def past_do(self, non_terminals, stack_len):
        self.last_node = non_terminals.pop(0)
        self.indexes_stack.extend(range(stack_len, stack_len + len(non_terminals)))
        self.node_stack.extend(reversed(non_terminals))

    
    def __str__(self):
        tree_string = ''
        for pre, _, node in RenderTree(self.root_node):
            tree_string += f"{pre}{node.name}\n"
        return tree_string

class Parser:
    def __init__(self, scanner, **paths):
        self.scanner = scanner
        self.syntax_errors = []

        first_dict = self.get_first_dict(path=paths.get('firsts', 'Firsts.csv'))
        follow_dict = self.get_follow_dict(path=paths.get('follows', 'Follows.csv'))
        grammar_tuples = self.get_grammar_tuple(path=paths.get('grammar', 'Grammar.csv'))
        predict_list = self.get_predict_list(path=paths.get('predicts', 'Predicts.csv'))
        start_symbol = grammar_tuples[0][0]
        self.parse_table = self.get_parse_table(grammar_tuples, first_dict, follow_dict, predict_list)
        self.non_terminals = first_dict.keys()

        self.stack = [start_symbol]
        self.tree = Tree(start_symbol)

    def parse(self):
        advance_input = True
        while True:
            if advance_input:
                lookahead, lexeme, token_type, line_no = self._get_valid_token()
            stack_top = self.stack[-1]
            if stack_top in self.non_terminals:
                advance_input = self._parse_non_terminal(stack_top, lookahead, lexeme, token_type, line_no, advance_input)
            elif stack_top == lookahead:
                if stack_top == EOF:
                    print('successfully parsed!')
                    return
                self.stack.pop()
                advance_input = True
            else:
                self._add_error(line_no, 'missing', self.stack.pop())


    def _parse_non_terminal(self, stack_top, lookahead, lexeme, token_type, line_no, advance_input):
        rules = self.next_term(stack_top, lookahead)
        if rules == 'synch':
            self._add_error(line_no, 'missing', self.stack.pop())
        elif rules == '':
            self._add_error(line_no, 'illegal', lookahead)
            advance_input = True
        elif rules == EPSILON:
            self.tree.add_node('epsilon')
            self.stack.pop()
            advance_input = False
        else:
            advance_input = self._parse_valid_non_terminal(rules, lexeme, token_type, advance_input)
        return advance_input

    
    def _parse_valid_non_terminal(self, rules, lexeme, token_type, advance_input):
        print(rules)
        stack_len = len(self.stack)
        self.tree.pre_do(stack_len)
        self.stack.pop() 
        non_terminal_rules = []
        for rule in rules:
            is_non_terminal = rule in self.non_terminals or rule == EOF
            node = self.tree.add_node(rule, not is_non_terminal, token_type=token_type, lexeme=lexeme)
            if is_non_terminal:
                non_terminal_rules.append(node)
        self.stack.extend(reversed(rules))
        advance_input = False
        if not non_terminal_rules:
            return advance_input
        self.tree.past_do(non_terminal_rules, stack_len)
        return advance_input


    def _add_error(self, line_no, error_type, argument):
        msg = f'#{str(line_no)} : syntax_error, {error_type} {argument}'
        self.syntax_errors.append(msg)

    def _get_valid_token(self):
        invalid_token = True  # whitespace and comment are not valid tokens
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
        return lookahead, lexeme, token_type, line_no


    def write_parse_tree_to_file(self):
        with open('parse_tree.txt', 'w') as parse_tree_file:
            parse_tree_file.writelines(str(self.tree))

    def get_first_dict(self, path):
        res = {}
        with open(path, 'r') as first_file:
            for line in first_file.readlines():
                words = line.strip().split(' ')
                res[words[0]] = words[1:]
        return res

    def get_follow_dict(self, path):
        res = {}
        with open(path, 'r') as follow_file:
            for line in follow_file.readlines():
                words = line.strip().split(' ')
                res[words[0]] = words[1:]
        return res

    def get_predict_list(self, path):
        res = []
        with open(path, 'r') as predict_file:
            for line in predict_file.readlines():
                words = line.strip().split(' ')
                res.append(words) 
        return res

    def get_grammar_tuple(self, path):
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

    def next_term(self, non_terminal, terminal):
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


