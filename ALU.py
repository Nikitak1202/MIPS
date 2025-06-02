class ALU:
    def __init__(self):
        self.A         = 0         # First 32-bit data input
        self.B         = 0         # Second 32-bit data input
        self.ALUOp     = None  # Operation control signal
        self.result    = 0    # 32-bit result
        self.zero      = False  # Zero flag
        self.operation = 'NOP'

    def operate(self):
        # R-type ALU operations based on ALUOp
        if self.ALUOp == 0x20:    # add
            self.result = self.A + self.B
            self.operation = f"Operation: ADD: {self.A} + {self.B} = {self.result}"

        elif self.ALUOp == 0x22:  # sub
            self.result = self.A - self.B
            self.operation = f"Operation: SUB: {self.A} - {self.B} = {self.result}"

        elif self.ALUOp == 0x24:  # and
            self.result = self.A & self.B
            self.operation = f"Operation: AND: {self.A} & {self.B} = {self.result}"

        elif self.ALUOp == 0x25:  # or
            self.result = self.A | self.B
            self.operation = f"Operation: OR: {self.A} | {self.B} = {self.result}"

        elif self.ALUOp == 0x2A:  # slt
            self.result = 1 if self.A < self.B else 0
            self.operation = f"Operation: SLT: ({self.A} < {self.B}) results in {self.result}"

        elif self.ALUOp == 0x00:  # sll (shift left logical)
            # Using the lower 5 bits of B as shift amount
            shift_amt = self.B & 0x1F
            self.result = self.A << shift_amt
            self.operation = f"Operation: SLL: {self.A} << {shift_amt} = {self.result}"

        elif self.ALUOp == 0x02:  # srl (shift right logical)
            shift_amt = self.B & 0x1F
            self.result = (self.A % 0x100000000) >> shift_amt  # logical shift
            self.operation = f"Operation: SRL: {self.A} >> {shift_amt} = {self.result}"

        else:
            self.operation = "WARNING!!! Unknown operation in ALU!"
        
        # Set the zero flag based on the result
        self.zero = (self.result == 0)