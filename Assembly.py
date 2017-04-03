import sys, os

if len(sys.argv) != 4:
    print('python ' + sys.argv[0] + ' <Instruction Set Name> <ASM File Name> <Output File Name>')
    exit()

if not os.path.exists(sys.argv[1]) or not os.path.exists(sys.argv[2]):
    print('Files not Found.')

INSFILE = sys.argv[1]
FILEINPUT = sys.argv[2]
FILEOUTPUT = sys.argv[3]

def Format_Line(code):
    commit = code.find(';')
    if commit != -1:
        code = code[:commit]
    if code == '':
        return []
    code = code.replace('\t', ' ').split(sep=' ')
    i = 0
    while i < len(code):
        if code[i] == '':
            code.pop(i)
        else:
            i += 1
    return code

#Format the file
def Format_File(code):
    if len(code) == 0:
        return []
    i = 0
    while i < len(code):
        code[i] = code[i].replace('\n', '').upper()
        temp = Format_Line(code[i])
        if len(temp) == 0:
            code.pop(i)
        else:
            code[i] = temp
            i += 1
    return code

def FindLab(lab, table):
    for each in table:
        if each[0] == lab:
            return each[1]
    return None

#all return are based on 10
def FindIns(ins, table):
    if ins == 'BYTE':
        return -1, None
    elif ins == 'WORD':
        return -2, None
    elif ins == 'RESB':
        return -3, None
    elif ins == 'RESW':
        return -4, None
    else:
        for each in table:
            if ins == each[0]:
                return int(each[1]), int(each[2], 16)
    return None, None

def Init(code, table):
    NAME = ''
    START = None
    END = None
    LOC = None
    Lable = []
    if code[0][1] == 'START':
        NAME += code[0][0][:6]
        START = LOC = int(code[0][2], 16)
    elif code[0][0] == 'START':
        START = LOC = int(code[0][1], 16)
    else:
        print('\'START\' not found.')
        exit()
    for idx in range(1, len(code) - 1):
        format, opcode = FindIns(code[idx][0], table)
        if format == None:
            Lable.insert(len(Lable), [code[idx][0], LOC])
            code[idx].pop(0)
            format, opcode = FindIns(code[idx][0], table)
        if format == None:
            print('Instruction Error')
            exit()
        elif format == -1:
            Length = len(code[idx][1][code[idx][1].find('\'') + 1:-1])
            if code[idx][1].find('C') != -1:
                LOC += Length
            elif code[idx][1].find('X') != -1:
                if Length % 2 != 0:
                    Length += 1
                LOC += int(Length / 2)
        elif format == -2:
            LOC += 3
        elif format == -3:
            LOC += int(code[idx][1])
        elif format == -4:
            LOC += int(code[idx][1]) * 3
        else:
            LOC += format
    for each in code[len(code) - 1]:
        if each == 'END':
            END = LOC
    if END == None:
        print('\'END\' not found.')
        exit()
    return NAME, START, END, Lable, code

def FillBits(code, char, length):
    return (char * (length - len(code))) + code

def ASCII(code):
    Temp = ''
    for char in code:
        Temp += hex(ord(char))[2:]
    return Temp

fin = open(FILEINPUT, 'r')
asm = fin.readlines()
fin.close()
fin = open(INSFILE, 'r')
instable = fin.readlines()
fin.close()

asm = Format_File(asm)
instable = Format_File(instable)
NAME, START, END, LABLE, asm = Init(asm, instable)
asm.pop(0)
asm.pop(len(asm) - 1)
ObjectProgram = [('H' + NAME + (' ' * (6 - len(NAME))) + FillBits(hex(START)[2:], '0', 6) + FillBits(hex(END - START)[2:], '0', 6)).upper() + '\n']
END = START
temp = 'T' + FillBits(hex(END)[2:], '0', 6)
RS = False
for each in asm:
    if int((len(temp) - 7) / 2) >= 28:
        ObjectProgram += [(temp[:7] + FillBits(hex(int(len(temp[7:]) / 2))[2:], '0', 2) + temp[7:]).upper() + '\n']
        temp = 'T' + FillBits(hex(END)[2:], '0', 6)
        RS = True
    if each[0] == 'BYTE':
        RS = False
        if each[1][0] == 'C':
            temp += ASCII(each[1][each[1].find('\'') + 1:-1])
            END += len(each[1][each[1].find('\'') + 1:-1])
        elif each[1][0] == 'X':
            t = each[1][each[1].find('\'') + 1:-1]
            Length = len(t)
            if Length % 2 != 0:
                temp += '0' + t
            else:
                temp += t
            END += int(Length / 2)
        else:
            print('Instruction Error.')
            exit()
    elif each[0] == 'WORD':
        RS = False
        each[1] = hex(int(each[1]))[2:]
        if len(each[1]) > 6:
            print('Instruction Error')
            exit()
        temp += FillBits(each[1], '0', 6)
        END += 3
    elif each[0] == 'RESB':
        if not RS:
            ObjectProgram += [(temp[:7] + FillBits(hex(int(len(temp[7:]) / 2))[2:], '0', 2) + temp[7:]).upper() + '\n']
        END += int(each[1])
        temp = 'T' + FillBits(hex(END)[2:], '0', 6)
        RS = True
    elif each[0] == 'RESW':
        if not RS:
            ObjectProgram += [(temp[:7] + FillBits(hex(int(len(temp[7:]) / 2))[2:], '0', 2) + temp[7:]).upper() + '\n']
        END += int(each[1]) * 3
        temp = 'T' + FillBits(hex(END)[2:], '0', 6)
        RS = True
    else:
        RS = False
        format, opcode = FindIns(each[0], instable)
        opcode = hex(opcode)[2:]
        if len(opcode) < 2:
            opcode = '0' + opcode
        if len(each) == 1:
            temp += opcode + '0000'
        else:
            if len(each) == 2:
                comma = each[1].find(',')
                if comma == -1:
                    address = FindLab(each[1], LABLE)
                    if address == None:
                        print('Instruction Error')
                        exit()
                    else:
                        temp += opcode + FillBits(hex(address)[2:], '0', 4)
                else:
                    before = each[1][:comma]
                    after = each[1][comma + 1:]
                    if after == 'X':
                        address = FindLab(before, LABLE)
                        if address == None:
                            print('Instruction Error')
                            exit()
                        else:
                            temp += opcode + hex((32768 | address) )[2:]
                    else:
                        print('Instruction Error')
                        exit()
            elif len(each) == 3:
                comma = each[1].find(',')
                if comma != -1:
                    if each[2] == 'X':
                        address = FindLab(each[1][:-1], LABLE)
                        if address == None:
                            print('Instruction Error')
                            exit()
                        else:
                            temp += opcode + hex((32768 | address))[2:]
                    else:
                        print('Instruction Error')
                        exit()
                else:
                    comma = each[2].find(',')
                    if comma != -1 and each[2][comma + 1:] == 'X':
                        address = FindLab(each[1], LABLE)
                        if address == None:
                            print('Instruction Error')
                            exit()
                        else:
                            temp += opcode + hex((32768 | address))[2:]
                    else:
                        print('Instruction Error')
                        exit()
            else:
                print('Instruction Error')
                exit()
        END += int(format)
ObjectProgram += [(temp[:7] + FillBits(hex(int(len(temp[7:]) / 2))[2:], '0', 2) + temp[7:]).upper() + '\n']
ObjectProgram += [('E' + FillBits(hex(START)[2:], '0', 6)).upper()]

print('Object Code : \n')
for each in ObjectProgram:
    print(each, end='')

fout = open(FILEOUTPUT, 'w')
fout.writelines(ObjectProgram)
fout.flush()
fout.close()

print('\n\n\'' + FILEOUTPUT + '\' Outputed.')

