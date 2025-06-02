class StatePrinter:
    def __init__(self):
        self.if_stage = {}
        self.dec_stage = {}
        self.exe_stage = {}
        self.mem_stage = {}
        self.wb_stage = {}
    
    def collect_if(self, pc, instr_str, instr_bin):
        self.if_stage = {
            'pc': pc,
            'instr_str': instr_str,
            'instr_bin': instr_bin
        }
    
    def collect_dec(self, pc, instr_name, reg_read1, reg_read2, imm_ext):
        self.dec_stage = {
            'pc': pc,
            'instr_name': instr_name,
            'reg_read1': reg_read1,
            'reg_read2': reg_read2,
            'imm_ext': imm_ext
        }
    
    def collect_exe(self, pc, instr_name, alu_operation, branch_target, jump_target):
        self.exe_stage = {
            'pc': pc,
            'instr_name': instr_name,
            'alu_operation': alu_operation,
            'branch_target': branch_target,
            'jump_target': jump_target
        }
    
    def collect_mem(self, pc, instr_name, mem_write, mem_read, mem_data, written_data):
        self.mem_stage = {
            'pc': pc,
            'instr_name': instr_name,
            'mem_write': mem_write,
            'mem_read': mem_read,
            'mem_data': mem_data,
            'written_data': written_data
        }
    
    def collect_wb(self, pc, instr_name, memto_reg, result, target_reg):
        self.wb_stage = {
            'pc': pc,
            'instr_name': instr_name,
            'memto_reg': memto_reg,
            'result': result,
            'target_reg': target_reg
        }
    
    def print_all(self):
        # Print in original order: IF, DEC, EXE, MEM, WB
        print("\n----- FETCH STAGE -----")
        if self.if_stage:
            print(f"PC = {self.if_stage['pc']}")
            if self.if_stage['instr_str']:
                print(f"Instruction: {self.if_stage['instr_str']} (binary: {self.if_stage['instr_bin']:032b})")
            else:
                print("Instruction: NOP")
        
        print("\n----- DECODE STAGE -----")
        if self.dec_stage:
            print(f"PC               = {self.dec_stage['pc']}")
            print(f"Instruction Name = {self.dec_stage['instr_name']}")
            print(f"Read data 1      = {self.dec_stage['reg_read1']}")
            print(f"Read data 2      = {self.dec_stage['reg_read2']}")
            print(f"Sign extended    = {self.dec_stage['imm_ext']}")
        else:
            print("Stage not active")
        
        print("\n----- EXECUTE STAGE -----")
        if self.exe_stage:
            print(f"PC               = {self.exe_stage['pc']}")
            print(f"Instruction Name = {self.exe_stage['instr_name']}")
            print(f"ALU {self.exe_stage['alu_operation']}")
            print(f"Branch Target    = {self.exe_stage['branch_target']}")
            print(f"Jump Target      = {self.exe_stage['jump_target']}")
        else:
            print("Stage not active")
        
        print("\n----- MEMORY ACCESS STAGE -----")
        if self.mem_stage:
            print(f"PC               = {self.mem_stage['pc']}")
            print(f"Instruction Name = {self.mem_stage['instr_name']}")
            print(f'MemWrite         = {self.mem_stage["mem_write"]}')
            print(f'MemRead          = {self.mem_stage["mem_read"]}')
            if self.mem_stage["mem_read"]:
                print(f'Read Data        = {self.mem_stage["mem_data"]}')
            elif self.mem_stage["mem_write"]: 
                print(f'Written Data     = {self.mem_stage["written_data"]}')
        else:
            print("Stage not active")
        
        print("\n----- WRITE BACK STAGE -----")
        if self.wb_stage:
            print(f"PC               = {self.wb_stage['pc']}")
            print(f"Instruction Name = {self.wb_stage['instr_name']}")
            if self.wb_stage['memto_reg']:
                print(f'Writting {self.wb_stage["result"]} to RegFile from Memory at address {self.wb_stage["target_reg"]}')
            else:
                print(f'Writting {self.wb_stage["result"]} to RegFile from ALU at address {self.wb_stage["target_reg"]}')
        else:
            print("Stage not active")