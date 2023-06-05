#Memory와 Register 접근 구현에 Bridge Pattern을 적용

from asyncio.windows_events import NULL
from io import BufferedReader


class Access:   #Implementor(API)
    def access(self):
        pass

    def printing(self):
        pass

class RegisterAccess(Access):   #Concrete Implementor
    def __init__(self):
        self.reg = [0] * 35

    def access(self, addr, value, readOrWrite):
        if readOrWrite == 0:
            return self.reg[addr]

        elif readOrWrite == 1:
            self.reg[addr] = value
            return value

        else:
            print("readOrWrite must be 0 or 1!")
            exit(1)

    def printing(self):
        r = ["r0", "at", "v0", "v1", "a0", "a1", "a2", "a3", "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "t8", "t9", "k0", "k1", "gp", "sp", "fp", "ra", "PC", "HI", "LO"]
        # 0 : Zero / 1 : Assembler Temporary / 2 ~ 3 : Output Argument / 4 ~ 7 : Input Argument / 8 ~ 27 : General Register / 28 : Global Pointer / 29 : Stack Pointer / 30 : Frame Pointer / 31 : Return Address / 32 : Program Counter / 33 : High Register / 34 : Low Register

        print("---- REGISTER ----")

        for i in range(32):
            print("R%02d [%s] = 0x%0.8X" % (i, r[i], self.reg[i]))

        for i in range(32, 35):
            print("%s = 0x%0.8X" % (r[i], self.reg[i]))

        print()

    def initReg(self):
        for i in range(35):
            self.reg[i] = 0


class MemoryAccess(Access): #Concrete Implementor
    def __init__(self):
        self.progMEM = bytearray(0x100000)
        self.dataMEM = bytearray(0x100000)
        self.stackMEM = bytearray(0x100000)

    def access(self, addr, value, readOrWrite, size):
        selectMEM = addr >> 20
        offset = addr & 0xfffff

        if selectMEM == 0x004:      #Text 영역 Memory
            pM = self.progMEM

        elif selectMEM == 0x100:    #Data 영역 Memory
            pM = self.dataMEM

        elif selectMEM == 0x7ff:    #Stack 영역 Memory
            pM = self.stackMEM

        else:
            print("Wrong Memory Access!")
            exit(1)

        if size == 0:   #1byte
            if readOrWrite == 0:    #read
                value = pM[offset]
                return value

            elif readOrWrite == 1:  #write
                pM[offset] = value & 0xff
                return value

        elif size == 1: #half word
            if readOrWrite == 0:    #read
                value = (pM[offset]) | (pM[offset + 1] << 8)
                return value

            elif readOrWrite == 1:  #write
                pM[offset] = value & 0x00ff
                pM[offset + 1] = (value & 0xff00) >> 8
                return value

        elif size == 2: #word
            if readOrWrite == 0:    #read
                value = pM[offset] | (pM[offset + 1] << 8) | (pM[offset + 2] << 16) | (pM[offset + 3] << 24)
                return value

            elif readOrWrite == 1:  #write
                pM[offset] = value & 0x000000ff
                pM[offset + 1] = (value & 0x0000ff00) >> 8
                pM[offset + 2] = (value & 0x00ff0000) >> 16
                pM[offset + 3] = (value & 0xff000000) >> 24
                return value
        else:
            print("Wrong Memory Access Size!")
            exit(1)

    def printing(self, start, end):
        front = start >> 20  # 앞 12비트
        offset = start & 0xFFFFF
        e_offset = end & 0xFFFFF

        if front == 0x004:
            pM = self.progMEM
            print("Program Memory space")

        elif front == 0x100:
            print("Data Memory space")
            pM = self.dataMEM

        elif front == 0x7FF:
            print("Stack Memory space")
            pM = self.stackMEM

        else:
            print("No Such Memory")
            return 1

        for i in range(offset, e_offset + 1):
            if (i % 4) == 0 or i == offset:
                print("\n[0x%X] " % ((front << 20) + i), end="")

            print("0x%02x" % pM[i], end="")

        print()

class MemoryRegister: #Abstraction
    def __init__(self, access:Access):
        self.access = access

    def useToAccess(self):
        pass

    def useToPrint(self):
        pass

class Register(MemoryRegister): #Concrete Abstraction   (Register)
    def useToAccess(self, addr, value, readOrWrite):                #addr = Register 번호 / value = Register에 쓰고자 하는 값 / readOrWrite = 0: Register 읽기 , 1: Register 쓰기 
        return self.access.access(addr, value, readOrWrite)

    def useToPrint(self):
        self.access.printing()

    def initReg(self):
        self.access.initReg()

class Memory(MemoryRegister):   #Concrete Abstraction   (Memory)
    def useToAccess(self, addr, value, readOrWrite, size):          #addr = Memory 주소 / value = Memory에 쓰고자 하는 값 / readOrWrite = 0: Memory 읽기 , 1: Memory 쓰기 / size = Memory에 한번에 Access할 크기 0: 1byte , 1: half word , 2: word
        return self.access.access(addr, value, readOrWrite, size)

    def useToPrint(self, start, end):       #start: Memory Print 시작 지점 / end: Memory Print 끝 지점
        self.access.printing(start, end)





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
                print("jal 0x%x" %(IR.I & 0x0000ffff))
                L=(PC>>28)|((IR.I & 0x0000ffff) <<2)
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





isEnd = False
isExecutable = False

#interface는 Command Pattern을 적용

class Command:  #Command(API)
    def execute(self):
        pass

class interface:    #Invoker
    def __init__(self):
        self.command = NULL

    def addCommand(self, command: Command):
        self.command = command

    def runCommand(self):
        self.command.execute()



class setPC(Command):           #Program Counter 세팅
    def __init__(self, addr, Reg: MemoryRegister):
        self.PC = 32
        self.addr = addr
        self.Reg = Reg

    def execute(self):
        self.Reg.useToAccess(self.PC, self.addr, 1)

class setSP(Command):           #Stack Pointer 세팅
    def __init__(self, addr, Reg: MemoryRegister):
        self.addr = addr
        self.Reg = Reg

    def execute(self):
        self.Reg.useToAccess(29, self.addr, 1)

class loadProgram(Command):     #프로그램 로드
    def __init__(self, MEM: MemoryRegister, Reg: MemoryRegister, fileReader: BufferedReader):
        self.MEM = MEM
        self.Reg = Reg
        self.fileReader = fileReader

    def execute(self):
        global isEnd, isExecutable

        instNum, dataNum = 0, 0
        buff = 0

        self.Reg.initReg()
        self.Reg.useToAccess(32, 0x400000, 1)
        self.Reg.useToAccess(29, 0x7ff00000, 1)
        isEnd = False

        buff = self.fileReader.read(4)

        if buff == 0:
            print("File read error!")
            isExecutable = False
            return 1
        
        instNum = int.from_bytes(buff, byteorder = 'big')

        buff = self.fileReader.read(4)

        if buff == 0:
            print("File read error!")
            isExecutable = False
            return 1    

        dataNum = int.from_bytes(buff, byteorder = 'big')

        for i in range(instNum):
            buff = int.from_bytes(self.fileReader.read(4), byteorder = "big")

            self.MEM.useToAccess(0x400000 + (i * 4), buff, 1, 2)

        for i in range(dataNum):
            buff = int.from_bytes(self.fileReader.read(4), byteorder = "big")

            self.MEM.useToAccess(0x10000000 + (i * 4), buff, 1 ,2)

        isExecutable = True
        print("Program load success\n")

class jumpProgram(Command):     #특정 위치로 Jump
    def __init__(self, startPosition, Reg: MemoryRegister):
        self.Reg = Reg
        self.startPosition = startPosition

    def execute(self):
        if startPosition % 4 != 0:
            startPosition = startPosition & 0xfffffffc

        if (startPosition >> 20) == 4:
            self.Reg.useToAccess(32, self.startPosition, 1)
            print("PC is set at 0x%x\n" % self.Reg.useToAccess(32, 0, 0))
        else:
            print("Error: Wrong Access!\n")

class goProgram(Command):   #프로그램 전체 실행
    def __init__(self, command: Command):
        self.step = command

    def execute(self):
        global isEnd, isExecutable

        while not isEnd:
            self.step.execute()

        print("-----Program End-----\n\n")

class step(Command):        #프로그램 단계별 실행
    def __init__(self, MEM: MemoryRegister, Reg: MemoryRegister):
        self.Reg = Reg
        self.MEM = MEM

    def execute(self):
        global isEnd, isExecutable
        PC = self.Reg.useToAccess(32, 0, 0)
        inst = self.MEM.useToAccess(PC, 0, 0, 2)

        if ALU.ALU(inst, PC, self.MEM, self.Reg) == 0:
            isEnd = True
            isExecutable = False
        else:   isEnd = False

        self.Reg.useToPrint()

class setRegister(Command): #특정 Register 값 세팅
    def __init__(self, regNum, value, Reg: MemoryRegister):
        self.regNum = regNum
        self.value = value
        self.Reg = Reg

    def execute(self):
        self.Reg.useToAccess(self.regNum, self.value, 1)
        print("%d %d" % (self.regNum, self.value))

class setMemory(Command):   #특정 Memory위치의 값 세팅
    def __init__(self, location, value, MEM: MemoryRegister):
        self.location = location
        self.value = value
        self.MEM = MEM

    def execute(self):
        self.MEM.useToAccess(self.location, self.value, 1, 2)
        print("%0.8x %d" % (self.location, self.value))



#종합적으로 Facade Pattern을 적용한다.

class Facade:
    def __init__(self):
        self.MEM = Memory(MemoryAccess())
        self.Reg = Register(RegisterAccess())
        self.interface = interface()

    def run(self):
        global isEnd, isExecutable

        print("-----Simulator Start-----\n")
        print("Supported Command: l/j/g/s/m/r/x/sr/sm\n")

        while(True):
            print("Enter Command: ")
            command = input().split()

            if command[0] == 'l':                               # l XXX.bin => load XXX.bin
                if len(command) != 2:
                    print("Error: Wrong command format!\n")

                else:
                    try:
                        openedFile = open(command[1], 'rb')
                        self.interface.addCommand(loadProgram(self.MEM, self.Reg, openedFile))
                        self.interface.runCommand()
                    except FileNotFoundError as e:
                        print(e)

            elif command[0] == "j" and isExecutable == True:    # j 0xXXXXXX => jump to 0xXXXXXX
                if len(command) != 2:
                    print("Error: Wrong command format!\n")

                else:
                    self.interface.addCommand(jumpProgram(int(command[1], 16), self.Reg))
                    self.interface.runCommand()

            elif command[0] == "g" and isExecutable == True:    # g => go program
                self.interface.addCommand(goProgram(step(self.MEM, self.Reg)))
                self.interface.runCommand()

            elif command[0] == 's' and isExecutable == True:    # s => step
                self.interface.addCommand(step(self.MEM, self.Reg))
                self.interface.runCommand()

            elif command[0] == "m" and isExecutable == True:    # m 0xXXXXXX 0xXXXXXX => print memory 0xXXXXXX to 0xXXXXXX
                if len(command) != 3:
                    print("Error: Wrong command format!\n")

                else:
                    self.MEM.useToPrint(int(command[1], 16), int(command[2], 16))

            elif command[0] == "r" and isExecutable == True:    # r => print register
                self.Reg.useToPrint()

            elif command[0] == 'x':                             # exit simulater
                print("-----Simulator End-----\n")
                return 0

            elif command[0] == 'sr' and isExecutable == True:   # sr $XX value => set register $XX to value
                if len(command) != 3:
                    print("Error: Wrong command format!\n")

                else:
                    self.interface.addCommand(setRegister(int(command[1]), int(command[2]), self.Reg))
                    self.interface.runCommand()

            elif command[0] == 'sm' and isExecutable == True:   #sm 0xXXXXXX value => set memory 0xXXXXXX to value
                if len(command) != 3:
                    print("Error: Wrong command format!\n")

                else:
                    self.interface.addCommand(setMemory(int(command[1], 16), int(command[2]), self.MEM))
                    self.interface.runCommand()

            else:
                if isExecutable == False:                       #로드한 프로그램이 실행 불능 상태일 때
                    if isEnd == True:                           #프로그램 실행이 종료된 경우
                        print("-----Program End-----\n")

                    else:                                       #예기치 못한 문제로 프로그램이 실행 불가능한 경우
                        print("Error: Program is unexecutable!\n")

                else:                                           #시뮬레이터에서 지원하지 않는 명령어
                    print("Error: Unsupported Command!\n")

        return 0

main = Facade()
main.run()