import itertools
import subprocess
import codecs
import ast

def make_file(tt,tt_name,ep_name,str):
    i=len(tt[0])-1
    with open('solver_func/tt/%s'%(tt_name), 'w') as f:
        f.write('.i %d\n.o 1\n.ilb %s\n.ob F\n'%(i,str))
        for t in tt:
            f.write(f'{t}\n')
        f.write('.e')
    with open('solver_func/espresso/%s'%(ep_name), 'w') as fileobj:
        subprocess.call(['/Users/kurahararikuto/sboxanalyzer/espresso/build/espresso',
                     *["-Dmany", "-estrong", "-epos", "-s", "-t", "-of"], # -Dexact
                     'solver_func/tt/%s'%(tt_name)], stdout=fileobj)
    print("end")

def Copy(bit):
    if bit<2:
        print("error")
        exit()
    tt_name=f"integral/Copy_{bit}bit_tt.txt"
    ep_name=f"integral/Copy_{bit}bit_espresso.txt"
    st="a0"
    for i in range(bit):
        st+=f" b{i}"
    tt=[]
    for i in range(2**(bit+1)):
        B=[]
        for j in range(bit):
            B.append((i>>j)&1)
        a=(i>>bit)&1
        check=a
        for b in B:
            check-=b
        if check==0:
            tt.append(f"{i:0{bit+1}b}1")
    print(tt)
    make_file(tt,tt_name,ep_name,st)

def XOR(bit):
    if bit<2:
        print("error")
        exit()
    tt_name=f"integral/XOR_{bit}bit_tt.txt"
    ep_name=f"integral/XOR_{bit}bit_espresso.txt"
    st=""
    for i in range(bit):
        st+=f"a{i} "
    st+="b0"
    tt=[]
    for i in range(2**(bit+1)):
        A=[]
        b=i&1
        for j in range(1,bit+1):
            A.append((i>>j)&1)
        check=-b
        for a in A:
            check+=a
        if check==0:
            tt.append(f"{i:0{bit+1}b}1")
    print(tt)
    make_file(tt,tt_name,ep_name,st)

def Sbox(bit_size,name,read_path):
    tt_name=f"integral/{name}_sbox_tt.txt"
    ep_name=f"integral/{name}_sbox_espresso.txt"
    tt=[]
    st=""
    for i in range(bit_size):
        st+=f"a{i} "
    for i in range(bit_size):
        st+=f"b{i} "
    st=st[:-1]
    tt = []
    temp = []
    with open(read_path,"r") as f:
        lines = f.readlines()
        for i in range(1,len(lines)):
            temp = ast.literal_eval(lines[i].strip())
            temp = "".join(map(str, temp))
            # print(temp)
            tt.append(temp+"1")
    print(len(tt))
    print(tt)
    make_file(tt,tt_name,ep_name,st)


Copy(8)
# XOR(4)
# Sbox(4,"Orthros","solver_func/sbox_integral/out_table/Orthros_out_table.txt")
# Sbox(8,"AES","solver_func/sbox_integral/out_table/AES_out_table.txt")


