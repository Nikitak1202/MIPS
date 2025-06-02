class RegFile:
    def __init__(self):
        # Create 32 registers
        self.regs = [0] * 32
        self.regs[29] = 0x1000000    # SP 
        self.regs[31] = 0xFFFFFFFF   # LR 

    def read(self, reg_num):
        return self.regs[reg_num]

    def write(self, reg_num, value):
        if reg_num == 0:
            return
        print(f"I'm writting {value} into {reg_num}")
        self.regs[reg_num] = value