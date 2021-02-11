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
        self.calling_function = []

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
        print('==== action sym',action_symbol)
        if not self.main_access_link:
            t = self.get_temp()
            self.main_access_link = t
        print(f'{action_symbol[1:]}({arg})\r\t\t\t\t\t\t\t\t-> {str(self.semantic_stack)[:-1]}')
        self.action_symbols[action_symbol[1:]](arg)

    def pid(self, args):
        print(args)
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
            self.calling_function.append(lexeme)
            return
        if self.fun_declarating:
            if lexeme == 'output':
                self.calling_function.append(lexeme)
                return
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
            self.semantic_stack.append(t)
        else:
            for key, val in self.memory.items():
                if key == lexeme:
                    self.semantic_stack.append(val)
                    return
            if lexeme == 'output':
                self.calling_function.append(lexeme)
                return
            addr = self.find_addr()
            self.memory.update({lexeme: addr})
            sym = {'addr': addr, 'data_type': 'void' if void_type else 'int', 'args': {}, 'vars': {}}
            self.symbol_table.update({lexeme: sym})
            self.add_to_program_block(f'(ASSIGN, #0, {addr}, )')
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
        self.add_to_program_block(f'(ASSIGN, #{arg}, {num_addr}, )')
        self.temp.update({num_addr: arg})
        self.semantic_stack.append(num_addr)

    def array_address(self, arg=None):
        index = self.semantic_stack.pop()
        var_addr = self.semantic_stack.pop()
        t = self.get_temp()
        self.add_to_program_block(f'(MULT, {index}, #4, {t})')
        self.add_to_program_block(f'(ADD, #{var_addr}, {t}, {t})')
        self.semantic_stack.append('@' + str(t))
        # self.temp.update({t: var_addr + 4*int(self.temp[index])})

    def assign(self, arg=None):
        pprint(self.symbol_table)
        op2 = self.semantic_stack.pop()
        op1 = self.semantic_stack.pop()
        self.add_to_program_block(f'(ASSIGN, {op2}, {op1}, )')
        # t = self.get_temp()
        self.semantic_stack.append(op1)
        # self.temp[t] = op1

    def whil(self, arg=None):
        i = len(self.program_block)
        self.program_block[self.semantic_stack[-1]] = f'(JPF, {self.semantic_stack[-2]}, {i + 1}, )'
        self.add_to_program_block(f'(JP, {self.semantic_stack[-3] + 1}, , )')
        # self.add_to_program_block('')
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.break_stack.pop()

    def add(self, arg=None):
        op1 = self.semantic_stack.pop()
        operation = self.semantic_stack.pop()
        op2 = self.semantic_stack.pop()
        t = self.get_temp()
        self.semantic_stack.append(t)
        if operation == '+':
            self.add_to_program_block(f'(ADD, {op1}, {op2}, {t})')
        else:
            self.add_to_program_block(f'(SUB, {op2}, {op1}, {t})')

    def mult(self, arg=None):
        op1 = self.semantic_stack.pop()
        op2 = self.semantic_stack.pop()
        t = self.get_temp()
        self.semantic_stack.append(t)
        self.add_to_program_block(f'(MULT, {op1}, {op2}, {t})')

    def save(self, arg=None):
        pb_ind = len(self.program_block)
        self.semantic_stack.append(pb_ind)
        self.add_to_program_block('')

    def jpf(self, arg=None):
        pb_ind = self.semantic_stack.pop()
        if_exp = self.semantic_stack.pop()
        i = len(self.program_block)
        print(self.program_block)

        self.program_block[pb_ind] = f'(JPF, {if_exp}, {i + 1},)'
        self.semantic_stack.append(i)
        self.add_to_program_block('')

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
            self.add_to_program_block(f'(EQ, {op_1}, {op_2}, {t})')
        elif operand == '<':
            self.add_to_program_block(f'(LT, {op_1}, {op_2}, {t})')

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
            if self.fun_declarating:
                for key, value in self.symbol_table[self.function]["args"]:
                    if value['addr'] == n:
                        number = value['addr']
                        t = self.get_temp()
                        self.semantic_stack.append(t)
                        if sign == '-':
                            self.add_to_program_block(f'(MULT, {number}, #-1, {t})')
                        else:
                            self.add_to_program_block(f'(MULT, {number}, #1, {t})')
                        return
                for key, value in self.symbol_table[self.function]["vars"].items():
                    if value['addr'] == n:
                        number = value['addr']
                        t = self.get_temp()
                        self.semantic_stack.append(t)
                        if sign == '-':
                            self.add_to_program_block(f'(MULT, {number}, #-1, {t})')
                        else:
                            self.add_to_program_block(f'(MULT, {number}, #1, {t})')
                        return
                for key, val in self.memory.items():
                    if value['addr'] == n:
                        number = value['addr']
                        t = self.get_temp()
                        self.semantic_stack.append(t)
                        if sign == '-':
                            self.add_to_program_block(f'(MULT, {number}, #-1, {t})')
                        else:
                            self.add_to_program_block(f'(MULT, {number}, #1, {t})')
                        return
            else:
                for key, val in self.memory.items():
                    if val == n:
                        number = val
                        t = self.get_temp()
                        self.semantic_stack.append(t)
                        if sign == '-':
                            self.add_to_program_block(f'(MULT, {number}, #-1, {t})')
                        else:
                            self.add_to_program_block(f'(MULT, {number}, #1, {t})')


    def save_program_block(self):
        with open('output.txt', 'w') as output:
            for i, block in enumerate(self.program_block):
                output.write(f'{i}\t{block}\n')

    def pop(self, arg=None):
        self.semantic_stack.pop()

    def output(self, arg=None):
        to_print = self.semantic_stack.pop()
        self.semantic_stack.append(None)
        self.add_to_program_block(f'(PRINT, {to_print}, , )')


    def save_arr(self, args):
        void_type = args[0]
        lexeme = args[1]
        size = args[2]
        line_no = args[3]
        index = self.semantic_stack.pop()
        if len(self.calling_function) > 0:
            self.symbol_table[self.function]['vars'][lexeme].update({'type': 'arr'})
            for i in range(1, int(self.temp[index])):
                self.add_to_program_block(f'(ASSIGN, #0, {self.func_memory_cur}, )')
                self.func_memory_cur += 4
        else:
            self.symbol_table[lexeme].update({'type': 'arr'})
            for i in range(1, int(self.temp[index])):
                self.add_to_program_block(f'(ASSIGN, #0, {self.cur_mem_addr}, )')
                self.cur_mem_addr += 4
        if void_type:
            err_msg = f"{line_no}: Semantic Error! Illegal type of void for {lexeme}."
            self.semantic_errors.append(err_msg)
            del self.symbol_table[lexeme]
            return


    def tmp_save(self, arg=None):
        self.break_stack.append('switch')
        print('break stacke now', self.break_stack)
        i = len(self.program_block)
        self.add_to_program_block(f'(JP, {i + 2}, ,)')
        self.add_to_program_block('')
        self.semantic_stack.append(i + 1)

    def cmp_save(self, arg=None):
        t = self.get_temp()
        op1 = self.semantic_stack.pop()
        op2 = self.semantic_stack[-1]
        self.add_to_program_block(f'(EQ, {op1}, {op2}, {t})')
        self.semantic_stack.append(t)
        self.add_to_program_block('')
        i = len(self.program_block)
        self.semantic_stack.append(i - 1)

    def jp_break(self, line_no):
        print('now we are in break ~~~~~~~~', self.break_stack)
        if len(self.break_stack) == 0:
            err_msg = f"{line_no}: Semantic Error! No 'while' or 'switch' found for 'break'"
            self.semantic_errors.append(err_msg)
        break_top = self.break_stack[-1]
        if break_top == 'switch':
            self.add_to_program_block(f'(JP, {self.semantic_stack[-4]}, ,)')
        else: #todo here for break in while loops
            self.add_to_program_block(f'(JP, {self.semantic_stack[-2]}, ,)')

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
        self.break_stack.pop()

    def function_call(self, arg):
        print('~~~~~~',self.calling_function)
        if self.calling_function[-1] == 'output':
            self.output()
            return
        address = self.symbol_table[self.calling_function[-1]]['addr']
        return_address = self.symbol_table[self.calling_function[-1]]['return_address']
        self.add_to_program_block(f'(ASSIGN, #{len(self.program_block) + 2}, {return_address}, )')
        self.add_to_program_block(f'(JP, {address}, , )')
        if self.function_arg_number != len(self.symbol_table[self.calling_function[-1]]['args']):
            err_msg = f"{arg}: semantic error! Mismatch in numbers of arguments of {self.calling_function[-1]}"
            self.semantic_errors.append(err_msg)
            return
        if self.symbol_table[self.calling_function[-1]]['data_type'] == 'void':
            self.semantic_stack.append(None)
        else:
            return_value = self.symbol_table[self.calling_function[-1]]['return_value']
            self.semantic_stack.append(return_value)
        self.function_arg_number = 0
        self.calling_function.pop()
        self.function = self.callers.pop()


    def arg(self, arg=None):
        if not self.function or ((not self.callers or self.callers[-1] != 'main') and self.fun_declarating):
            return
        st = self.symbol_table[self.calling_function[-1]]
        if len(st["args"]) == self.function_arg_number:
            err_msg = f"{arg}: semantic error! Mismatch in numbers of arguments of {self.calling_function[-1]}"
            self.semantic_errors.append(err_msg)
            return
        value_address = self.semantic_stack.pop()
        address = st['args'][self.function_arg_number][1]['addr']
        self.add_to_program_block(f'(ASSIGN, {value_address}, {address}, )')
        self.function_arg_number += 1

    def arg_declaration(self, arg):
        lexeme = arg
        self.arg_declarating = True
        self.fun_declarating = True
        self.function = self.temp_id
        if self.function != 'main':
            self.semantic_stack.append(len(self.program_block))
            self.program_block.append(None)
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
        self.add_to_program_block(f'(JP, @{address}, , )')
        if self.function != 'main':
            st = self.semantic_stack.pop()
            self.program_block[st] = f'(JP, {len(self.program_block)}, , )'
        self.symbol_table[self.function].update({'type': 'func'})
        self.function = None

    def param_arr(self, arg=None):
        self.temp_args[-1][-1].update({'type': 'arr'})
        if self.arg_declarating:
            self.semantic_stack.pop()

    def param_var(self, arg=None):
        self.temp_args[-1][-1].update({'type': 'var'})
        if self.arg_declarating:
            self.semantic_stack.pop()

    def fun_declarated(self, args):
        if not self.function:
            return
        self.symbol_table[self.function].update({'args': self.temp_args, 'addr': len(self.program_block)})
        self.arg_declarating = False
        self.temp_args = []

    def return_stmt(self, arg=None):
        if self.symbol_table[self.function]['data_type'] == 'void':
            return_address = self.symbol_table[self.function]['return_address']
            self.add_to_program_block(f'(JP, @{return_address}, , )')
            return
        t = self.symbol_table[self.function]['return_value']
        l = self.semantic_stack.pop()
        self.add_to_program_block(f'(ASSIGN, {l}, {t}, )')
        return_address = self.symbol_table[self.function]['return_address']
        self.add_to_program_block(f'(JP, @{return_address}, , )')



    def add_to_program_block(self, str):
        print('------------------->>', str, 'added.')
        self.program_block.append(str)

# arg type check


# temp_args = [
#     [arg, {'addr': 2, 'data_type': 'void/int', 'type': 'var/arr'}],
#     [arg, {'addr': 2, 'data_type': 'void/int', 'type': 'var/arr'}],
# ]

# test  1: 1 func                            done
# test  2: 1 func                            done
# test  3: switch, 1 func                    done
# test  4: while break, inner func
# test  5: array argument, 1 func
# test  6: 1 func                            done
# test  7: switch, 1 func                    done
# test  8: 1 func, global arr used in func   done
# test  9: inner func, array argument
# test 10: while break, inner func
