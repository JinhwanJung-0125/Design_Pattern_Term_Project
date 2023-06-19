from Modules.Memory_Register import MemoryRegister

#InstructionRegister

class InstructionRegister:              #명령어 포멧 Data Structure
    def __init__(self, num):
        self.I = num  #32-bits 숫자
        self.RI = self.RFormat(num)    #32-bits R format형식 명령어
        self.II = self.IFormat(num)    #32-bits I format형식 명령어
        self.JI = self.JFormat(num)    #32-bits J format형식 명령어

    class RFormat:
        def __init__(self, I):
            self.funct = I & 0x2f  #6bit
            self.shamt = (I >> 6) & 0x1f  #5bit
            self.rd = (I >> 11) & 0x1f #5bit
            self.rt = (I >> 16) & 0x1f #5bit
            self.rs = (I >> 21) & 0x1f #5bit
            self.opcode = I >> 26 #6bit

    class IFormat:
        def __init__(self, I):
            self.immediate = I & 0xffff  #16bit
            self.rt = (I >> 16) & 0x1f #5bit
            self.rs = (I >> 21) & 0x1f #5bit
            self.opcode = I >> 26 #6bit

    class JFormat:
        def __init__(self, I):
            self.address = I & 0x3ffffff    #26bit
            self.opcode = I >> 26 #6bit

#ALU class

class ALU:
    @staticmethod
    def invert_endian(inVal):   #Endian 변환 함수
        inVal = ((inVal >> 24) & 0xff) | ((inVal << 8) & 0xff0000) | ((inVal >> 8) & 0xff00) | ((inVal << 24) & 0xff000000)
        return inVal

    @staticmethod
    def ALU(inst, PC, MEM: MemoryRegister, Reg: MemoryRegister):
        IR = InstructionRegister(inst)
        print("IR ", bin(IR.I))
        PC = Reg.useToAccess(32, 0, 0)

        if IR.RI.opcode == 0:       # sll rd rt shamt
            if IR.RI.funct == 0:
                print("sll $" + str(IR.RI.rd) + " $" + str(IR.RI.rt) + " " + str(IR.RI.shamt))
                Reg.useToAccess(IR.RI.rd, Reg.useToAccess(IR.RI.rt, 0, 0) << IR.RI.shamt, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.funct == 2:  # srl rd rt shamt
                print("srl $" + str(IR.RI.rd) + " $" + str(IR.RI.rt) + " " + str(IR.RI.shamt))
                Reg.useToAccess(IR.RI.rd, Reg.useToAccess(IR.RI.rt, 0, 0) >> IR.RI.shamt, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.funct == 3:  # sra rd rt shamt
                print("sra $" + str(IR.RI.rd) + " $" + str(IR.RI.rt) + " " + str(IR.RI.shamt))
                MSB = Reg.useToAccess(IR.RI.rt, 0, 0) & 0x80000000
                temp = Reg.useToAccess(IR.RI.rt, 0, 0)

                for _ in range(IR.RI.shamt):
                    temp = (temp >> 1) + MSB

                Reg.useToAccess(IR.RI.rt, temp, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.funct == 8:  # jr rs
                print("jr $" + str(IR.RI.rs))
                PC = Reg.useToAccess(IR.RI.rs, 0, 0)
                Reg.useToAccess(32, PC, 1)

            elif IR.RI.funct == 12:  # syscall
                print("Inst: syscall")
                Reg.useToAccess(32, PC + 4, 1)
                return 0

            elif IR.RI.funct == 16:  # mfhi rd
                print("mfhi $" + str(IR.RI.rd))
                Reg.useToAccess(IR.RI.rd, (Reg.useToAccess(33, 0, 0)), 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.funct == 18:  # mflo rd
                print("mflo $" + str(IR.RI.rd))
                Reg.useToAccess(IR.RI.rd, (Reg.useToAccess(34, 0, 0)), 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.funct == 24:  # MULT: multiply rs, rt
                print("mul $" + str(IR.RI.rs) + " $" + str(IR.RI.rt))
                multiResult = Reg.useToAccess(IR.RI.rs, 0, 0) * Reg.useToAccess(IR.RI.rt, 0, 0)
                hi = multiResult >> 32  # 상위 32비트
                lo = multiResult & 0xffffffff  # 하위 32비트
                Reg.useToAccess(33, hi, 1)
                Reg.useToAccess(34, lo, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.funct == 32:  # add rd rs rt
                print("add $" + str(IR.RI.rd) + " $" + str(IR.RI.rs) + " $" + str(IR.RI.rt))
                result = Reg.useToAccess(IR.RI.rs, 0, 0) + Reg.useToAccess(IR.RI.rt, 0, 0)
                Reg.useToAccess(IR.RI.rd, result, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.funct == 34:  # sub rd rs rt
                print("sub $" + str(IR.RI.rd) + " $" + str(IR.RI.rs) + " $" + str(IR.RI.rt))
                result = Reg.useToAccess(IR.RI.rs, 0, 0) - Reg.useToAccess(IR.RI.rt, 0, 0)
                Reg.useToAccess(IR.RI.rd, result, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.funct == 36:  # and rd rs rt
                print("and $" + str(IR.RI.rd) + " $" + str(IR.RI.rs) + " $" + str(IR.RI.rt))
                result = Reg.useToAccess(IR.RI.rs, 0, 0) & Reg.useToAccess(IR.RI.rt, 0, 0)
                Reg.useToAccess(IR.RI.rd, result, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.funct == 37:  # or rd rs rt
                print("or $" + str(IR.RI.rd) + " $" + str(IR.RI.rs) + " $" + str(IR.RI.rt))
                result = Reg.useToAccess(IR.RI.rs, 0, 0) | Reg.useToAccess(IR.RI.rt, 0, 0)
                Reg.useToAccess(IR.RI.rd, result, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.funct == 38:  # xor rd rs rt 
                print("xor $" + str(IR.RI.rd) + " $" + str(IR.RI.rs) + " $" + str(IR.RI.rt))
                result = Reg.useToAccess(IR.RI.rs, 0, 0) ^ Reg.useToAccess(IR.RI.rt, 0, 0)
                Reg.useToAccess(IR.RI.rd, result, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.funct == 39:  # nor rd rs rt
                print("nor $" + str(IR.RI.rd) + " $" + str(IR.RI.rs) + " $" + str(IR.RI.rt))
                result = Reg.useToAccess(IR.RI.rs, 0, 0) | Reg.useToAccess(IR.RI.rt, 0, 0)
                Reg.useToAccess(IR.RI.rd, ~result, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.funct == 42:  # slt: set less than: if(rs < rt) rd = 1; else rd = 0; slt rd rs rt
                print("slt $" + str(IR.RI.rd) + " $" + str(IR.RI.rs) + " $" + str(IR.RI.rt))
                if Reg.useToAccess(IR.RI.rs, 0, 0) < Reg.useToAccess(IR.RI.rt, 0, 0):
                    Reg.useToAccess(IR.RI.rd, 1, 1)

                else:
                    Reg.useToAccess(IR.RI.rd, 0, 1)

                Reg.useToAccess(32, PC + 4, 1)

            else:                    # default
                print("default")
                Reg.useToAccess(32, PC + 4, 1)
        else:
            if IR.RI.opcode == 1:   #bltz rs, L : branch less then 0
                print("bltz $" + str(IR.RI.rs) + " 0x%x" %((IR.I & 0x0000ffff) << 2))
                L = PC + ((IR.I & 0x0000ffff) << 2)

                if Reg.useToAccess(IR.RI.rs, 0, 0) < 0:
                    Reg.useToAccess(32, L, 1)

                else:
                    Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.opcode == 2: #j L : jump -> address00 + 4 : Program Counter
                print("j 0x%x" %(IR.I & 0x03ffffff))
                L = (PC >> 28) | ((IR.I & 0x03ffffff) << 2)
                Reg.useToAccess(32, L , 1)

            elif IR.RI.opcode == 3: #jal L : jump and link
                print("jal 0x%x" %(IR.I & 0x03ffffff))
                L = (PC >> 28) | ((IR.I & 0x03ffffff) << 2)
                Reg.useToAccess(31, PC+4, 1)
                Reg.useToAccess(32, L, 1) #다음 주소값 명령어를 레지스터에 저장

            elif IR.RI.opcode == 4: #beq rs, rt, L : branch equal
                print("beq $" + str(IR.RI.rs) + " $" + str(IR.RI.rt) + " 0x%x" %(IR.I & 0x0000ffff))
                L = PC + ((IR.I & 0x0000ffff) << 2)
                if Reg.useToAccess(IR.RI.rs, 0, 0) == Reg.useToAccess(IR.RI.rt, 0, 0):
                    Reg.useToAccess(32, L, 1)
                else:
                    Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.opcode == 5: #bne rs, rt, L: Branch not equal
                print("bne $" + str(IR.RI.rs) + " $" + str(IR.RI.rt) + " 0x%x" %(IR.I & 0x0000ffff))
                L = PC + ((IR.I & 0x0000ffff) << 2)
                if Reg.useToAccess(IR.RI.rs, 0, 0) != Reg.useToAccess(IR.RI.rt, 0, 0):
                    Reg.useToAccess(32, L, 1)
                else:
                    Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.opcode == 8: #addi rt,rs, imm: ADD immediate
                print("addi $" + str(IR.RI.rt) + " $" + str(IR.RI.rs) + " " + str(IR.I & 0x0000ffff))
                result = Reg.useToAccess(IR.RI.rs, 0, 0) + (IR.I & 0x0000ffff)
                Reg.useToAccess(IR.RI.rt, result, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.opcode == 10:    #slti rt,rs, imm: set less than immediate
                print("slti $" + str(IR.RI.rt) + " $" + str(IR.RI.rs) + " " + str(IR.I & 0x0000ffff))
                if(Reg.useToAccess(IR.RI.rs,0,0) < (IR.I & 0x0000ffff)):
                    Reg.useToAccess(IR.RI.rt, 1, 1);#$s1=1
                else:
                    Reg.useToAccess(IR.RI.rt, 0, 1);#$s1=0
                Reg.useToAccess(32, PC+4, 1);

            elif IR.RI.opcode == 12:    #andi rt, rs, imm: AND immediate
                print("andi $" + str(IR.RI.rt) + " $" + str(IR.RI.rs) + " " + str(IR.I & 0x0000ffff))
                result = Reg.useToAccess(IR.RI.rs, 0, 0) & (IR.I & 0x0000ffff)
                Reg.useToAccess(IR.RI.rt, result, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.opcode == 13:    #ori rt, rs, imm: OR immediate
                print("ori $" + str(IR.RI.rt) + " $" + str(IR.RI.rs) + " " + str(IR.I & 0x0000ffff))
                result = Reg.useToAccess(IR.RI.rs, 0, 0) | (IR.I & 0x0000ffff)
                Reg.useToAccess(IR.RI.rt, result, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.opcode == 14:    #xor rt, rs, imm: XOR immediate
                print("xor $" + str(IR.RI.rt) + " $" + str(IR.RI.rs) + " " + str(IR.I & 0x0000ffff))
                result = Reg.useToAccess(IR.RI.rs, 0, 0) ^ (IR.I & 0x0000ffff)
                Reg.useToAccess(IR.RI.rt, result, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.opcode == 15:    #lui rt, imm: load upper immediate// 상위 16bit에 imm값 넣고 뒤 16bit는 0으로 둔다.
                print("lui $" + str(IR.RI.rt) + " 0x%x" %(IR.I & 0x0000ffff))
                immUp = (IR.I & 0x0000ffff) << 16
                Reg.useToAccess(IR.RI.rt, immUp, 1)
                Reg.useToAccess(32, PC + 4, 1)

            elif IR.RI.opcode == 32:    #lb rt, imm(rs): load byte
                print("lb $" + str(IR.RI.rt) + " imm(" + str(IR.RI.rs) + ")")
                MEMout = MEM.useToAccess(Reg.useToAccess(IR.RI.rs,0,0) + (IR.I & 0x0000ffff), 0, 0, 0)
                if(((MEMout & 0xa0) >> 7) == 1): MEMout = MEMout | 0xffffff00
                Reg.useToAccess(IR.RI.rt, MEMout, 1)
                Reg.useToAccess(32, PC+4, 1)

            elif IR.RI.opcode == 35:    #lw rt, imm(rs): load word
                print("lw $" + str(IR.RI.rt) + " imm(" + str(IR.RI.rs) + ")")
                Reg.useToAccess(IR.RI.rt, MEM.useToAccess(Reg.useToAccess(IR.RI.rs,0,0) + (IR.I & 0x0000ffff), 0, 0, 2), 1)
                Reg.useToAccess(32, PC+4, 1)

            elif IR.RI.opcode == 36:    #lbu rt, imm(rs): load byte unsigned
                print("lbu $" + str(IR.RI.rt) + " imm(" + str(IR.RI.rs) + ")")
                Reg.useToAccess(IR.RI.rt, MEM.useToAccess(Reg.useToAccess(IR.RI.rs,0,0) + (IR.I & 0x0000ffff), 0, 0, 0), 1)
                Reg.useToAccess(32, PC+4, 1)

            elif IR.RI.opcode == 40:    #sb rt, imm(rs): store byte / reg->mem
                print("sb $" + str(IR.RI.rt) + " imm(" + str(IR.RI.rs) + ")")
                MEM.useToAccess(Reg.useToAccess(IR.RI.rs,0,0) + (IR.I & 0x0000ffff), Reg.useToAccess(IR.RI.rt, 0, 0), 1, 0)
                Reg.useToAccess(32, PC+4, 1)

            elif IR.RI.opcode == 43:    #sw rt, imm(rs): store word
                print("sw $" + str(IR.RI.rt) + " imm(" + str(IR.RI.rs) + ")")
                MEM.useToAccess(Reg.useToAccess(IR.RI.rs,0,0) + (IR.I & 0x0000ffff), Reg.useToAccess(IR.RI.rt, 0, 0), 1, 2)
                Reg.useToAccess(32, PC+4, 1)

            else:                       # default
                print("default")
                Reg.useToAccess(32, PC+4, 1)

        return 1