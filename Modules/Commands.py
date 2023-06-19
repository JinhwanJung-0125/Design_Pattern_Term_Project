from io import BufferedReader
from asyncio.windows_events import NULL
from Modules.Memory_Register import Memory, Register, MemoryAccess, RegisterAccess, MemoryRegister
from Modules.ALU import ALU

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