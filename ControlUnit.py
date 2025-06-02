class ControlUnit:
    def __init__(self):
        # Inputs
        self.opCode = 0
        self.funct  = 0
        # Outputs (control signals)
        self.ALUOp    = None
        self.RegDst   = 0
        self.ALUSrc   = 0
        self.MemtoReg = 0
        self.RegWrite = 0
        self.MemRead  = 0
        self.MemWrite = 0
        self.Branch   = 0
        self.Jump     = 0
        self.JumpReg  = 0
        self.InstrName = 'NOP'

    def generate_signals(self):
        if self.opCode == 0:  # R-type instructions
            r_type_instructions = {
                0x20: 'add',
                0x22: 'sub',
                0x24: 'and',
                0x25: 'or',
                0x2A: 'slt',
                0x00: 'sll',
                0x02: 'srl',
                0x08: 'jr',
                0x10: 'NOP',
                0x09: 'jalr'
            }
            self.InstrName = r_type_instructions.get(self.funct, 0)
            #print(f"Executing R-type instruction: {self.InstrName}")
            self.RegDst   = 1
            self.ALUSrc   = 0
            self.MemtoReg = 0
            self.RegWrite = 1
            self.MemRead  = 0
            self.MemWrite = 0
            self.Branch   = 0
            self.Jump     = 1 if self.funct in [0x09, 0x08] else 0
            self.JumpReg  = 1 if self.funct in [0x09, 0x08] else 0
            self.ALUOp    = self.funct

        elif self.opCode == 0x08:  # addi
            self.InstrName = 'addi'
            #print(f"Executing {self.InstrName} instruction")
            self.RegDst   = 0
            self.ALUSrc   = 1
            self.MemtoReg = 0
            self.RegWrite = 1
            self.MemRead  = 0
            self.MemWrite = 0
            self.Branch   = 0
            self.Jump     = 0
            self.JumpReg  = 0
            self.ALUOp    = 0x20

        elif self.opCode == 0x23:  # lw
            self.InstrName = 'lw'
            #print(f"Executing {self.InstrName} instruction")
            self.RegDst   = 0
            self.ALUSrc   = 1
            self.MemtoReg = 1
            self.RegWrite = 1
            self.MemRead  = 1
            self.MemWrite = 0
            self.Branch   = 0
            self.Jump     = 0
            self.JumpReg  = 0
            self.ALUOp    = 0x20

        elif self.opCode == 0x2B:  # sw
            self.InstrName = 'sw'
            #print(f"Executing {self.InstrName} instruction")
            self.RegDst   = None
            self.ALUSrc   = 1
            self.MemtoReg = None
            self.RegWrite = 0
            self.MemRead  = 0
            self.MemWrite = 1
            self.Branch   = 0
            self.Jump     = 0
            self.JumpReg  = 0
            self.ALUOp    = 0x20

        elif self.opCode == 0x04:  # beq
            self.InstrName = 'beq'
            #print(f"Executing {self.InstrName} instruction")
            self.RegDst   = None
            self.ALUSrc   = 0
            self.MemtoReg = None
            self.RegWrite = 0
            self.MemRead  = 0
            self.MemWrite = 0
            self.Branch   = 1
            self.Jump     = 0
            self.JumpReg  = 0
            self.ALUOp    = 0x22

        elif self.opCode == 0x02:  # j
            self.InstrName = 'j'
            #print(f"Executing {self.InstrName} instruction")
            self.RegDst   = None
            self.ALUSrc   = None
            self.MemtoReg = None
            self.RegWrite = 0
            self.MemRead  = 0
            self.MemWrite = 0
            self.Branch   = 0
            self.Jump     = 1
            self.JumpReg  = 0
            self.ALUOp    = None

        elif self.opCode == 0x03:  # jal
            self.InstrName = 'jal'
            #print(f"Executing {self.InstrName} instruction")
            self.RegDst   = None
            self.ALUSrc   = None
            self.MemtoReg = None
            self.RegWrite = 1
            self.MemRead  = 0
            self.MemWrite = 0
            self.Branch   = 0
            self.Jump     = 1
            self.JumpReg  = 0
            self.ALUOp    = None

        else:
            self.InstrName = 'unknown'
            #print("WARNING!!! Unknown opCode:", self.opCode)
            self.RegDst   = 0
            self.ALUSrc   = 0
            self.MemtoReg = 0
            self.RegWrite = 0
            self.MemRead  = 0
            self.MemWrite = 0
            self.Branch   = 0
            self.Jump     = 0
            self.JumpReg  = 0
            self.ALUOp    = 0