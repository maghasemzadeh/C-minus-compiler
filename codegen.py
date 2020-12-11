class Codegen:
    def __init__(self):
        self.semantic_stack = []
        self.program_block = []
        self.cur_temp = 1000
        self.cur_mem_addr = 500
        self.action_symbols = {
            'pid': self.pid,
            'pnum': self.pnum,
            'array_address': self.array_address,
            'assign': self.assign,
            'add': self.add,
            'mult': self.mult,
            'lt': self.lt,
            'eq': self.eq
        }

    def find_addr(self):
        t = self.cur_mem_addr
        self.cur_mem_addr += 4
        return t

    def get_temp(self):
        t = self.cur_temp
        self.cur_temp += 4
        return t
        
    def codegen(self, action_symbol, arg=None):
        self.action_symbols[action_symbol](arg)
            
    def pid(self, arg):
        # todo symbol table
        addr = self.find_addr()
        self.semantic_stack.append(addr)

    def pnum(self, arg):
        num = '#' + str(arg)
        self.semantic_stack.append(num)

    def array_address(self, arg=None):
        pass

    def assign(self, arg=None):
        pass

    def add(self, arg=None):
        pass

    def mult(self, arg=None):
        pass

    def lt(self, arg=None):
        pass

    def eq(self, arg=None):
        pass