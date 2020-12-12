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
        self.memory.update({addr: arg})
        self.semantic_stack.append(addr)

    def pnum(self, arg):
        num_addr = self.get_temp()
        self.temp.update({num_addr: arg})
        self.semantic_stack.append(num_addr)

    def array_address(self, arg=None):
        pass

    def assign(self, arg=None):
        pass

    def add(self, arg=None):
        pass

    def mult(self, arg=None):
        pass

    def save(self, arg=None):
        pass

    def jpf(self, arg=None):
        pass

    def jp(self, arg=None):
        pass

    def label(self, arg=None):
        pass

    def relop(self, arg=None):
        pass

    def relop_sign(self, arg=None):
        pass

    def sign(self, arg=None):
        pass

    def signed_num(self, arg=None):
        pass
