class InstParser:
    def __init__(self):
        # Parsed fields
        self.opCode = None   # 6 bits
        self.rs = None       # 5 bits
        self.rt = None       # 5 bits
        self.rd = None       # 5 bits (only for R-type)
        self.shamt = None    # 5 bits (only for R-type)
        self.funct = None    # 6 bits (only for R-type)
        self.immediate = None  # 16 bits (for I-type)
        self.address = None    # 26 bits (for J-type)

    def parse(self, instr):
        # instr is assumed to be a 32-bit integer.
        self.opCode = (instr >> 26) & 0x3F
        self.rs = (instr >> 21) & 0x1F
        self.rt = (instr >> 16) & 0x1F
        self.rd = (instr >> 11) & 0x1F
        self.shamt = (instr >> 6) & 0x1F
        self.funct = instr & 0x3F
        self.immediate = instr & 0xFFFF
        self.address = instr & 0x3FFFFFF