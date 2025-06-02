from InstMemory import InstMemory
from RegFile import RegFile
from DataMemory import DataMemory
from InstParser import InstParser
from ControlUnit import ControlUnit
from ALU import ALU
from SignExtend import SignExtend
from Mux import Mux
from Latch import Latch
from ForwardUnit import ForwardUnit
from StatePrinter import StatePrinter


# System state variables
HALT_PC         = 0xFFFFFFFF
PC              = 0
CYCLE_DURATION  = 2 # (ns) it is determined by the delay of the longest stage 
PC_BEYOND_LIMIT = False

# Initialize counters for statistics.
total_instructions = 0
num_rtype          = 0
num_itype          = 0
num_jtype          = 0
num_mem_access     = 0
num_taken_branches = 0
num_cycles         = 0
# Flag of amount of cycles to wait after fetching last one to let instructions inside the pipeline to finish
cycles_left        = 2   
cycles_left_count  = 0

# Instantiate all hardware components.
InstMemory  = InstMemory("factorial.bin") # Input file for the computing 4th factorial. 
#InstMemory  = InstMemory("summation.bin") # Input file for the summation 1-10.
#InstMemory   = InstMemory("input.bin")  
RegFile      = RegFile()                
DataMemory   = DataMemory()             
InstParser   = InstParser()             
ControlUnit  = ControlUnit()            
ALU          = ALU()                    
SignExtend   = SignExtend()   
ForwardUnit  = ForwardUnit()    

ALUSrc_MUX     = Mux()
RegDst_MUX     = Mux()
Result_MUX     = Mux()
Branch_MUX     = Mux()
Jump_MUX       = Mux()
Jump_Reg_MUX   = Mux()
BypassL0A_MUX  = Mux()
BypassL0B_MUX  = Mux()
BypassL1A_MUX  = Mux()
BypassL1B_MUX  = Mux()
LW_BypassA_MUX = Mux()
LW_BypassB_MUX = Mux()
SW_Bypass0_MUX = Mux()
SW_Bypass1_MUX = Mux()


FD           = Latch(["PC4", "Instr"])

DE           = Latch(['RegDst'  , 'Branch', 'MemRead' , 'MemtoReg', 'ALUOp' , 'MemWrite', 'ALUSrc', 'rt', 'rs', 'rd', 
                      'RegWrite', 'PC4'   , 'RegRead1', 'RegRead2', 'ImmExt', 'Jump'    , 'Addres', 'JumpReg' , 'InstrName'])

EM           = Latch(['Jump'     , 'RegDst'  , 'MemRead'    , 'MemtoReg'    , 'MemWrite' ,  'RegWrite', 'rt', 'rd', 'PC4',
                      'ALUResult', 'RegRead2', 'BranchTaken', 'BranchTarget', 'JumpTarget', 'RegRead1', 'JumpReg', 'InstrName'])

MW           = Latch(['RegRead2' ,  'MemData', 'MemtoReg', 'RegWrite', 'PC4',
                      'ALUResult', 'rt', 'rd', 'RegDst'  , 'InstrName'])

printer = StatePrinter()


while PC != HALT_PC and PC_BEYOND_LIMIT != True:
    # ---------------------------
    # Write Back
    # ---------------------------
    # Writeback MUX: Select data to write back to register file
    Result_MUX.input0 = MW.output.ALUResult      
    Result_MUX.input1 = MW.output.MemData
    Result_MUX.select = MW.output.MemtoReg
    Result_MUX.evaluate()

    # RegDst MUX: Select destination register number
    RegDst_MUX.input0 = MW.output.rt    
    RegDst_MUX.input1 = MW.output.rd    
    RegDst_MUX.select = MW.output.RegDst
    RegDst_MUX.evaluate()

    # Write Back: Update register file if RegWrite is enabled
    if MW.output.RegWrite:
        RegFile.write(RegDst_MUX.output, Result_MUX.output)

    # Collect WB stage data
    if MW.output.PC4 != 0 and MW.output.InstrName != "NOP":
        printer.collect_wb(
            pc=MW.output.PC4 - 4,
            instr_name=MW.output.InstrName,
            memto_reg=MW.output.MemtoReg,
            result=Result_MUX.output,
            target_reg=RegDst_MUX.output
        )
    else:
        printer.wb_stage = {}  # Stage not active

    # ---------------------------
    # Instruction Fetch
    # ---------------------------
    # NEXT PC CALCULATION
    # Branch MUX
    Branch_MUX.input0 = PC
    Branch_MUX.input1 = EM.output.BranchTarget
    Branch_MUX.select = 1 if EM.output.BranchTaken else 0
    Branch_MUX.evaluate()

    # Jump MUX
    Jump_MUX.input0 = Branch_MUX.output
    Jump_MUX.input1 = EM.output.JumpTarget
    Jump_MUX.select = EM.output.Jump
    Jump_MUX.evaluate()

    # Jump Register MUX (jr or jalr)
    Jump_Reg_MUX.input0 = Jump_MUX.output
    Jump_Reg_MUX.input1 = EM.output.RegRead1
    Jump_Reg_MUX.select = EM.output.JumpReg
    Jump_Reg_MUX.evaluate()
    PC = Jump_Reg_MUX.output

    # PC check
    current_instr_str = None
    if (PC // 4) == len(InstMemory.instructions):
        print("WARNING: PC is BEYOND the LIMIT!!!")
        current_instr = 0x00000010 # NOP
        if ControlUnit.InstrName in ['add', 'sub', 'or', 'and', 'sw', 'lw', 'slt', 'srl', 'sll']:
            cycles_left = 3
        elif ControlUnit.InstrName in ['jr', 'jalr', 'j', 'jal', 'beq']:
            cycles_left = 1
        else:
            cycles_left = 0

    if cycles_left != 2:
        if cycles_left == cycles_left_count:
            PC_BEYOND_LIMIT = True
        else:
            cycles_left_count += 1
    else: # Fetching 
        current_instr_str = InstMemory.instructions[(PC // 4)]
        current_instr = int(current_instr_str, 16)
        print(f"PC: 0x{PC:08X}, Instruction: {current_instr_str} (binary: {current_instr:032b})")
    
    # Write to the Latch
    FD.input.PC4   = PC + 4
    FD.input.Instr = current_instr if 'current_instr' in locals() else 0

    # Collect IF stage data
    if 'current_instr' in locals() and current_instr != 0:
        printer.collect_if(
            pc=PC,
            instr_str=current_instr_str,
            instr_bin=current_instr
        )
    else:
        printer.if_stage = {}  # Stage not active

    # PC increasing
    PC += 4

    # Stats and branch\jump affected Latches handling
    if EM.output.BranchTaken:
        DE.flush()
        EM.flush()
        FD.EN = True
        num_taken_branches += 1
        print('Branch is taken')

    elif EM.output.Jump:
        FD.EN = True
        DE.EN = True
        print('Jump occured')


    # ---------------------------
    # Instruction Decode
    # ---------------------------
    InstParser.parse(FD.output.Instr)

    # Control Signals Generation
    ControlUnit.opCode = InstParser.opCode
    ControlUnit.funct  = InstParser.funct
    ControlUnit.generate_signals()  

    # JUMP CASE: disable previous stage Latch
    if ControlUnit.Jump:
        FD.EN = False
        PC -= 4  # Adjust PC to prevent fetching the next instruction
        cycles_left        = 2   
        cycles_left_count  = 0

    # Sign Extension of Immediate
    SignExtend.input = InstParser.immediate 
    SignExtend.extend() 

    # Saving Link for jal and jalr 
    if ControlUnit.opCode == 0x03 or ControlUnit.funct == 0x09:
        RegFile.write(31, FD.output.PC4) 

    # Write to the Latch
    DE.input.RegDst    = ControlUnit.RegDst
    DE.input.Branch    = ControlUnit.Branch
    DE.input.MemRead   = ControlUnit.MemRead
    DE.input.MemtoReg  = ControlUnit.MemtoReg
    DE.input.ALUOp     = ControlUnit.ALUOp
    DE.input.MemWrite  = ControlUnit.MemWrite
    DE.input.RegWrite  = ControlUnit.RegWrite
    DE.input.PC4       = FD.output.PC4
    DE.input.RegRead1  = RegFile.read(InstParser.rs)
    DE.input.RegRead2  = RegFile.read(InstParser.rt)
    DE.input.ALUSrc    = ControlUnit.ALUSrc
    DE.input.ImmExt    = SignExtend.output
    DE.input.Jump      = ControlUnit.Jump
    DE.input.Addres    = InstParser.address
    DE.input.JumpReg   = ControlUnit.JumpReg
    DE.input.rs        = InstParser.rs
    DE.input.rt        = InstParser.rt
    DE.input.rd        = InstParser.rd
    DE.input.InstrName = ControlUnit.InstrName

    # Collect DEC stage data
    if DE.input.PC4 != 0 and ControlUnit.InstrName != "NOP":
        printer.collect_dec(
            pc=DE.input.PC4 - 4,
            instr_name=ControlUnit.InstrName,
            reg_read1=DE.input.RegRead1,
            reg_read2=DE.input.RegRead2,
            imm_ext=DE.input.ImmExt
        )
    else:
        printer.dec_stage = {}  # Stage not active


    # ---------------------------
    # Instruction Execution
    # ---------------------------
    # Check if we need to forward data from subsequent stages
    ForwardUnit.CreateSignals(DE.output.rs, DE.output.InstrName, DE.output.rt,
                              EM.output.rd, EM.output.RegWrite, EM.output.InstrName, EM.output.rt,
                              MW.output.rd, MW.output.RegWrite, MW.output.InstrName, MW.output.rt)
    
    # Check for lw-caused data hazard level 0
    if ForwardUnit.LWHazard0:
        print("LW Data hazard: Stall IF, ID and EX stages")
        DE.duplicate()
        FD.duplicate()
        PC -= 4  # Adjust PC to prevent fetching the next instruction

    # Check for lw-caused data hazard level 1
    if ForwardUnit.LWHazardA1 or ForwardUnit.LWHazardB1:
        print('LW Data Hazard: Forwarding from MEM stage to EX stage')

    # Bypass Level 0 MUX for ALU Operand A
    BypassL0A_MUX.input0 = DE.output.RegRead1
    BypassL0A_MUX.input1 = EM.output.ALUResult
    BypassL0A_MUX.select = ForwardUnit.BypassL0A
    BypassL0A_MUX.evaluate()

    # Bypass Level 1 MUX for ALU Operand A
    BypassL1A_MUX.input0 = BypassL0A_MUX.output
    BypassL1A_MUX.input1 = MW.output.ALUResult
    BypassL1A_MUX.select = ForwardUnit.BypassL1A
    BypassL1A_MUX.evaluate()

    # LW Bypass MUX for ALU Operand A
    LW_BypassA_MUX.input0 = BypassL1A_MUX.output
    LW_BypassA_MUX.input1 = MW.output.MemData
    LW_BypassA_MUX.select = ForwardUnit.LWHazardA1
    LW_BypassA_MUX.evaluate()

    ALU.A = LW_BypassA_MUX.output

    # Bypass MUX Level 0 for ALU Operand B
    BypassL0B_MUX.input0 = DE.output.RegRead2
    BypassL0B_MUX.input1 = EM.output.ALUResult
    BypassL0B_MUX.select = ForwardUnit.BypassLB0
    BypassL0B_MUX.evaluate()

    # Bypass MUX Level 1 for ALU Operand B
    BypassL1B_MUX.input0 = BypassL0B_MUX.output
    BypassL1B_MUX.input1 = MW.output.ALUResult
    BypassL1B_MUX.select = ForwardUnit.BypassLB1
    BypassL1B_MUX.evaluate()

    # ALU Operand B MUX
    ALUSrc_MUX.input0 = BypassL1B_MUX.output             
    ALUSrc_MUX.input1 = DE.output.ImmExt    
    ALUSrc_MUX.select = DE.output.ALUSrc
    ALUSrc_MUX.evaluate()

    # LW Bypass MUX for ALU Operand B
    LW_BypassB_MUX.input0 = ALUSrc_MUX.output
    LW_BypassB_MUX.input1 = MW.output.MemData
    LW_BypassB_MUX.select = ForwardUnit.LWHazardB1
    LW_BypassB_MUX.evaluate()

    ALU.B = LW_BypassB_MUX.output

    # ALU Operation
    ALU.ALUOp = DE.output.ALUOp  
    ALU.operate()    

    # JUMP CASE: disable previous stage Latch
    if DE.output.Jump:
        DE.EN = False     

    # Branch and Jump targets calculation
    branch_target = DE.output.PC4 + (DE.output.ImmExt << 2)  
    jump_target = ((DE.output.PC4) & 0xF0000000) | (DE.output.Addres << 2)

    # SW Bypass MUX level 0
    SW_Bypass0_MUX.input0 = DE.output.RegRead2
    SW_Bypass0_MUX.input1 = EM.output.ALUResult
    SW_Bypass0_MUX.select = ForwardUnit.SWHazard0
    SW_Bypass0_MUX.evaluate()

    # SW Bypass MUX level 1
    SW_Bypass1_MUX.input0 = SW_Bypass0_MUX.output
    SW_Bypass1_MUX.input1 = MW.output.ALUResult
    SW_Bypass1_MUX.select = ForwardUnit.SWHazard1
    SW_Bypass1_MUX.evaluate()

    # Write to the Latch
    EM.input.Jump         = DE.output.Jump
    EM.input.RegDst       = DE.output.RegDst
    EM.input.MemRead      = DE.output.MemRead
    EM.input.MemtoReg     = DE.output.MemtoReg
    EM.input.ALUResult    = ALU.result
    EM.input.MemWrite     = DE.output.MemWrite
    EM.input.RegWrite     = DE.output.RegWrite
    EM.input.BranchTaken  = DE.output.Branch and ALU.zero
    EM.input.RegRead1     = DE.output.RegRead1
    EM.input.RegRead2     = SW_Bypass1_MUX.output 
    EM.input.BranchTarget = branch_target
    EM.input.JumpTarget   = jump_target
    EM.input.JumpReg      = DE.output.JumpReg
    EM.input.rt           = DE.output.rt
    if DE.output.InstrName == 'addi': 
        EM.input.rd = DE.output.rt 
    else: 
        EM.input.rd = DE.output.rd
    EM.input.PC4          = DE.output.PC4
    EM.input.InstrName    = DE.output.InstrName

    # Collect EXE stage data
    if DE.output.PC4 != 0 and DE.output.InstrName != "NOP":
        printer.collect_exe(
            pc=DE.output.PC4 - 4,
            instr_name=DE.output.InstrName,
            alu_operation=ALU.operation,
            branch_target=branch_target,
            jump_target=jump_target
        )
    else:
        printer.exe_stage = {}  # Stage not active

    
    # ---------------------------
    # Memory access
    # ---------------------------
    # Memory Write
    DataMemory.write_word(EM.output.ALUResult, EM.output.RegRead2, EM.output.MemWrite)

    # Write to the Latch 
    MW.input.RegRead2  = EM.output.RegRead2
    MW.input.MemData   = DataMemory.read_word(EM.output.ALUResult, EM.output.MemRead)
    MW.input.MemtoReg  = EM.output.MemtoReg
    MW.input.ALUResult = EM.output.ALUResult
    MW.input.RegDst    = EM.output.RegDst
    MW.input.RegWrite  = EM.output.RegWrite
    MW.input.rt        = EM.output.rt
    MW.input.rd        = EM.output.rd
    MW.input.PC4       = EM.output.PC4
    MW.input.InstrName = EM.output.InstrName

    # Collect MEM stage data
    if EM.output.PC4 != 0 and EM.output.InstrName != "NOP":
        mem_data = MW.input.MemData if EM.output.MemRead else None
        written_data = EM.output.RegRead2 if EM.output.MemWrite else None
        printer.collect_mem(
            pc=EM.output.PC4 - 4,
            instr_name=EM.output.InstrName,
            mem_write=EM.output.MemWrite,
            mem_read=EM.output.MemRead,
            mem_data=mem_data,
            written_data=written_data
        )
    else:
        printer.mem_stage = {}  # Stage not active

    # Print pipeline state in original order
    printer.print_all()

    # Latching data
    FD.transfer()           
    DE.transfer()           
    EM.transfer()           
    MW.transfer()
    num_cycles += 1


    # ---------------------------
    # Stats gaining
    # ---------------------------
    if EM.output.PC4 != 0 and EM.output.InstrName != "NOP":
        total_instructions += 1

        # Determining instruction type
        if EM.output.InstrName in ['add', 'sub', 'jr', 'jalr', 'or', 'and', 'slt', 'srl', 'sll']:
            num_rtype += 1
        elif EM.output.InstrName in ['addi', 'lw', 'sw', 'beq']:
            num_itype += 1
        elif EM.output.InstrName in ['j', 'jal']:
            num_jtype += 1

        # Counting memory access instructions
        if EM.output.InstrName in ['lw', 'sw']:
            num_mem_access += 1


    # ---------------------------
    # Print Architectural State
    # ---------------------------
    print("\nRegister file state:")
    for idx, val in enumerate(RegFile.regs):
        print(f"  R{idx:02d}: 0x{val:08X}", end="\t")
        if (idx + 1) % 4 == 0:
            print()
    print("\nMemory state (only non-zero cells):")
    for i, word in enumerate(DataMemory.memory):
        if word != 0:
            print(f"  Address: 0x{i*4:08X}  Value: 0x{word:08X}")
    print("----------------------------\n\n\n")

print(f"Number of cycles: {num_cycles}")
print(f"Execution time = num_cycles * CYCLE_DURATION = {num_cycles * CYCLE_DURATION}ns")
print(f"Total instructions executed: {total_instructions}")
print(f"Number of R-type instructions: {num_rtype}")
print(f"Number of I-type instructions: {num_itype}")
print(f"Number of J-type instructions: {num_jtype}")
print(f"Number of memory access instructions: {num_mem_access}")
print(f"Number of taken branches: {num_taken_branches}")
print(f"Final return value (R2): 0x{RegFile.read(2):08X}")