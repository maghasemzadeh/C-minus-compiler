from pprint import pprint


class Codegen:
    def __init__(self):
        self.semantic_errors = []
        self.semantic_stack = []
        self.program_block = []
        self.cur_temp = 1000
        self.temp = {}
        self.cur_mem_addr = 500
        self.func_memory_cur = 2000
        self.memory = {}
        self.break_stack = []
        self.main_access_link = None
        self.fun_declarating = False
        self.arg_declarating = False
        self.action_symbols = {
            'pid': self.pid,
            'pnum': self.pnum,
            'array_address': self.array_address,
            'assign': self.assign,
            'add': self.add,
            'mult': self.mult,
            'save': self.save,
            'jp': self.jp,
            'jpf': self.jpf,
            'label': self.label,
            'relop': self.relop,
            'relop_sign': self.relop_sign,
            'sign': self.sign,
            'signed_num': self.signed_num,
            'while': self.whil,
            'pop': self.pop,
            'output': self.output,
            'save_arr': self.save_arr,
            'tmp_save': self.tmp_save,
            'cmp_save': self.cmp_save,
            'jp_break': self.jp_break,
            'jp_switch': self.jp_switch,
            'jpf_switch': self.jpf_switch,
            'function_call': self.function_call,
            'var': self.var,
            'arg': self.arg,
            'fun_declaration': self.fun_declaration,
            'fun_declaration_end': self.fun_declaration_end,
            'param_var': self.param_var,
            'param_arr': self.param_arr,
            'fun_declarated': self.fun_declarated,
            'arg_declaration': self.arg_declaration,
            'return_stmt': self.return_stmt,
        }
        self.arg_actions = ['pid', 'pnum', 'sign', 'relop_sign',
                            'fun_declaration', 'arg_declaration']
        self.symbol_table = {}
        self.temp_args = []
        self.function = None
        self.callers = []
        self.function_arg_number = 0
        self.temp_id = None

    def find_addr(self):
        t = self.cur_mem_addr
        self.cur_mem_addr += 4
        return t

    def get_temp(self):
        t = self.cur_temp
        self.cur_temp += 4
        return t

    def find_func_addr(self):
        t = self.func_memory_cur
        self.func_memory_cur += 4
        return t

    def generate(self, action_symbol, arg=None):
        if not self.main_access_link:
            t = self.get_temp()
            self.main_access_link = t
        print(f'{action_symbol[1:]}({arg})\r\t\t\t\t\t\t\t\t-> {str(self.semantic_stack)[:-1]}')
        self.action_symbols[action_symbol[1:]](arg)

    def pid(self, args):
        tmp = 0
        if len(args) == 3:
            void_type = args[0]
        else:
            tmp = 1
        lexeme = args[1 - tmp]
        line_no = args[2 - tmp]
        self.temp_id = lexeme
        if lexeme in self.symbol_table and self.symbol_table[lexeme]['type'] == 'func':
            self.callers.append(self.function)
            self.function = lexeme
            t = self.symbol_table[lexeme]['return_address']
            l = len(self.program_block)
            self.program_block.append(f'(ASSIGN, {l}, {t}, )')
            return
        if self.fun_declarating:
            for key, value in self.symbol_table[self.function]["args"]:
                if key == lexeme:
                    self.semantic_stack.append(value['addr'])
                    return
            for key, value in self.symbol_table[self.function]["vars"].items():
                if key == lexeme:
                    self.semantic_stack.append(value['addr'])
                    return
            for key, val in self.memory.items():
                if key == lexeme:
                    self.semantic_stack.append(val)
                    return
            if lexeme == 'output':
                return
            if void_type:
                err_msg = f"{line_no}: Semantic Error! Illegal type of void for {lexeme}."
                self.semantic_errors.append(err_msg)
                return
            t = self.find_func_addr()
            sym = {'addr': t, 'data_type': 'void' if void_type else 'int'}
            if self.arg_declarating:
                self.temp_args.append([lexeme, sym])
            else:
                if not 'vars' in self.symbol_table[self.function]:
                    self.symbol_table[self.function]['vars'] = {}
                sym = {lexeme: sym}
                self.symbol_table[self.function]['vars'].update(sym)

        else:
            for key, val in self.memory.items():
                if key == lexeme:
                    self.semantic_stack.append(val)
                    return
            if lexeme == 'output':
                return
            addr = self.find_addr()
            self.memory.update({lexeme: addr})
            sym = {'addr': addr, 'data_type': 'void' if void_type else 'int', 'args': {}, 'vars': {}}
            self.symbol_table.update({lexeme: sym})
            self.program_block.append(f'(ASSIGN, #0, {addr}, )')
            self.semantic_stack.append(addr)

    def var(self, args):
        void_type = args[0]
        lexeme = args[1]
        line_no = args[2]
        if void_type:
            err_msg = f"{line_no}: Semantic Error! Illegal type of void for {lexeme}."
            self.semantic_errors.append(err_msg)
            del self.symbol_table[lexeme]
            return
        if self.function:
            self.symbol_table[self.function]['vars'][lexeme].update({'type': 'var'})
        else:
            self.symbol_table[lexeme].update({'type': 'var'})

    def pnum(self, arg):
        num_addr = self.get_temp()
        self.program_block.append(f'(ASSIGN, #{arg}, {num_addr}, )')
        self.temp.update({num_addr: arg})
        self.semantic_stack.append(num_addr)

    def array_address(self, arg=None):
        index = self.semantic_stack.pop()
        var_addr = self.semantic_stack.pop()
        t = self.get_temp()
        self.program_block.append(f'(MULT, {index}, #4, {t})')
        self.program_block.append(f'(ADD, #{var_addr}, {t}, {t})')
        self.semantic_stack.append('@' + str(t))
        # self.temp.update({t: var_addr + 4*int(self.temp[index])})

    def assign(self, arg=None):
        op2 = self.semantic_stack.pop()
        op1 = self.semantic_stack.pop()
        self.program_block.append(f'(ASSIGN, {op2}, {op1}, )')
        # t = self.get_temp()
        self.semantic_stack.append(op1)
        # self.temp[t] = op1

    def whil(self, arg=None):
        i = len(self.program_block)
        self.program_block[self.semantic_stack[-1]] = f'(JPF, {self.semantic_stack[-2]}, {i + 1}, )'
        self.program_block.append(f'(JP, {self.semantic_stack[-3] + 1}, , )')
        # self.program_block.append('')
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()

    def add(self, arg=None):
        op1 = self.semantic_stack.pop()
        operation = self.semantic_stack.pop()
        op2 = self.semantic_stack.pop()
        t = self.get_temp()
        self.semantic_stack.append(t)
        if operation == '+':
            self.program_block.append(f'(ADD, {op1}, {op2}, {t})')
        else:
            self.program_block.append(f'(SUB, {op2}, {op1}, {t})')

    def mult(self, arg=None):
        op1 = self.semantic_stack.pop()
        op2 = self.semantic_stack.pop()
        t = self.get_temp()
        self.semantic_stack.append(t)
        self.program_block.append(f'(MULT, {op1}, {op2}, {t})')

    def save(self, arg=None):
        pb_ind = len(self.program_block)
        self.semantic_stack.append(pb_ind)
        self.program_block.append('')

    def jpf(self, arg=None):
        pb_ind = self.semantic_stack.pop()
        if_exp = self.semantic_stack.pop()
        i = len(self.program_block)

        self.program_block[pb_ind] = f'(JPF, {if_exp}, {i + 1},)'
        self.semantic_stack.append(i)
        self.program_block.append('')

    def jp(self, arg=None):
        pb_ind = self.semantic_stack.pop()
        i = len(self.program_block)
        self.program_block[pb_ind] = f'(JP, {i}, ,)'

    def label(self, arg=None):
        self.break_stack.append('while')
        pb_ind = len(self.program_block) - 1
        self.semantic_stack.append(pb_ind)

    def relop(self, arg=None):
        op_2 = self.semantic_stack.pop()
        operand = self.semantic_stack.pop()
        op_1 = self.semantic_stack.pop()
        t = self.get_temp()
        self.semantic_stack.append(t)
        if operand == '==':
            self.program_block.append(f'(EQ, {op_1}, {op_2}, {t})')
        elif operand == '<':
            self.program_block.append(f'(LT, {op_1}, {op_2}, {t})')

    def relop_sign(self, arg):
        self.semantic_stack.append(arg)

    def sign(self, arg):
        self.semantic_stack.append(arg)

    def signed_num(self, arg=None):
        n = self.semantic_stack.pop()
        sign = self.semantic_stack.pop()
        if self.temp.__contains__(n):
            number = int(self.temp[n])
            if sign == '-':
                self.pnum(-number)
            else:
                self.pnum(number)
        else:
            for key, val in self.memory.items():
                if val == n:
                    number = val
                    t = self.get_temp()
                    self.semantic_stack.append(t)
                    if sign == '-':
                        self.program_block.append(f'(MULT, {number}, #-1, {t})')
                    else:
                        self.program_block.append(f'(MULT, {number}, #1, {t})')

        # todo check here

    def save_program_block(self):
        with open('output.txt', 'w') as output:
            for i, block in enumerate(self.program_block):
                output.write(f'{i}\t{block}\n')

    def pop(self, arg=None):
        self.semantic_stack.pop()

    def output(self, arg=None):
        to_print = self.semantic_stack.pop()
        self.semantic_stack.append(None)
        self.program_block.append(f'(PRINT, {to_print}, , )')


    def save_arr(self, args):
        void_type = args[0]
        lexeme = args[1]
        size = args[2]
        line_no = args[3]
        index = self.semantic_stack.pop()
        for i in range(1, int(self.temp[index])):
            self.program_block.append(f'(ASSIGN, #0, {self.cur_mem_addr}, )')
            self.cur_mem_addr += 4
        if void_type:
            err_msg = f"{line_no}: Semantic Error! Illegal type of void for {lexeme}."
            self.semantic_errors.append(err_msg)
            del self.symbol_table[lexeme]
            return

        self.symbol_table[lexeme].update({'type': 'arr'})

    def tmp_save(self, arg=None):
        self.break_stack.append('switch')
        i = len(self.program_block)
        self.program_block.append(f'(JP, {i + 2}, ,)')
        self.program_block.append('')
        self.semantic_stack.append(i + 1)

    def cmp_save(self, arg=None):
        t = self.get_temp()
        op1 = self.semantic_stack.pop()
        op2 = self.semantic_stack[-1]
        self.program_block.append(f'(EQ, {op1}, {op2}, {t})')
        self.semantic_stack.append(t)
        i = len(self.program_block)
        self.semantic_stack.append(i)

    def jp_break(self, line_no):
        if len(self.break_stack) == 0:
            err_msg = f"{line_no}: Semantic Error! No 'while' or 'switch' found for 'break'"
            self.semantic_errors.append(err_msg)
        break_top = self.break_stack.pop()
        if break_top == 'switch':
            self.program_block.append(f'(JP, {self.semantic_stack[-4]}, ,)')
        else: #todo here for break in while loops
            self.program_block.append(f'(JP, {self.semantic_stack[-2]}, ,)')

    def jpf_switch(self, arg=None):
        ind = self.semantic_stack[-1]
        i = len(self.program_block)
        self.program_block[ind] = f'(JPF, {self.semantic_stack[-2]}, {i} ,)'
        self.semantic_stack.pop()
        self.semantic_stack.pop()

    def jp_switch(self, arg=None):
        i = len(self.program_block)
        ind = self.semantic_stack[-2]
        self.program_block[ind] = f'(JP, {i}, ,)'
        self.semantic_stack.pop()
        self.semantic_stack.pop()

    def function_call(self, arg):
        if self.function == 'output':
            self.output()
            return
        address = self.symbol_table[self.function]['addr']
        self.program_block.append(f'(jp, {address}, , )')
        if self.function_arg_number != len(self.symbol_table[self.function]['args']):
            err_msg = f"{arg}: semantic error! Mismatch in numbers of arguments of {self.function}"
            self.semantic_errors.append(err_msg)
            return
        self.function_arg_number = 0
        self.function = self.callers.pop()


    def arg(self, arg=None):
        if not self.function or ((not self.callers or self.callers[-1] != 'main') and self.fun_declarating):
            return
        st = self.symbol_table[self.function]
        if len(st["args"]) == self.function_arg_number:
            err_msg = f"{arg}: semantic error! Mismatch in numbers of arguments of {self.function}"
            self.semantic_errors.append(err_msg)
            return
        value_address = self.semantic_stack.pop()
        address = st['args'][self.function_arg_number]
        self.program_block.append(f'(ASSIGN, {value_address}, {address}, )')
        self.function_arg_number += 1

    def arg_declaration(self, arg):
        lexeme = arg
        self.arg_declarating = True
        self.fun_declarating = True
        self.function = self.temp_id
        t = self.find_func_addr()
        self.symbol_table[self.function].update({'return_value': t})
        t = self.find_func_addr()
        self.symbol_table[self.function].update({'return_address': t})

    def fun_declaration(self, arg):
        lexeme = arg
        if not self.function:
            return
        self.symbol_table[lexeme].update({'type': 'func'})

    def fun_declaration_end(self, arg=None):
        if not self.function:
            return
        self.fun_declarating = False
        address = self.symbol_table[self.function]['return_address']
        self.program_block.append(f'(jp, @{address}, , )')
        if self.symbol_table[self.function]['data_type'] == 'void':
            self.semantic_stack.append(None)
        return_value = self.symbol_table[self.function]['return_value']
        self.semantic_stack.append(return_value)
        self.symbol_table[self.function].update({'type': 'func'})
        self.function = None

    def param_arr(self, arg=None):
        self.temp_args[-1][-1].update({'type': 'arr'})

    def param_var(self, arg=None):
        self.temp_args[-1][-1].update({'type': 'var'})

    def fun_declarated(self, args):
        if not self.function:
            return
        self.symbol_table[self.function].update({'args': self.temp_args, 'addr': len(self.program_block)})
        self.arg_declarating = False
        self.temp_args = []

    def return_stmt(self, arg=None):
        t = self.symbol_table[self.function]['return_value']
        l = self.semantic_stack.pop()
        self.program_block.append(f'(ASSIGN, {l}, {t}, )')


# arg type check


# temp_args = [
#     [arg, {'addr': 2, 'data_type': 'void/int', 'type': 'var/arr'}],
#     [arg, {'addr': 2, 'data_type': 'void/int', 'type': 'var/arr'}],
# ]
