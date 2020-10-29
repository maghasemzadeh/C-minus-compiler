class Parser:
    def __init__(self, parse_table, start_symbol, scanner, non_terminals):
        self.stack = [start_symbol]
        self.parse_table = parse_table
        self.scanner = scanner
        self.non_terminals = non_terminals

    def parse(self):
        advance_input = True
        while True:
            if advance_input:
                lookahead = self.scanner.get_next_token()
            stack_top = self.stack[-1]
            if stack_top in self.non_terminals:
                rules = self.parse_table[stack_top][lookahead]
                if rules == 'synch':
                    pass  # todo exception, pop stack[-1]
                elif rules == '┤':
                    pass # todo exception, skip lookahead
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
                pass # todo exception, pop stack[-1]

