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
jalr_instr = rtype_instruction(2, 0, 31, 0, 0x09)
jr_instr   = rtype_instruction(1, 0, 0, 0, 0x08)

i_instr1 = itype_instruction(0x08, 0, 5, 10)         # addi: r5 = 10
i_instr2 = itype_instruction(0x2B, 5, 21, 4)         # sw: store r5 to memory at offset 4
i_instr3 = itype_instruction(0x23, 5, 8, 4)          # lw: load from memory at offset 4 to r8
i_instr4 = itype_instruction(0x04, 14, 21, 10)       # beq 
i_instr5 = itype_instruction(0x04, 14, 21, 9)        # beq 
i_instr6 = itype_instruction(0x04, 10, 11, 1)        # beq 
i_instr7 = itype_instruction(0x08, 8, 11, 5)        # addi
i_instr8 = itype_instruction(0x04, 10, 11, -2)       # beq 
i_instr9 = itype_instruction(0x08, 1, 1, 72)         # addi 
i_instr10 = itype_instruction(0x08, 2, 2, 84)        # addi 

j_instr1 = jtype_instruction(0x02, 0x03)             # j
j_instr2 = jtype_instruction(0x03, 0xF)              # jal
  
instructions = [
    i_instr1, i_instr2, i_instr3, i_instr7, i_instr3,
    r_instr1, r_instr2, r_instr3, r_instr5
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


# Generate binary files for both programs
create_summation_program('summation.bin')
create_factorial_program('factorial.bin')