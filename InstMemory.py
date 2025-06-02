import struct


class InstMemory:
    def __init__(self, filename):
        self.instructions = []  # List of instructions
        self.load_file(filename)

    def load_file(self, filename):
        # Read the binary file and store each 32-bit word as a hex number.
        with open(filename, 'rb') as f:
            while True:
                word = f.read(4)
                if not word or len(word) < 4:
                    break
                # Unpack as unsigned int (big-endian) and store in hex form.
                (instr,) = struct.unpack('>I', word)
                self.instructions.append(hex(instr))