class DataMemory:
    def __init__(self, size_in_bytes=0x400000):
        # Memory is byte-addressed. Store words (32 bits) in a list.
        self.size = size_in_bytes // 4
        self.memory = [0] * self.size

    def read_word(self, address, MemRead):
        if MemRead:
            if address % 4 != 0 or address // 4 >= self.size:
                print("MEMORY READ ERROR: unaligned or out-of-bounds")
                return 0
            return self.memory[address // 4]
        else:
            return 0
        

    def write_word(self, address, data, MemWrite):
        if MemWrite:
            if address % 4 != 0 or address // 4 >= self.size:
                print("WARNING!!!")
                print("Memory write error: unaligned or out-of-bounds")
            self.memory[address // 4] = data