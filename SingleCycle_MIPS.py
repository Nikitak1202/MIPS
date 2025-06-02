from InstMemory import InstMemory
from RegFile import RegFile
from DataMemory import DataMemory
from InstParser import InstParser
from ControlUnit import ControlUnit
from ALU import ALU
from SignExtend import SignExtend
from Mux import Mux

HALT_PC = 0xFFFFFFFF
CYCLE_DURATION = 10 # (ns) it is determined by the sum of delays of all stages
PC = 0
PC_BEYOND_LIMIT = False

# Initialize counters for statistics.
total_instructions = 0
num_rtype = 0
num_itype = 0
num_jtype = 0
num_mem_access = 0
num_taken_branches = 0
num_cycles = 0

# Instantiate all hardware components.
#InstMemory  = InstMemory("factorial.bin") # Input file for the computing 4th factorial. 
#InstMemory  = InstMemory("summation.bin") # Input file for the summation 1-10.
InstMemory  = InstMemory("input.bin")  # General input file for thr testing all implemented instructions.
RegFile     = RegFile()                # 32 registers, with SP (r29) and LR (r31) pre-initialized.
DataMemory  = DataMemory()             # Data memory block.
InstParser  = InstParser()             # Parses a 32-bit instruction into its fields.
ControlUnit = ControlUnit()            # Generates control signals based on opCode & funct.
ALU         = ALU()                    # The arithmetic and logic unit.
SignExtend  = SignExtend()             # Sign extends 16-bit immediates to 32 bits.

while PC != HALT_PC and PC_BEYOND_LIMIT != True:
    # ---------------------------
    # Instruction Fetch & Decode
    # ---------------------------
    if (PC // 4) >= len(InstMemory.instructions):
        print("WARNING: PC is BEYOND the LIMIT!!!")
        break

    current_instr_str = InstMemory.instructions[PC // 4]
    current_instr = int(current_instr_str, 16)
    
    InstParser.parse(current_instr)
    
    # ---------------------------
    # Control Signal Generation
    # ---------------------------
    ControlUnit.opCode = InstParser.opCode
    ControlUnit.funct  = InstParser.funct
    ControlUnit.generate_signals()  
    print(f"PC = {PC}, Instruction: {ControlUnit.InstrName}")

    # Statistics collecting
    if ControlUnit.opCode == 0:
        num_rtype += 1
    elif ControlUnit.opCode in [0x08, 0x23, 0x2B, 0x04]:
        num_itype += 1
    elif ControlUnit.opCode in [0x02, 0x03]:
        num_jtype += 1
    if ControlUnit.opCode in [0x23, 0x2B]:
        num_mem_access += 1

    # ---------------------------
    # Register File Read
    # ---------------------------
    ALU.A = RegFile.read(InstParser.rs)  
    
    # ---------------------------
    # Sign Extension of Immediate
    # ---------------------------
    SignExtend.input = InstParser.immediate 
    SignExtend.extend()  
    
    # ---------------------------
    # ALUSrc MUX: Select second ALU operand
    # ---------------------------
    ALUSrc_MUX = Mux()
    ALUSrc_MUX.input0 = RegFile.read(InstParser.rt)             
    ALUSrc_MUX.input1 = SignExtend.output      
    ALUSrc_MUX.select = ControlUnit.ALUSrc     # 0 → register, 1 → immediate.
    ALUSrc_MUX.evaluate()
    ALU.B = ALUSrc_MUX.output  

    # ---------------------------
    # ALU Operation
    # ---------------------------
    ALU.ALUOp = ControlUnit.ALUOp  
    ALU.operate()      
    print(ALU.operation)           

    # ---------------------------
    # RegDst MUX: Select destination register number
    # ---------------------------
    RegDst_MUX = Mux()
    RegDst_MUX.input0 = InstParser.rt    
    RegDst_MUX.input1 = InstParser.rd    
    RegDst_MUX.select = ControlUnit.RegDst  # 0 → rt, 1 → rd.
    RegDst_MUX.evaluate()

    # ---------------------------
    # Writeback MUX: Select data to write back to register file
    # ---------------------------
    Result_MUX = Mux()
    Result_MUX.input0 = ALU.result       
    Result_MUX.input1 = DataMemory.read_word(ALU.result, ControlUnit.MemRead)
    Result_MUX.select = ControlUnit.MemtoReg  # 0 → ALU result, 1 → memory data.
    Result_MUX.evaluate()

    # ---------------------------
    # Write Back: Update register file if RegWrite is enabled
    # ---------------------------
    RegFile.write(RegDst_MUX.output, Result_MUX.output)

    # ---------------------------
    # Memory Write: Update Data Memory if MemWrite is enabled
    # ---------------------------
    DataMemory.write_word(ALU.result, RegFile.read(InstParser.rt), ControlUnit.MemWrite)
    
    # ---------------------------
    # Next PC: Determine next PC using branch and jump Mux blocks.
    # ---------------------------
    next_pc = PC + 4
    branch_target = next_pc + (SignExtend.output << 2)  
    jump_target = ((next_pc) & 0xF0000000) | (InstParser.address << 2)
    
    Branch_MUX = Mux()
    Branch_MUX.input0 = next_pc
    Branch_MUX.input1 = branch_target
    Branch_MUX.select = 1 if (ControlUnit.Branch and ALU.zero) else 0
    Branch_MUX.evaluate()

    if ControlUnit.Branch and ALU.zero:
        num_taken_branches += 1
        print("Branch is taken")
    
    Jump_MUX = Mux()
    Jump_MUX.input0 = Branch_MUX.output
    Jump_MUX.input1 = jump_target
    Jump_MUX.select = ControlUnit.Jump
    Jump_MUX.evaluate()
    
    PC = Jump_MUX.output

    # Saving Link for jal and jalr 
    if ControlUnit.opCode == 0x03 or ControlUnit.funct == 0x09:
        RegFile.write(31, next_pc)

    # Update PC for jr and jalr
    if InstParser.funct in [0x08, 0x09] and InstParser.opCode == 0x0: 
        PC = RegFile.read(InstParser.rs)
    # ---------------------------
    # Print Architectural State
    # ---------------------------
    total_instructions += 1
    PC_BEYOND_LIMIT = (PC // 4) >= len(InstMemory.instructions)
    if PC_BEYOND_LIMIT:
        print("WARNING: PC is BEYOND the LIMIT!!!")

    print(f"Updated PC: {PC}")
    print("Register file state:")
    for idx, val in enumerate(RegFile.regs):
        print(f"  R{idx:02d}: 0x{val:08X}", end="\t")
        if (idx + 1) % 4 == 0:
            print()
    print("\nMemory state (only non-zero cells):")
    for i, word in enumerate(DataMemory.memory):
        if word != 0:
            print(f"  Address: 0x{i*4:08X}  Value: 0x{word:08X}")
    print("----------------------------\n")
    num_cycles += 1


print(f"Number of cycles: {num_cycles}")
print(f"Execution time = num_cycles * CYCLE_DURATION = {num_cycles * CYCLE_DURATION}ns")
print(f"Total instructions executed: {total_instructions}")
print(f"Number of R-type instructions: {num_rtype}")
print(f"Number of I-type instructions: {num_itype}")
print(f"Number of J-type instructions: {num_jtype}")
print(f"Number of memory access instructions: {num_mem_access}")
print(f"Number of taken branches: {num_taken_branches}")
print(f"Final return value (R2): 0x{RegFile.read(2):08X}")