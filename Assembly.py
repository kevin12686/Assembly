
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
            if code[idx][1].find('C') != -1:
                LOC += len(code[idx][1][code[idx][1].find('\'') + 1:-1])
            elif code[idx][1].find('X') != -1:
                LOC += int(len(code[idx][1][code[idx][1].find('\'') + 1:-1]) / 2)
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





fin = open('test.asm', 'r')
asm = fin.readlines()
fin.close()
fin = open('Instruction Set.txt', 'r')
instable = fin.readlines()
fin.close()
#print(asm)
print(Format_File(asm))
#print(instable)
print(Format_File(instable))
print(Init(asm, instable))