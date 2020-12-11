class Codegen:
    def __init__(self):
        self.semantic_stack = []
        self.program_block = []
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
        
    def codegen(self, action_symbol, arg=None):
        self.action_symbols[action_symbol](arg)
            
    def pid(self, arg):
        pass

    def pnum(self, arg):
        pass

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