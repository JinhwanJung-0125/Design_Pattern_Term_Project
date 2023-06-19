#Memory와 Register 구현은 Bridge Pattern을 적용

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

        for i in range(offset, e_offset + 4):
            if (i % 4) == 0 or i == offset:
                print("\n[0x%X] " % ((front << 20) + i), end="")

            print("%02x" % pM[i], end="")

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