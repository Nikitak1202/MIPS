# -------------------------------------------------------------
# Forwarding / Hazard-detection unit
# -------------------------------------------------------------
# All comments are now in English.
class ForwardUnit:
    def __init__(self):
        # ALU-operand forwarding
        self.BypassL0A = self.BypassL1A = 0
        self.BypassLB0 = self.BypassLB1 = 0

        # Hazards caused by a preceding lw
        self.LWHazard0 = self.LWHazardA1 = self.LWHazardB1 = 0

        # Hazards for sw (rt – data to store, rs – base address)
        self.SWHazardRT0 = self.SWHazardRT1 = 0
        self.SWHazardRS0 = self.SWHazardRS1 = 0


    def CreateSignals(self,  DE_rs,              DE_InstrName, DE_rt,
                             EM_rd, EM_RegWrite, EM_InstrName, EM_rt,
                             MW_rd, MW_RegWrite, MW_InstrName, MW_rt):

        # ---------------------------------------------------------
        # 1. Determine the effective write-back register number
        #    (rt for  lw / addi, rd for every R-type instruction)
        # ---------------------------------------------------------
        EM_WB = EM_rt if EM_InstrName in ['lw', 'addi'] else EM_rd
        MW_WB = MW_rt if MW_InstrName in ['lw', 'addi'] else MW_rd

        # ---------------------------------------------------------
        # Level-0 hazard: lw in EX/MEM, current instr in ID/EX
        # ---------------------------------------------------------
        Rtype_Intersection0 = (
            EM_InstrName == 'lw' and
            DE_InstrName in ['add', 'sub', 'jr', 'jalr',
                             'or',  'and', 'slt', 'srl', 'sll'] and
            (EM_rt == DE_rs or EM_rt == DE_rt)
        )
        ItypeIntersection0  = (
           (EM_InstrName == 'lw' and
            DE_InstrName in ['addi', 'beq'] and
            EM_rt == DE_rs)
            or 
           (EM_InstrName == 'lw' and DE_InstrName == 'lw')
        )
        SW_LW_Intersection0 = (
            EM_InstrName == 'lw' and DE_InstrName == 'sw' and
            (EM_rt == DE_rs or EM_rt == DE_rt)
        )
        self.LWHazard0 = int(
            Rtype_Intersection0 or ItypeIntersection0 or SW_LW_Intersection0
        )

        # ---------------------------------------------------------
        # Level-1 hazard for operand A (rs)
        # ---------------------------------------------------------
        Rtype_A1 = (
            MW_InstrName == 'lw' and
            DE_InstrName in ['add', 'sub', 'jr', 'jalr',
                             'or',  'and', 'slt', 'srl', 'sll'] and
            MW_rt == DE_rs
        )
        Itype_A1 = (
            MW_InstrName == 'lw' and
            DE_InstrName in ['addi', 'lw', 'beq'] and
            MW_rt == DE_rs
        )
        SW_LW_A1 = (
            MW_InstrName == 'lw' and DE_InstrName == 'sw' and
            (MW_rt == DE_rs or MW_rt == DE_rt)
        )
        self.LWHazardA1 = int(Rtype_A1 or Itype_A1 or SW_LW_A1)

        # ---------------------------------------------------------
        # Level-1 hazard for operand B (rt)
        # (beq was already present)
        # ---------------------------------------------------------
        self.LWHazardB1 = int(
            MW_InstrName == 'lw' and
            DE_InstrName in ['add', 'sub', 'jr', 'jalr',
                             'or',  'and', 'slt', 'srl', 'sll', 'beq'] and
            MW_rt == DE_rt
        )

        # ---------------------------------------------------------
        # Forwarding logic for ALU operand A (rs)
        # ---------------------------------------------------------
        self.BypassL0A = int(EM_RegWrite and EM_WB == DE_rs)
        self.BypassL1A = int(
            MW_RegWrite and MW_WB == DE_rs and not self.BypassL0A
        )

        # ---------------------------------------------------------
        # Forwarding logic for ALU operand B (rt)
        # ---------------------------------------------------------
        self.BypassLB0 = int(EM_RegWrite and EM_WB == DE_rt)
        self.BypassLB1 = int(
            MW_RegWrite and MW_WB == DE_rt and not self.BypassLB0
        )

        # ---------------------------------------------------------
        # sw-related hazards
        #   rt – data word to store
        #   rs – base address
        # ---------------------------------------------------------
        # Data (rt) – level 0
        self.SWHazardRT0 = int(
            DE_InstrName == 'sw' and EM_RegWrite and DE_rt == EM_WB
        )
        # Data (rt) – level 1
        self.SWHazardRT1 = int(
            DE_InstrName == 'sw' and MW_RegWrite and DE_rt == MW_WB
            and not self.SWHazardRT0
        )
        # Address base (rs) – level 0
        self.SWHazardRS0 = int(
            DE_InstrName == 'sw' and EM_RegWrite and DE_rs == EM_WB
        )
        # Address base (rs) – level 1
        self.SWHazardRS1 = int(
            DE_InstrName == 'sw' and MW_RegWrite and DE_rs == MW_WB
            and not self.SWHazardRS0
        )
