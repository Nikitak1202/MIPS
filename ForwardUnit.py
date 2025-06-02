class ForwardUnit:
    def __init__(self):
        self.BypassL0A  = 0
        self.BypassL1A  = 0
        self.BypassLB0  = 0
        self.BypassLB1  = 0

        self.LWHazard0  = 0
        self.LWHazardA1 = 0
        self.LWHazardB1 = 0

        self.SWHazard0  = 0
        self.SWHazard1 = 0  


    def CreateSignals(self,  DE_rs,              DE_InstrName, DE_rt, 
                             EM_rd, EM_RegWrite, EM_InstrName, EM_rt,
                             MW_rd, MW_RegWrite, MW_InstrName, MW_rt):
        
        # Bypass Detection for lw-caused data hazard level 0
        Rtype_Intersection0 = EM_InstrName == 'lw'and (DE_InstrName in ['add', 'sub', 'jr', 'jalr', 'or', 'and', 'slt', 'srl', 'sll']) and (EM_rt == DE_rs or EM_rt == DE_rt)
        ItypeIntersection0 = EM_InstrName == 'lw'and (DE_InstrName in ['addi', 'lw', 'sw', 'beq']) and EM_rt == DE_rs
        if Rtype_Intersection0 or ItypeIntersection0:
            self.LWHazard0 = 1
        else:
            self.LWHazard0 = 0

        # Bypass Detection for lw-caused data hazard level 1 ALU operand A
        Rtype_IntersectionA1 = MW_InstrName == 'lw' and (DE_InstrName in ['add', 'sub', 'jr', 'jalr', 'or', 'and', 'slt', 'srl', 'sll']) and MW_rt == DE_rs # MW_rt == DE_rt
        ItypeIntersectionA1 = MW_InstrName == 'lw' and (DE_InstrName in ['addi', 'lw', 'sw', 'beq']) and MW_rt == DE_rs
        if Rtype_IntersectionA1 or ItypeIntersectionA1:
            self.LWHazardA1 = 1  
        else:
            self.LWHazardA1 = 0

        # Bypass Detection for lw-caused data hazard level 1 ALU operand B
        if MW_InstrName == 'lw' and (DE_InstrName in ['add', 'sub', 'jr', 'jalr', 'or', 'and', 'slt', 'srl', 'sll']) and MW_rt == DE_rt:
            self.LWHazardB1 = 1  
        else:
            self.LWHazardB1 = 0

        # Bypass Logic for ALU Operand A
        if EM_RegWrite and (EM_rd == DE_rs):
            self.BypassL0A = 1
        else:
            self.BypassL0A = 0

        if MW_RegWrite and (MW_rd == DE_rs) and self.BypassL0A == 0:
            self.BypassL1A = 1
        else:
            self.BypassL1A = 0

        # Bypass Logic for ALU Operand B
        if EM_RegWrite and (EM_rd == DE_rt):
            self.BypassLB0 = 1
        else:
            self.BypassLB0 = 0
        
        if MW_RegWrite and (MW_rd == DE_rt) and self.BypassLB0 == 0:
            self.BypassLB1 = 1
        else:
            self.BypassLB1 = 0

        # Store Word Hazard Detection level 0
        if DE_InstrName == 'sw' and EM_RegWrite and (DE_rt == EM_rd):
            self.SWHazard0 = 1
        else:
            self.SWHazard0 = 0

        # Store Word Hazard Detection level 1
        if DE_InstrName == 'sw' and MW_RegWrite and (DE_rt == MW_rd) and self.SWHazard0 == 0:
            self.SWHazard1 = 1
        else:
            self.SWHazard1 = 0