
def format_line(code):
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
def format_file(code):
    if len(code) == 0:
        return []
    i = 0
    while i < len(code):
        code[i] = code[i].replace('\n', '')
        temp = format_line(code[i])
        if len(temp) == 0:
            code.pop(i)
        else:
            code[i] = temp
            i += 1
    return code

fin = open('test.asm', 'r')
asm = fin.readlines()
fin.close()
fin = open('Instruction Set.txt', 'r')
ins = fin.readlines()
fin.close()
print(asm)
print(format_file(asm))
print(ins)
print(format_file(ins))