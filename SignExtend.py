class SignExtend:
    def __init__(self):
        self.input = 0         # 16-bit value (unsigned representation)
        self.output = 0        # 32-bit signed value

    def extend(self):
        # Mask to get the lower 16 bits
        raw = self.input & 0xFFFF
        # If the sign bit (bit 15) is set, subtract 2^16 to obtain a negative value
        if raw & (1 << 15):
            self.output = raw - (1 << 16)
        else:
            self.output = raw