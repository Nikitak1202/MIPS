import struct

# Instruction format functions (R-type, I-type, J-type)
def rtype_instruction(rs, rt, rd, shamt, funct):
    # Build R-type instruction (opcode=0)
    opcode = 0
    return (opcode << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (shamt << 6) | funct

def itype_instruction(opcode, rs, rt, immediate):
    # Build I-type instruction with 16-bit immediate
    return (opcode << 26) | (rs << 21) | (rt << 16) | (immediate & 0xFFFF)

def jtype_instruction(opcode, address):
    # Build J-type instruction with 26-bit address
    return (opcode << 26) | (address & 0x3FFFFFF)


# Example instructions (for demonstration)
r_instr1 = rtype_instruction(21, 8, 11,  0, 0x20)   # add 
r_instr2 = rtype_instruction(11, 21, 14, 0, 0x24)    # and
r_instr3 = rtype_instruction(12, 21, 11, 0, 0x22)    # sub  
r_instr4 = rtype_instruction(21, 11, 17, 0, 0x25)    # or  
r_instr5 = rtype_instruction(22, 21, 20, 0, 0x2A)    # slt 

i_instr1 = itype_instruction(0x08, 0, 5, 10)         # addi: r5 = 10
i_instr2 = itype_instruction(0x2B, 5, 5, 2)         # sw: store r5 to memory at offset 4
i_instr3 = itype_instruction(0x23, 5, 8, 2)          # lw: load from memory at offset 4 to r8
i_instr4 = itype_instruction(0x08, 8, 11, 5)        # addi
  
instructions = [
    i_instr1, i_instr2, i_instr3, i_instr4, i_instr3,
    r_instr1, r_instr2, r_instr3, r_instr4, r_instr5
    ] 

# Save example instructions to a binary file (big-endian format)
with open('input.bin', 'wb') as f:
    for instr in instructions:
        f.write(struct.pack('>I', instr))


def create_summation_program(filename):
    """
    Registers:
        r2 <- sum (final result)
        r1 <- current addend (starts at 1)
        r3 <- loop counter (initialized to 10)
    Loop:
        r2 = r2 + r1, r1++, r3--, and repeat until r3 becomes zero.
        Then return (jr r31).
    """
    instructions = []
    instructions.append(itype_instruction(0x08, 0, 2, 0))    # r2 = 0 (initialize sum)
    instructions.append(itype_instruction(0x08, 0, 1, 1))    # r1 = 1 (initial addend)
    instructions.append(itype_instruction(0x08, 0, 3, 10))   # r3 = 10 (loop counter)
    instructions.append(rtype_instruction(2, 1, 2, 0, 0x20)) # r2 = r2 + r1
    instructions.append(itype_instruction(0x08, 1, 1, 1))    # r1 = r1 + 1
    instructions.append(itype_instruction(0x08, 3, 3, -1))   # r3 = r3 - 1
    instructions.append(itype_instruction(0x04, 3, 0, 1))    # if (r3 == 0) branch to exit (offset=1)
    instructions.append(jtype_instruction(0x02, 3))          # jump to loop start (instruction index 3)
    instructions.append(rtype_instruction(31, 0, 0, 0, 0x08))# jr r31 (return)

    with open(filename, 'wb') as f:
        for instr in instructions:
            f.write(struct.pack('>I', instr))


def create_factorial_program(filename):
    """
    Registers:
        r2 <- result (final factorial, initialized to 1)
        r1 <- multiplier (starts at 2)
        r5 <- iteration counter (3 multiplications: by 2,3,4)
        r4 <- accumulator for repeated addition (multiplication)
        r3 <- temporary copy of multiplier for inner loop
    For each multiplication, the accumulator adds the current result repeatedly.
    """
    instructions = []
    instructions.append(itype_instruction(0x08, 0, 2, 1))    # r2 = 1 (initialize result)
    instructions.append(itype_instruction(0x08, 0, 1, 2))    # r1 = 2 (initialize multiplier)
    instructions.append(itype_instruction(0x08, 0, 5, 3))    # r5 = 3 (iteration counter)
    instructions.append(itype_instruction(0x08, 0, 4, 0))    # r4 = 0 (initialize accumulator)
    instructions.append(itype_instruction(0x08, 1, 3, 0))    # r3 = r1 (copy multiplier to r3)
    instructions.append(rtype_instruction(4, 2, 4, 0, 0x20)) # r4 = r4 + r2 (accumulator += result)
    instructions.append(itype_instruction(0x08, 3, 3, -1))   # r3 = r3 - 1
    instructions.append(itype_instruction(0x04, 3, 0, 1))    # if (r3 == 0) branch to update result (offset=1)
    instructions.append(jtype_instruction(0x02, 5))          # jump back to inner loop (instruction index 5)
    instructions.append(itype_instruction(0x08, 4, 2, 0))    # r2 = r4 (update result with accumulator)
    instructions.append(itype_instruction(0x08, 1, 1, 1))    # r1 = r1 + 1 (increment multiplier)
    instructions.append(itype_instruction(0x08, 5, 5, -1))   # r5 = r5 - 1 (decrement iteration counter)
    instructions.append(itype_instruction(0x04, 5, 0, 1))    # if (r5 == 0) branch to done (offset=1)
    instructions.append(jtype_instruction(0x02, 3))          # jump to outer loop start (instruction index 3)
    instructions.append(rtype_instruction(31, 0, 0, 0, 0x08))# jr r31 (return)

    with open(filename, 'wb') as f:
        for instr in instructions:
            f.write(struct.pack('>I', instr))


def create_sort_program(filename: str):
    code = []

    # ---------------------------------------------------------------------
    # ①  Initial unsorted integers
    #     addr  0 ← 7,  addr  4 ← 2,  addr  8 ← 5,  addr 12 ← 1
    #     addr 16 ← 4,  addr 20 ← 6,  addr 24 ← 0,  addr 28 ← 3
    # ---------------------------------------------------------------------
    init_values = [7, 6, 5, 4, 3, 2, 1]  # Initial values in descending order
    for idx, val in enumerate(init_values):
        code += [
            itype_instruction(0x08, 0, 2, val),      # addi r2, r0, imm
            itype_instruction(0x2B, 0, 2, idx * 4)   # sw   r2, offset(r0)
        ]

    # helper : compare–swap memory words at addresses A,B
    def cmp_swap(addr_a, addr_b):
        nonlocal code
        code += [
            itype_instruction(0x23, 0, 2, addr_a),   # lw r2, A(r0)
            itype_instruction(0x23, 0, 3, addr_b),   # lw r3, B(r0)
            rtype_instruction(3, 2, 4, 0, 0x2A),     # slt r4, r3, r2  (B<A?)
            itype_instruction(0x04, 4, 0, 2),        # beq r4,r0,+2    (skip if ordered)
            itype_instruction(0x2B, 0, 3, addr_a),   # sw r3, A(r0)
            itype_instruction(0x2B, 0, 2, addr_b),   # sw r2, B(r0)
        ]

    # ---------------------------------------------------------------------
    # ②  Unrolled bubble-sort for 7 elements
    #     Pass-k performs (8-k) adjacent compare-swaps
    # ---------------------------------------------------------------------
    addr = [i * 4 for i in range(8)]

    # pass-1  → 7 swaps
    for i in range(7): cmp_swap(addr[i], addr[i+1])

    # pass-2  → 6 swaps
    for i in range(6): cmp_swap(addr[i], addr[i+1])

    # pass-3  → 5 swaps
    for i in range(5): cmp_swap(addr[i], addr[i+1])

    # pass-4  → 4 swaps
    for i in range(4): cmp_swap(addr[i], addr[i+1])

    # pass-5  → 3 swaps
    for i in range(3): cmp_swap(addr[i], addr[i+1])

    # pass-6  → 2 swaps
    for i in range(2): cmp_swap(addr[i], addr[i+1])

    # pass-7  → 1 swap
    cmp_swap(addr[0], addr[1])

    # ---------------------------------------------------------------------
    # ③  return
    # ---------------------------------------------------------------------
    code.append(rtype_instruction(31, 0, 0, 0, 0x08))  # jr r31

    # ---------------------------------------------------------------------
    # ④  write big-endian binary file
    # ---------------------------------------------------------------------
    import struct
    with open(filename, "wb") as f:
        for instr in code:
            f.write(struct.pack(">I", instr))


# Generate binary files for both programs
create_summation_program('summation.bin')
create_factorial_program('factorial.bin')
create_sort_program("sort.bin")