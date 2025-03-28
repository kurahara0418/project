from itertools import chain, product
import subprocess
import codecs

def make_file(tt,tt_name,ep_name,str):
    i=len(tt[0])-1
    with open('solver_func/tt/signed/%s'%(tt_name), 'w') as f:
        f.write('.i %d\n.o 1\n.ilb %s\n.ob F\n'%(i,str))
        for t in tt:
            f.write(f'{t}\n')
        f.write('.e')
    with open('solver_func/espresso/signed/%s'%(ep_name), 'w') as fileobj:
        subprocess.call(['/Users/kurahararikuto/sboxanalyzer/espresso/build/espresso',
                     *["-Dmany", "-estrong", "-epos", "-s", "-t", "-of"], # -Dexact
                     'solver_func/tt/signed/%s'%(tt_name)], stdout=fileobj)
    print("end")

def gen_str(num,bit):
    out = ""
    cnt = 0
    for i in range(bit-1,0,-1):
        temp = num // (3**i)
        if temp == 0:
            out += "="
            cnt += 1
        elif temp == 1:
            out += "u"
        else:
            out += "n"
        num -= (3**i)*(temp)
    if (num % 3) == 0:
        out += "="
        cnt += 1
    elif (num % 3) == 1:
        out += "u"
    else:
        out += "n"
    return out,cnt

def char_to_cnf(char):
    if char=="=":
        return "00"
    if char=="u":
        return "11"
    if char=="n":
        return "01"

def char_to_num(char):
    if char == "0":
        return 0,0
    if char == "1":
        return 1,1
    if char == "u":
        return 1,0
    if char == "n":
        return 0,1

def convert_str(out1,out2,bit):
    out = ""
    str1 = f"{out1:0{bit}b}"
    str2 = f"{out2:0{bit}b}"
    for i in range(bit):
        n1 = str1[i]
        n2 = str2[i]
        if n1 == n2:
            char = "="
        elif n1 == "1":
            char = "u"
        else:
            char = "n"
        out+=char
    return out

def F_add_c():
    table3 = {'===':'==','==n':'n=','==u':'u=','=n=':'n=','=u=':'u=','=nn':'=n','=un':'==','=nu':'==','=uu':'=u','n==':'n=','u==':'u=','n=n':'=n','u=n':'==','n=u':'==','u=u':'=u','nn=':'=n','nu=':'==','un=':'==','uu=':'=u','nnn':'nn','nun':'n=','unn':'n=','nnu':'n=','uun':'u=','unu':'u=','nuu':'u=','uuu':'uu'}
    tt_name="F_add_c_tt.txt"
    ep_name="F_add_c_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 b0 b1 b2 b3"
    tt=[]
    bit=3
    for i in range(3**bit):
        state = gen_str(i,bit)
        state+=table3[state]
        temp=""
        for char in state:
            temp+=char_to_num(char)
        tt.append(temp+"1")
    print(tt)
    # make_file(tt,tt_name,ep_name,s)

def F_add_z():
    table4 = {'nn':['=n'],'uu':['=u'],'nu':['=='],'un':['=='],'n=':['n=','un'],'u=':['u=','nu'],'=n':['n=','un'],'=u':['u=','nu'],'==':['==']}
    tt_name="F_add_z_tt.txt"
    ep_name="F_add_z_espresso.txt"
    s="a0 a1 a2 a3 b0 b1 b2 b3 p0"
    tt=[]
    bit=2
    for i in range(3**bit):
        state1 = gen_str(i,bit)
        state2 = table4[state1]
        p=str(len(state2)-1)
        # print(state1)
        # print(p)
        for state_temp in state2:
            temp=""
            state=state1+state_temp
            for char in state:
                temp+= char_to_num(char)
            tt.append(temp+p+"1")
    # print(tt)
    # make_file(tt,tt_name,ep_name,s)

def Ch():
    tt_name="Ch_tt.txt"
    ep_name="Ch_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 b0 b1 p0 p1"
    tt=[]
    bit = 3
    data = []
    outs = ["=","u","n"]
    for i in range(3**bit):
        state,cnt = gen_str(i,bit)
        temps=[state]
        for j in range(2**cnt):
            if cnt == 0:
                temps.append(state)
                break
            bins = format(j,f"0{cnt}b")
            temp = ""
            l=0
            for k in range(bit):
                if state[k] == "=":
                    temp += bins[l]
                    l+=1
                else:
                    temp += state[k]
            temps.append(temp)
        e_cnt = [0,0,0]
        for temp in temps[1:]:
            e1=0
            e2=0
            e1_temp=[0,0,0]
            e2_temp=[0,0,0]
            # print(temp)
            for i in range(bit):
                e1_temp[i],e2_temp[i]=char_to_num(temp[i])
            e1=(e1_temp[0]&e1_temp[1])^((not e1_temp[0])&e1_temp[2])
            e2=(e2_temp[0]&e2_temp[1])^((not e2_temp[0])&e2_temp[2])
            if e1 == e2:
                e_cnt[0]+=1
            elif e1 == 1:
                e_cnt[1]+=1
            else:
                e_cnt[2]+=1
        for i in range(3):
            out = outs[i]
            if e_cnt[i]==0:
                continue
            if cnt==0:
                p="00"
            else:
                p = (e_cnt[i])/(2**cnt)
                if p==1.0:
                    p="00"
                elif p==0.5:
                    p="01"
                elif p==0.25:
                    p="11"
                else:
                    print(p)
            str_=""
            for char in (temps[0]+out):
                # print(char)
                cnf=char_to_cnf(char)
                str_+=cnf
            # print(str_+p)
            tt.append(str_+p+"1")
    # print(tt)
    # print(len(tt))
    make_file(tt,tt_name,ep_name,s)
def Maj():
    tt_name="Maj_tt.txt"
    ep_name="Maj_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 b0 b1 p0"
    tt=[]
    bit = 3
    data = []
    outs = ["=","u","n"]
    for i in range(3**bit):
        state,cnt = gen_str(i,bit)
        temps=[state]
        for j in range(2**cnt):
            if cnt == 0:
                temps.append(state)
                break
            bins = format(j,f"0{cnt}b")
            temp = ""
            l=0
            for k in range(bit):
                if state[k] == "=":
                    temp += bins[l]
                    l+=1
                else:
                    temp += state[k]
            temps.append(temp)
        e_cnt = [0,0,0]
        for temp in temps[1:]:
            e1=0
            e2=0
            e1_temp=[0,0,0]
            e2_temp=[0,0,0]
            # print(temp)
            for i in range(bit):
                e1_temp[i],e2_temp[i]=char_to_num(temp[i])
            e1=(e1_temp[0]&e1_temp[1])^(e1_temp[1]&e1_temp[2])^(e1_temp[2]&e1_temp[0])
            e2=(e2_temp[0]&e2_temp[1])^(e2_temp[1]&e2_temp[2])^(e2_temp[2]&e2_temp[0])
            if e1 == e2:
                e_cnt[0]+=1
            elif e1 == 1:
                e_cnt[1]+=1
            else:
                e_cnt[2]+=1
        for i in range(3):
            out = outs[i]
            if e_cnt[i]==0:
                continue
            if cnt==0:
                p="0"
            else:
                p = (e_cnt[i])/(2**cnt)
                if p==1.0:
                    p="0"
                elif p==0.5:
                    p="1"
                # elif p==0.25:
                #     p="11"
                else:
                    print(p)
            str_=""
            for char in (temps[0]+out):
                # print(char)
                cnf=char_to_cnf(char)
                str_+=cnf
            # print(str_+p)
            tt.append(str_+p+"1")
    # print(tt)
    # print(len(tt))
    make_file(tt,tt_name,ep_name,s)
def XOR_3():
    tt_name="XOR_3_tt.txt"
    ep_name="XOR_3_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 b0 b1 p0"
    tt=[]
    bit = 3
    data = []
    outs = ["=","u","n"]
    for i in range(3**bit):
        state,cnt = gen_str(i,bit)
        temps=[state]
        for j in range(2**cnt):
            if cnt == 0:
                temps.append(state)
                break
            bins = format(j,f"0{cnt}b")
            temp = ""
            l=0
            for k in range(bit):
                if state[k] == "=":
                    temp += bins[l]
                    l+=1
                else:
                    temp += state[k]
            temps.append(temp)
        e_cnt = [0,0,0]
        for temp in temps[1:]:
            e1=0
            e2=0
            # print(temp)
            for i in range(bit):
                e1_temp,e2_temp=char_to_num(temp[i])
                # print(str_)
                e1^=e1_temp
                e2^=e2_temp
            if e1 == e2:
                e_cnt[0]+=1
            elif e1 == 1:
                e_cnt[1]+=1
            else:
                e_cnt[2]+=1
        for i in range(3):
            out = outs[i]
            if e_cnt[i]==0:
                continue
            if cnt==0:
                p="0"
            else:
                p = (e_cnt[i])/(2**cnt)
                if p==1.0:
                    p="0"
                elif p==0.5:
                    p="1"
                else:
                    print(p)
            str_=""
            for char in (temps[0]+out):
                # print(char)
                cnf=char_to_cnf(char)
                str_+=cnf
            # print(str_+p)
            tt.append(str_+p+"1")
    # print(tt)
    # print(len(tt))
    make_file(tt,tt_name,ep_name,s)
def XOR_4():
    tt_name="XOR_4_tt.txt"
    ep_name="XOR_4_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 p0"
    tt=[]
    bit = 4
    data = []
    outs = ["=","u","n"]
    for i in range(3**bit):
        state,cnt = gen_str(i,bit)
        temps=[state]
        for j in range(2**cnt):
            if cnt == 0:
                temps.append(state)
                break
            bins = format(j,f"0{cnt}b")
            temp = ""
            l=0
            for k in range(bit):
                if state[k] == "=":
                    temp += bins[l]
                    l+=1
                else:
                    temp += state[k]
            temps.append(temp)
        e_cnt = [0,0,0]
        for temp in temps[1:]:
            e1=0
            e2=0
            # print(temp)
            for i in range(bit):
                e1_temp,e2_temp=char_to_num(temp[i])
                # print(str_)
                e1^=e1_temp
                e2^=e2_temp
            if e1 == e2:
                e_cnt[0]+=1
            elif e1 == 1:
                e_cnt[1]+=1
            else:
                e_cnt[2]+=1
        for i in range(3):
            out = outs[i]
            if e_cnt[i]==0:
                continue
            if cnt==0:
                p="0"
            else:
                p = (e_cnt[i])/(2**cnt)
                if p==1.0:
                    p="0"
                elif p==0.5:
                    p="1"
                else:
                    print(p)
            str_=""
            for char in (temps[0]+out):
                # print(char)
                cnf=char_to_cnf(char)
                str_+=cnf
            # print(str_+p)
            tt.append(str_+p+"1")
    # print(tt)
    # print(len(tt))
    make_file(tt,tt_name,ep_name,s)
def equal():
    tt_name="equal_tt.txt"
    ep_name="equal_espresso.txt"
    s="a0 a1 a2 a3"
    tt=[]
    tt.append("00001")
    tt.append("11111")
    tt.append("01011")
    make_file(tt,tt_name,ep_name,s)
def F_add_lsv():
    tt_name="F_add_lsv_tt.txt"
    ep_name="F_add_lsv_espresso.txt"
    s="e0 e1 c0 c1 "
    tt=[]
    tt.append("00001")
    tt.append("11111")
    tt.append("01011")
    make_file(tt,tt_name,ep_name,s)

# F_add_c()
# F_add_z()
# Ch()
# Maj()
# XOR_3()
# XOR_4()
equal()

