from assets import *
from anytree import Node, RenderTree
from codegen import Codegen 
import re

class Tree:
    def __init__(self, root):
        self.root_node = Node(root)
        self.last_node = self.root_node
        self.indexes_stack = []
        self.fathers = []
        

    def add_node(self, stack_len, node_name, father=None, token_type=None):
        if not father:
            self.pop(stack_len)
            father = self.last_node
        if token_type:
            node = Node(f"({token_type}, {node_name})", parent=father)
        else: 
            node = Node(node_name, parent=father)
        return node

    def pop(self, stack_len):
        if not self.indexes_stack or stack_len != self.indexes_stack[-1]: return
        self.last_node = self.fathers.pop()
        self.indexes_stack.pop()

    def push(self, len_terms, stack_len, grandpa):
        if len_terms <= 0: return
        self.indexes_stack.extend(range(stack_len, stack_len + len_terms))
        self.fathers.extend(len_terms * [grandpa])

    
    def __str__(self):
        tree_string = ''
        for pre, _, node in RenderTree(self.root_node.children[0]):
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
        self._advance_input = True

        self.stack = [start_symbol]
        self.tree = Tree(start_symbol)

        self.codegen = Codegen()

    def parse(self):
        while True:
            if self._advance_input:
                lookahead, lexeme, token_type, line_no = self._get_valid_token()
                # print(f'lookahead={lookahead}, lexeme={lexeme}, token_type={token_type}, line_no={line_no}')
                if lookahead is None and lexeme is None:
                    return
            self.codegen.save_program_block()
            stack_top = self.stack[-1]
            # print(self.stack, lexeme)
            if stack_top in self.non_terminals:
                self._fetch_rules(stack_top, lookahead, line_no)
            elif stack_top == lookahead:
                self.stack.pop()
                if stack_top == EOF:
                    self.tree.add_node(len(self.stack), EOF)
                    self.codegen.save_program_block()
                    return
                self.tree.add_node(len(self.stack), lexeme, token_type=token_type)
                self._advance_input = True
            elif lookahead == EOF:
                pass
            elif re.match('^#\w+$', stack_top):
                self.stack.pop()
                self.tree.add_node(len(self.stack), stack_top)
                if stack_top == '#jp_break':
                    self.codegen.generate(stack_top, line_no)
                if stack_top[1:] in self.codegen.arg_actions:
                    self.codegen.generate(stack_top, lexeme)
                else:
                    self.codegen.generate(stack_top)
                self._advance_input = False
            else:
                self.stack.pop()
                self._advance_input = False
                self._add_error(line_no, 'missing', stack_top)
                self.tree.add_node(len(self.stack), lexeme, token_type=token_type)

    def _fetch_rules(self, stack_top, lookahead, line_no):
        rules = self.next_term(stack_top, lookahead)
        if rules == 'synch':
            self.stack.pop()
            self._add_error(line_no, 'missing', stack_top)
            self._advance_input = False
        elif rules == '':
            if lookahead == EOF:
                self._add_error(line_no, 'unexpected', 'EOF')
            else:
                self._add_error(line_no, 'illegal', lookahead)
            self._advance_input = True
        elif rules == [EPSILON]:
            self.stack.pop()
            father = self.tree.add_node(len(self.stack), stack_top)
            self.tree.add_node(len(self.stack), 'epsilon', father=father)
            self._advance_input = False
        else:
            self.stack.pop()
            self._push_rules(rules, stack_top)
            self._advance_input = False

    def _push_rules(self, rules, stack_top):
        stack_len = len(self.stack)
        new_node = self.tree.add_node(stack_len, stack_top)
        self.stack.extend(reversed(rules))
        self.tree.push(len(rules), stack_len, new_node)

    def _add_error(self, line_no, error_type, argument):
        msg = f'#{str(line_no+1)} : syntax_error, {error_type} {argument}'
        self.syntax_errors.append(msg)

    def is_terminal(self, term):
        return not term in self.non_terminals and not term == EOF

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
        for non_terminal, follows in follow.items():
            for terminal in follows:
                if terminal in parse_table[non_terminal]: continue
                parse_table[non_terminal][terminal] = SYNCH
        return parse_table

    def next_term(self, non_terminal, terminal):
        try:
            return self.parse_table[non_terminal][terminal]
        except:
            return ''

    # TODO: remove! (JUST FOR TESTS) 
    # def print_and_save_parse_table(self, path='parse_table.txt'):
    #     import pandas as pd
    #     df = pd.DataFrame(self.parse_table).T
    #     df.fillna('', inplace=True)
    #     df.to_csv(path)
    #     print(df)


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


