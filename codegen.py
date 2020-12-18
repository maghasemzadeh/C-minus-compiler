class Codegen:
    def __init__(self):
        self.semantic_stack = []
        self.program_block = []
        self.cur_temp = 1000
        self.temp = {}
        self.cur_mem_addr = 500
        self.memory = {}
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
            'save_arr': self.save_arr
        }
        self.arg_actions = ['pid', 'pnum', 'sign', 'relop_sign']

    def find_addr(self):
        t = self.cur_mem_addr
        self.cur_mem_addr += 4
        return t

    def get_temp(self):
        t = self.cur_temp
        self.cur_temp += 4
        return t

    def generate(self, action_symbol, arg=None):
        self.action_symbols[action_symbol[1:]](arg)
        print(f'{action_symbol[1:]}({arg})\r\t\t-> {str(self.semantic_stack)[:-1]}')

    def pid(self, arg):
        # TODO symbol table
        addr = self.find_addr()
        self.memory.update({addr: arg})
        self.semantic_stack.append(addr)

    def pnum(self, arg):
        num_addr = self.get_temp()
        self.temp.update({num_addr: arg})
        self.semantic_stack.append(num_addr)

    def array_address(self, arg=None):
        index = self.semantic_stack.pop()
        var_addr = self.semantic_stack.pop()
        index = index * 4
        var_addr += index
        self.semantic_stack.append(var_addr)

    def assign(self, arg=None):
        op2 = self.semantic_stack.pop()
        op1 = self.semantic_stack.pop()
        self.program_block.append(f'(ASSIGN, {op1}, {op2}, )')
        t = self.get_temp()
        self.semantic_stack.append(t)
        self.temp[t] = op1 

    def whil(self, arg=None):
        i = len(self.program_block)
        self.program_block[self.semantic_stack[-1]] = f'(JPF, {self.semantic_stack[-2]}, {i+1}, )'
        self.program_block.append(f'(JP, {self.semantic_stack[-3]+1}, , )')
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
            self.program_block.append(f'(SUB, {op1}, {op2}, {t})')

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
        self.program_block[pb_ind] = f'(JPF, {if_exp}, {i+1},)'
        self.semantic_stack.append(i)
        self.program_block.append('')

    def jp(self, arg=None):
        pb_ind = self.semantic_stack.pop()
        i = len(self.program_block)
        self.program_block[pb_ind] = f'(JP, {i}, ,)'

    def label(self, arg=None):
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
        number = self.semantic_stack.pop()
        sign = self.semantic_stack.pop()
        if sign == '-':
            self.semantic_stack.append(-number)
        else:
            self.semantic_stack.append(number)

    def save_program_block(self):
        with open('output.txt', 'w') as output:
            for i, block in enumerate(self.program_block):
                output.write(f'{i}\t{block}\n')


    def pop(self, arg=None):
        self.semantic_stack.pop()


    def output(self, arg=None):
        to_print = self.semantic_stack.pop()
        self.program_block.append(f'(PRINT, {to_print}, , )')

    def save_arr(self, arg=None):
        # TODO save size of array
        pass
