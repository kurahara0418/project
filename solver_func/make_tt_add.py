from itertools import chain, product
import subprocess
import codecs


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

def weight_a():
    tt_name="weight_a_tt.txt"
    ep_name="weight_a_espresso.txt"
    st="a0 a1 a2"
    tt=[]
    for i in range(2):
        for j in range(2):
            if i==j:
                tt.append(f"{i:01b}{j:01b}11")
            else:
                tt.append(f"{i:01b}{j:01b}01")
    print(tt)
    make_file(tt,tt_name,ep_name,st)
def weight_b():
    tt_name="weight_b_tt.txt"
    ep_name="weight_b_espresso.txt"
    st="a0 a1 a2"
    tt=[]
    for i in range(2):
        for j in range(2):
            if i==j==1:
                tt.append(f"{i:01b}{j:01b}01")
            else:
                tt.append(f"{i:01b}{j:01b}11")
    print(tt)
    make_file(tt,tt_name,ep_name,st)
def add_check():
    tt_name="add_check_tt.txt"
    ep_name="add_check_espresso.txt"
    st="a0 a1 a2"
    tt=[]
    for i in range(2**3):
        xor_temp=(i>>2)&1
        w_temp_a=(i>>1)&1
        w_temp_b=i&1
        # print(i)
        if w_temp_a==w_temp_b==1:
            if xor_temp==0:
                tt.append(f"{i:03b}1")
        else:
            tt.append(f"{i:03b}1")
    print(tt)
    make_file(tt,tt_name,ep_name,st)
def add_check2():
    tt_name="add_check2_tt.txt"
    ep_name="add_check2_espresso.txt"
    st="a0 a1"
    tt=[]
    tt.append("001")
    tt.append("011")
    tt.append("111")
    make_file(tt,tt_name,ep_name,st)
def add_w():
    tt_name="add_w_tt.txt"
    ep_name="add_w_espresso.txt"
    st="a0 a1 a2 a3 a4 a5 a6"
    tt=[]
    for i in range(2**7):
        w=i&1
        c_u=(i>>1)&1
        b_u=(i>>2)&1
        a_u=(i>>3)&1
        c=(i>>4)&1
        b=(i>>5)&1
        a=(i>>6)&1
        if a_u==b_u==c_u:
            if w==0:
                if a_u^a^b^c==0:
                    tt.append(f"{i:07b}1")
        else:
            if w==1:
                tt.append(f"{i:07b}1")
    print(tt)
    make_file(tt,tt_name,ep_name,st)
def addition():
    tt_name="addition_tt.txt"
    ep_name="addition_espresso.txt"
    st="a0 a1 a2 a3 a4 a5"
    tt=[]
    for i in range(2**6):
        a=(i>>5)&1
        b=(i>>4)&1
        c=(i>>3)&1
        a_u=(i>>2)&1
        b_u=(i>>1)&1
        c_u=i&1
        if a_u==b_u==c_u:
            if a_u^a^b^c==0:
                tt.append(f"{i:06b}1")
        else:
            tt.append(f"{i:06b}1")
    print(tt)
    make_file(tt,tt_name,ep_name,st)
def weight():
    tt_name="weight_tt.txt"
    ep_name="weight_espresso.txt"
    st="a0 a1 a2 a3"
    tt=[]
    for i in range(2**3):
        a=(i>>2)&1
        b=(i>>1)&1
        c=i&1
        if a==b==c:
            tt.append(f"{i:03b}01")
        else:
            tt.append(f"{i:03b}11")
    print(tt)
    make_file(tt,tt_name,ep_name,st)
def hw():
    tt_name="hw_tt.txt"
    ep_name="hw_espresso.txt"
    st="a0 a1 a2"
    tt=[]
    for i in range(2):
        for j in range(2):
            if i==j==0:
                tt.append(f"{i:01b}{j:01b}01")
            else:
                tt.append(f"{i:01b}{j:01b}11")
    print(tt)
    make_file(tt,tt_name,ep_name,st)
def conv():
    #temp:outの暫定 a_u:1つ右の入力　
    #wが1だったらなんでもあり、0だったらout=a_u^temp
    tt_name="conv_tt.txt"
    ep_name="conv_espresso.txt"
    st="a0 a1 a2 b0"
    tt=[]
    for i in range(2**4):
        temp=(i>>3)&1
        a_u=(i>>2)&1
        w=(i>>1)&1
        out=i&1
        if w==1:
            if out^temp^a_u==0:
                tt.append(f"{i:04b}1")
        else:
            tt.append(f"{i:04b}1")
    print(tt)
    make_file(tt,tt_name,ep_name,st)
def def_add_flag():
    tt_name="def_add_flag_tt.txt"
    ep_name="def_add_flag_espresso.txt"
    st="a0 a1 a2 f0"
    tt=[]
    for i in range(2**4):
        flag=i&1
        alfa=(i>>1)&1
        beta=(i>>2)&1
        gamma=(i>>3)&1
        if alfa==beta==gamma:
            if alfa==flag==0:
                tt.append(f"{i:04b}1")
            elif alfa==flag==1:
                tt.append(f"{i:04b}1")
        else:
            tt.append(f"{i:04b}1")
    print(tt)
    make_file(tt,tt_name,ep_name,st)
def add_flag():
    tt_name="add_flag_tt.txt"
    ep_name="add_flag_espresso.txt"
    st="a0 a1 a2 f0"
    tt=[]
    for i in range(2**4):
        flag=i&1
        alfa=(i>>1)&1
        beta=(i>>2)&1
        gamma=(i>>3)&1
        if alfa^beta^flag==gamma:
            tt.append(f"{i:04b}1")
    print(tt)
    make_file(tt,tt_name,ep_name,st)


# and_2bit()
# weight_a()
# weight_b()
# add_check()
add_check2()
# add_w()
# addition()
# weight()
# hw()
# conv()
# def_add_flag()
# add_flag()