from itertools import chain, product
import subprocess
import codecs

s = [0x63,  0x7c,   0x77,   0x7b,   0xf2,   0x6b,   0x6f,   0xc5,   0x30,   0x01,   0x67,   0x2b,   0xfe,   0xd7,   0xab,   0x76,
    0xca,   0x82,   0xc9,   0x7d,   0xfa,   0x59,   0x47,   0xf0,   0xad,   0xd4,   0xa2,   0xaf,   0x9c,   0xa4,   0x72,   0xc0,
    0xb7,   0xfd,   0x93,   0x26,   0x36,   0x3f,   0xf7,   0xcc,   0x34,   0xa5,   0xe5,   0xf1,   0x71,   0xd8,   0x31,   0x15,
    0x04,   0xc7,   0x23,   0xc3,   0x18,   0x96,   0x05,   0x9a,   0x07,   0x12,   0x80,   0xe2,   0xeb,   0x27,   0xb2,   0x75,
    0x09,   0x83,   0x2c,   0x1a,   0x1b,   0x6e,   0x5a,   0xa0,   0x52,   0x3b,   0xd6,   0xb3,   0x29,   0xe3,   0x2f,   0x84,
    0x53,   0xd1,   0x00,   0xed,   0x20,   0xfc,   0xb1,   0x5b,   0x6a,   0xcb,   0xbe,   0x39,   0x4a,   0x4c,   0x58,   0xcf,
    0xd0,   0xef,   0xaa,   0xfb,   0x43,   0x4d,   0x33,   0x85,   0x45,   0xf9,   0x02,   0x7f,   0x50,   0x3c,   0x9f,   0xa8,
    0x51,   0xa3,   0x40,   0x8f,   0x92,   0x9d,   0x38,   0xf5,   0xbc,   0xb6,   0xda,   0x21,   0x10,   0xff,   0xf3,   0xd2,
    0xcd,   0x0c,   0x13,   0xec,   0x5f,   0x97,   0x44,   0x17,   0xc4,   0xa7,   0x7e,   0x3d,   0x64,   0x5d,   0x19,   0x73,
    0x60,   0x81,   0x4f,   0xdc,   0x22,   0x2a,   0x90,   0x88,   0x46,   0xee,   0xb8,   0x14,   0xde,   0x5e,   0x0b,   0xdb,
    0xe0,   0x32,   0x3a,   0x0a,   0x49,   0x06,   0x24,   0x5c,   0xc2,   0xd3,   0xac,   0x62,   0x91,   0x95,   0xe4,   0x79,
    0xe7,   0xc8,   0x37,   0x6d,   0x8d,   0xd5,   0x4e,   0xa9,   0x6c,   0x56,   0xf4,   0xea,   0x65,   0x7a,   0xae,   0x08,
    0xba,   0x78,   0x25,   0x2e,   0x1c,   0xa6,   0xb4,   0xc6,   0xe8,   0xdd,   0x74,   0x1f,   0x4b,   0xbd,   0x8b,   0x8a,
    0x70,   0x3e,   0xb5,   0x66,   0x48,   0x03,   0xf6,   0x0e,   0x61,   0x35,   0x57,   0xb9,   0x86,   0xc1,   0x1d,   0x9e,
    0xe1,   0xf8,   0x98,   0x11,   0x69,   0xd9,   0x8e,   0x94,   0x9b,   0x1e,   0x87,   0xe9,   0xce,   0x55,   0x28,   0xdf,
    0x8c,   0xa1,   0x89,   0x0d,   0xbf,   0xe6,   0x42,   0x68,   0x41,   0x99,   0x2d,   0x0f,   0xb0,   0x54,   0xbb,   0x16]
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
def AES_sbox():
    tt_name="AES_sbox_tt.txt"
    ep_name="AES_sbox_espresso.txt"
    st="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 p0 p1 p2 p3 p4 p5 p6"
    ddt = [[0 for x in range(256)] for _ in range(256)]
    for i,j in product(range(256),range(256)):
        ddt[i^j][s[i]^s[j]] += 1

    tt=[]
    for x,value in zip(range(256*256), chain.from_iterable(ddt)):
        if x == 0:
            tt.append(f'{x:016b}00000001')
        elif value != 0:
            if value == 2:
                tt.append(f'{x:016b}11111111')
            elif value == 4:
                tt.append(f'{x:016b}01111111')
    make_file(tt,tt_name,ep_name,st)
def AES_sbox_DCSAT():
    tt_name="AES_sbox_DCSAT_tt.txt"
    ep_name="AES_sbox_DCSAT_espresso.txt"
    st="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 p0 p1"
    ddt = [[0 for x in range(256)] for _ in range(256)]
    for i,j in product(range(256),range(256)):
        ddt[i^j][s[i]^s[j]] += 1
    tt=[]
    for x,value in zip(range(256*256), chain.from_iterable(ddt)):
        if x == 0:
            tt.append(f'{0:016b}001')
        elif value != 0:
            if value == 2:
                tt.append(f'{x:016b}111')
            elif value == 4:
                tt.append(f'{x:016b}011')
    # print(tt)
    make_file(tt,tt_name,ep_name,st)
def AES_sbox_AS():
    tt_name="AES_sbox_AS_tt.txt"
    ep_name="AES_sbox_AS_espresso.txt"    
    st = "a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 c0"
    ddt = [[0 for x in range(256)] for _ in range(256)]
    for i,j in product(range(256),range(256)):
        ddt[i^j][s[i]^s[j]] += 1
    tt=[]
    for x,value in zip(range(256*256), chain.from_iterable(ddt)):
        if x == 0:
            tt.append(f'{0:016b}01')
        elif value != 0:
            tt.append(f'{x:016b}11')
    print(tt)
    # make_file(tt,tt_name,ep_name,st)
def AES_sbox_lim():
    tt_name="AES_sbox_lim_tt.txt"
    ep_name="AES_sbox_lim_espresso.txt"
    st="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 p0 p1 p2 p3 p4 p5 p6"
    ddt = [[0 for x in range(256)] for _ in range(256)]
    for i,j in product(range(256),range(256)):
        ddt[i^j][s[i]^s[j]] += 1
    tt=[]
    for x,value in zip(range(256*256), chain.from_iterable(ddt)):
        if x == 0:
            tt.append(f'{0:016b}00000001')
        elif value == 2 or value == 4:
            tt.append(f'{x:016b}11111111')
    # print(tt)
    make_file(tt,tt_name,ep_name,st)
def xor_2bit():
    tt_name="xor_2bit_tt.txt"
    ep_name="xor_2bit_espresso.txt"
    s="a0 a1 b0"
    tt=[]
    for i in range(2**2):
        result=0
        for j in range(2):
            result^=(i>>j)&1
        if result:
            tt.append(f'{i:02b}11')
        else:
            tt.append(f'{i:02b}01')
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def xor_3bit():
    tt_name="xor_3bit_tt.txt"
    ep_name="xor_3bit_espresso.txt"
    s="a0 a1 a2 b0"
    tt=[]
    for i in range(2**3):
        result=0
        for j in range(3):
            result^=(i>>j)&1
        if result:
            tt.append(f'{i:03b}11')
        else:
            tt.append(f'{i:03b}01')
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def xor_not_3bit():
    tt_name="xor_3bit_not_tt.txt"
    ep_name="xor_3bit_not_espresso.txt"
    s="a0 a1 a2 b0"
    tt=[]
    for i in range(2**3):
        result=0
        for j in range(3):
            result^=(i>>j)&1
        if not result:
            tt.append(f'{i:03b}01')
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def xor_4bit():
    tt_name="xor_4bit_tt.txt"
    ep_name="xor_4bit_espresso.txt"
    s="a0 a1 a2 a3 b0"
    tt=[]
    for i in range(2**4):
        result=0
        for j in range(4):
            result^=(i>>j)&1
        if result:
            tt.append(f'{i:04b}11')
        else:
            tt.append(f'{i:04b}01')
    # print(tt)
    # make_file(tt,tt_name,ep_name,s)
def xor_5bit():
    tt_name="xor_5bit_tt.txt"
    ep_name="xor_5bit_espresso.txt"
    s="a0 a1 a2 a3 a4 b0"
    tt=[]
    for i in range(2**5):
        result=0
        for j in range(5):
            result^=(i>>j)&1
        if result:
            tt.append(f'{i:05b}11')
        else:
            tt.append(f'{i:05b}01')
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def xor_6bit():
    tt_name="xor_6bit_tt.txt"
    ep_name="xor_6bit_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 b0"
    tt=[]
    for i in range(2**6):
        result=0
        for j in range(6):
            result^=(i>>j)&1
        if result:
            tt.append(f'{i:06b}11')
        else:
            tt.append(f'{i:06b}01')
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def xor_7bit():
    tt_name="xor_7bit_tt.txt"
    ep_name="xor_7bit_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 b0"
    tt=[]
    for i in range(2**7):
        result=0
        for j in range(7):
            result^=(i>>j)&1
        if result:
            tt.append(f'{i:07b}11')
        else:
            tt.append(f'{i:07b}01')
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def mc2_time():
    tt=[]
    tt_name="mc2_time_tt.txt"
    ep_name="mc2_time_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    for i in range(2**8):
        result=i<<1
        if result>>8:
            result^=0x11b
        tt.append(f'{i:08b}{result:08b}1')
    print(tt)
    make_file(tt,tt_name,ep_name,s)
def mc3_time():
    tt=[]
    tt_name="mc3_time_tt.txt"
    ep_name="mc3_time_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7" 
    for i in range(2**8):
        t=i<<1 
        result=t^i
        if result>>8:
            result^=0x11b
        tt.append(f'{i:08b}{result:08b}1')
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def A_mul_x():
    tt=[]
    tt_name="A_mul_x_tt.txt"
    ep_name="A_mul_x_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 a15 b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15" 
    for i in range(2**16):
        result=i<<1
        if result>>16:
            result^=0x1990f
        tt.append(f'{i:016b}{result:016b}1')
    # print(tt)
    # make_file(tt,tt_name,ep_name,s)  
def A_invmul_x():
    flag=False
    tt=[]
    tt_name="A_invmul_x_tt.txt"
    ep_name="A_invmul_x_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 a15 b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15" 
    for i in range(2**16):
        if i&1:
            flag=True
        result=i>>1
        if flag:
            result^=0xcc87
            flag=False
        tt.append(f'{i:016b}{result:016b}1')
    # print(tt)
    # make_file(tt,tt_name,ep_name,s)
def B_mul_x():
    tt=[]
    tt_name="B_mul_x_tt.txt"
    ep_name="B_mul_x_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 a15 b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15" 
    for i in range(2**16):
        result=i<<1
        if result>>16:
            result^=0x1c963
        tt.append(f'{i:016b}{result:016b}1')
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def B_invmul_x():
    flag=False
    tt=[]
    tt_name="B_invmul_x_tt.txt"
    ep_name="B_invmul_x_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 a15 b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15" 
    for i in range(2**16):
        if i&1==1:
            flag=True
        result=i>>1
        if flag:
            result^=0xe4b1
            flag=False
        tt.append(f'{i:016b}{result:016b}1')
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def carry_2bit():
    tt=[]
    tt_name="carry_2bit_tt.txt"
    ep_name="carry_2bit_espresso.txt"
    s="a0 a1 b0"
    for i in range(4):
        ans=0
        for j in range(2):
            ans|=(i>>j)&1
        tt.append(f"{i:02b}{ans:b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def carry_3bit():
    tt=[]
    tt_name="carry_3bit_tt.txt"
    ep_name="carry_3bit_espresso.txt"
    s="a0 a1 a2 b0"
    for i in range(2**3):
        cnt=0
        for j in range(3):
            cnt+=(i>>j)&1
        if cnt>1:
            tt.append(f"{i:03b}11")
        else:
            tt.append(f"{i:03b}01")            
    # print(tt)
    make_file(tt,tt_name,ep_name,s)  
def addition_32():
    with open('/Users/kurahararikuto/Documents/python/snowv/espresso/addition_32.txt', 'w') as f:
        f.write(".p\n")
        value=[["0","0","1","0","0","0"],["0","1","0","0","0","0"],
            ["1","0","0","0","0","0"],["1","1","1","0","0","0"],
            ["0","0","0","1","1","1"],["0","1","1","1","1","1"],
            ["1","0","1","1","1","1"],["1","1","0","1","1","1"]]
        m=31
        for i in range(m):
            for j in range(8):
                a=["-" for _ in range(32)]
                b=["-" for _ in range(32)]
                c=["-" for _ in range(32)]
                a[i]=value[j][0]
                b[i]=value[j][1]
                c[i]=value[j][2]
                a[i+1]=value[j][3]
                b[i+1]=value[j][4]
                c[i+1]=value[j][5]
                a="".join(a)
                b="".join(b)
                c="".join(c)
                f.write(a)
                f.write(b)
                f.write(c)
                f.write("\n")
        f.write(".e")
def weight_32():
    with open('/Users/kurahararikuto/Documents/python/snowv/espresso/weight_32.txt', 'w') as f:
        f.write(".p\n")
        m=31
        order=["acw","bcw","abw","abcw","abcw"]
        value=["100","010","010","0001","1111"]
        for i in range(m):
            for j in range(5):
                a=list("-" for _ in range(32))
                b=list("-" for _ in range(32))
                c=list("-" for _ in range(32))
                w=list("-" for _ in range(31))
                for k in range(len(order[j])):
                    if order[j][k]=="a":
                        a[i+1]=value[j][k]
                    if order[j][k]=="b":
                        b[i+1]=value[j][k]
                    if order[j][k]=="c":
                        c[i+1]=value[j][k]
                    if order[j][k]=="w":
                        w[i]=value[j][k]
                a="".join(a)
                b="".join(b)
                c="".join(c)
                w="".join(w)
                f.write(a)
                f.write(b)
                f.write(c)
                f.write(w)
                f.write("\n")
        f.write(".e")
def weight_4():
    with open('snow/espresso/weight_4.txt', 'w') as f:
        f.write(".p\n")
        m=3
        order=["acw","bcw","abw","abcw","abcw"]
        value=["100","010","010","0001","1111"]
        for i in range(m):
            for j in range(5):
                a=list("-" for _ in range(4))
                b=list("-" for _ in range(4))
                c=list("-" for _ in range(4))
                w=list("-" for _ in range(3))
                for k in range(len(order[j])):
                    if order[j][k]=="a":
                        a[i+1]=value[j][k]
                    if order[j][k]=="b":
                        b[i+1]=value[j][k]
                    if order[j][k]=="c":
                        c[i+1]=value[j][k]
                    if order[j][k]=="w":
                        w[i]=value[j][k]
                a="".join(a)
                b="".join(b)
                c="".join(c)
                w="".join(w)
                f.write(a)
                f.write(b)
                f.write(c)
                f.write(w)
                f.write("\n")
        f.write(".e")
def addition_4():
    with open('/Users/kurahararikuto/Documents/python/snowv/espresso/addition_4.txt', 'w') as f:
        f.write(".p\n")
        value=[["0","0","1","0","0","0"],["0","1","0","0","0","0"],
            ["1","0","0","0","0","0"],["1","1","1","0","0","0"],
            ["0","0","0","1","1","1"],["0","1","1","1","1","1"],
            ["1","0","1","1","1","1"],["1","1","0","1","1","1"]]
        for i in range(3):
            for j in range(8):
                a=list("----")
                b=list("----")
                c=list("----")
                a[i]=value[j][0]
                b[i]=value[j][1]
                c[i]=value[j][2]
                a[i+1]=value[j][3]
                b[i+1]=value[j][4]
                c[i+1]=value[j][5]
                a="".join(a)
                b="".join(b)
                c="".join(c)
                f.write(a)
                f.write(b)
                f.write(c)
                f.write("\n")
        f.write(".e")
def modulo_4():
    flag=False
    tt=[]
    tt_name="4_modulo_tt.txt"
    ep_name="4_modulo_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 a15 b0 b1 b2 b3 b4 b5 b6 b7"
    for i in range(2**4-1):
        for j in range(i+1,2**4):
            total=i+j
            if total&0b10000:
                total^=0b10000
            tt.append(f"{i:04b}{j:04b}{total:04b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def xor_2in_4bit_v1():
    with open('/Users/kurahararikuto/Documents/python/snowv/espresso/xor_2in_4bit_v1.txt', 'w') as f:
        f.write(".p\n")
        value=["001","010","100","111"]
        for i in range(4):
            for j in range(4):
                a=list("----")
                b=list("----")
                c=list("----")
                a[3-i]=value[j][0]
                b[3-i]=value[j][1]
                c[3-i]=value[j][2]
                a="".join(a)
                b="".join(b)
                c="".join(c)
                f.write(a)
                f.write(b)
                f.write(c)
                f.write("\n")
        f.write(".e")
def xor_2in_4bit_v2():
    with open('/Users/kurahararikuto/Documents/python/snowv/espresso/xor_2in_4bit_v2.txt', 'w') as f:
        f.write(".p\n")
        value=["001","010","100","111"]
        for i in range(4):
            for j in range(4):
                a=list("----")
                b=list("----")
                c=list("----")
                a[i]=value[j][0]
                b[i]=value[j][1]
                c[i]=value[j][2]
                a="".join(a)
                b="".join(b)
                c="".join(c)
                f.write(a)
                f.write(b)
                f.write(c)
                f.write("\n")
        f.write(".e")
def aes_modulo():
    tt=[]
    tt_name="aes_modulo_tt.txt"
    ep_name="aes_modulo_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 a8 b0 b1 b2 b3 b4 b5 b6 b7"
    for i in range(2**9):
        if (i>>8):
            result=(i^0b11011)&0xff
        else:
            result=i&0xff
        tt.append(f"{i:09b}{result:08b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def iv_lim():
    tt_name="iv_lim_tt.txt"
    ep_name="iv_lim_espresso.txt"
    st=[]
    for i in range(128):
        st.append("a")
        st.append(f"{i}")
        st.append(" ")
    st="".join(st)
    tt=[]
    x=1
    for i in range(128):
        y=x<<i
        tt.append(f'{y:0128b}1')
    # print(tt)
    make_file(tt,tt_name,ep_name,st)
def iv_hw2_lim():
    tt_name="iv_hw2_lim_tt.txt"
    ep_name="iv_hw2_lim_espresso.txt"
    st=[]
    for i in range(128):
        st.append("a")
        st.append(f"{i}")
        st.append(" ")
    st="".join(st)
    tt=[]
    for i in range(127):
        x=1<<i
        tt.append(f'{x:0128b}1')
        for j in range(i+1,128):
            y=1<<j
            z=y^x
            tt.append(f'{z:0128b}1')
    # print(tt)
    make_file(tt,tt_name,ep_name,st)
def key_lim():
    tt_name="key_lim_tt.txt"
    ep_name="key_lim_espresso.txt"
    st=[]
    for i in range(256):
        st.append("a")
        st.append(f"{i}")
        st.append(" ")
    st="".join(st)
    tt=[]
    x=1
    for i in range(256):
        y=x<<i
        tt.append(f'{y:0256b}1')
    # print(tt)
    make_file(tt,tt_name,ep_name,st)
def viA_mul_x():
    tt=[]
    tt_name="viA_mul_x_tt.txt"
    ep_name="viA_mul_x_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 a15 b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15" 
    for i in range(2**16):
        result=i<<1
        if result>>16:
            result^=0x14a6d
        tt.append(f'{i:016b}{result:016b}1')
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def viB_mul_x():
    tt=[]
    tt_name="viB_mul_x_tt.txt"
    ep_name="viB_mul_x_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 a15 b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15" 
    for i in range(2**16):
        result=i<<1
        if result>>16:
            result^=0x1cc87
        tt.append(f'{i:016b}{result:016b}1')
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def mix_7():
    tt=[]
    tt_name="mix_7_tt.txt"
    ep_name="mix_7_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3"
    tt=[]
    for i in range(2**8):
        st=[]
        input=[[]for _ in range(8)]
        output=[[]for _ in range(4)]
        for j in range(8):
            input[7-j]=1&(i>>j)
        # print(input)
        output[0]=input[0]^input[1]^input[5]^input[6]^input[7]
        output[1]=input[1]^input[2]^input[4]^input[6]^input[7]
        output[2]=input[2]^input[3]^input[4]^input[5]^input[7]
        output[3]=input[0]^input[3]^input[4]^input[5]^input[6]
        # print(output)
        for k in range(8):
            st.append(f"{input[k]:01b}")
        for k in range(4):
            st.append(f"{output[k]:01b}")
        st.append("1")
        tt.append("".join(st))
    # print(tt)
    # print(len(tt))
    make_file(tt,tt_name,ep_name,s)
def mix_346():
    tt=[]
    tt_name="mix_346_tt.txt"
    ep_name="mix_346_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 b0 b1 b2 b3"
    tt=[]
    for i in range(2**12):
        st=[]
        input=[[]for _ in range(12)]
        output=[[]for _ in range(4)]
        for j in range(12):
            input[11-j]=1&(i>>j)
        # print(input)
        output[0]=input[0]^input[1]^input[5]^input[6]^input[7]^input[8]^input[9]
        output[1]=input[1]^input[2]^input[4]^input[6]^input[7]^input[9]^input[10]
        output[2]=input[2]^input[3]^input[4]^input[5]^input[7]^input[10]^input[11]
        output[3]=input[0]^input[3]^input[4]^input[5]^input[6]^input[8]^input[11]
        # print(output)
        for k in range(12):
            st.append(f"{input[k]:01b}")
        for k in range(4):
            st.append(f"{output[k]:01b}")
        st.append("1")
        tt.append("".join(st))
    make_file(tt,tt_name,ep_name,s)
def mix_0125():
    tt_name="mix_0125_tt.txt"
    ep_name="mix_0125_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3"
    tt=[]
    for i in range(2**8):
        st=[]
        input=[[]for _ in range(8)]
        output=[[]for _ in range(4)]
        for j in range(8):
            input[7-j]=1&(i>>j)
        # print(input)
        output[0]=input[1]^input[2]^input[3]^input[4]^input[5]
        output[1]=input[0]^input[2]^input[3]^input[5]^input[6]
        output[2]=input[0]^input[1]^input[3]^input[6]^input[7]
        output[3]=input[0]^input[1]^input[2]^input[4]^input[7]
        # print(output)
        for k in range(8):
            st.append(f"{input[k]:01b}")
        for k in range(4):
            st.append(f"{output[k]:01b}")
        st.append("1")
        tt.append("".join(st))
    make_file(tt,tt_name,ep_name,s)
def addition_2():
    tt_name="addition_2_tt.txt"
    ep_name="addition_2_espresso.txt"
    s="a0 a1 a2 a3 w0"
    tt=[]
    for i in range(2**5):
        a=(i>>4)&1
        b=(i>>3)&1
        c=(i>>2)&1
        a2=(i>>1)&1
        w=i&1
        if w==0:
            if a^b^c^a2==0:
                tt.append(f"{i:05b}1")
        else:
            tt.append(f"{i:05b}1")
    make_file(tt,tt_name,ep_name,s)
def weight_2():
    tt_name="weight_2_tt.txt"
    ep_name="weight_2_espresso.txt"
    s="a0 a1 a2 w0"
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
    make_file(tt,tt_name,ep_name,s)
def snowvi_key_lim():
    tt_name="snowvi_key_lim_tt.txt"
    ep_name="snowvi_key_lim_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    for i in range(2**16):
        input=(i>>8)&0xff
        output=i&0xff
        if input==0:
            if output==0:
                tt.append(f"{input:08b}{output:08b}1")
        else:
            if output!=0:
                tt.append(f"{input:08b}{output:08b}1")
    print(tt)
    # make_file(tt,tt_name,ep_name,s)
def snowvi_key_lim2():
    tt_name="snowvi_key_lim2_tt.txt"
    ep_name="snowvi_key_lim2_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 f0"
    tt=[]
    for i in range(2**8):
        if i==0:
            tt.append(f"{i:08b}01")
        else:
            tt.append(f"{i:08b}11")
    print(tt)
    make_file(tt,tt_name,ep_name,s)
def and_2bit():
    tt_name="and_2bit_tt.txt"
    ep_name="and_2bit_espresso.txt"
    s="w0 w1 c0"
    tt=[]
    tt.append("0001")
    tt.append("0101")
    tt.append("1001")
    tt.append("1111")
    print(tt)
    make_file(tt,tt_name,ep_name,s)
def and_2bit_weight():
    tt_name="and_2bit_weight_tt.txt"
    ep_name="and_2bit_weight_espresso.txt"
    st="a0 a1 b0 w1"
    tt=[]
    for i in range(2):
        for j in range(2):
            for k in range(2):
                if i==j==0:
                    if k==0:
                        tt.append(f"{i:01b}{j:01b}{k:01b}01")
                else:
                    tt.append(f"{i:01b}{j:01b}{k:01b}11")
    print(tt)
    make_file(tt,tt_name,ep_name,st)
def and_16bit():
    tt_name="and_16bit.txt"
    ep_name="and_16bit_espresso.txt"
    s="a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13,a14,a15,b0"
    tt=[]
    for i in range(2**16):
        count=0
        for j in range(15):
            if (i>>j)&1:
                count+=1
        if count%2:
            tt.append(f"{i:016b}11")
        else:
            tt.append(f"{i:016b}01")
    print(tt)
    make_file(tt,tt_name,ep_name,s)
def comp_7to3():
    tt_name="comp_7to3.txt"
    ep_name="comp_7to3_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 b0 b1 b2"
    tt=[]
    for i in range(2**7):
        count=0
        for j in range(7):
            if (i>>j)&1:
                count+=1
        tt.append(f"{i:07b}{count:03b}1")
    # print(len(tt))
    make_file(tt,tt_name,ep_name,s)
def comp_15to4():
    tt_name="comp_15to4.txt"
    ep_name="comp_15to4_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 b0 b1 b2 b3"
    tt=[]
    for i in range(2**15):
        count=0
        for j in range(15):
            if (i>>j)&1:
                count+=1
        tt.append(f"{i:015b}{count:04b}1")
    print(tt)
    make_file(tt,tt_name,ep_name,s)
def or_2bit():
    tt_name="or_2bit_weight_tt.txt"
    ep_name="or_2bit_weight_espresso.txt"
    st="a0 a1 b0"
    tt=[]
    tt.append("0001")
    tt.append("0111")
    tt.append("1011")
    tt.append("1111")
    print(tt)
    make_file(tt,tt_name,ep_name,st)
def v_addition():
    tt_name="v_addition_tt.txt"
    ep_name="v_addition_espresso.txt"
    s="a0 a1 a2 a3 a4 a5"
    tt=[]
    for i in range(2**6):
        ux=(i>>5)&1
        uy=(i>>4)&1
        uz=(i>>3)&1
        lx=(i>>2)&1
        ly=(i>>1)&1
        lz=i&1
        if (lx^ly) == lz:
            lc = 0
        else:
            lc = 1
        if (lx+ly+lc)>1:
            uc = 1
        else:
            uc = 0
        if (ux^uy^uc) == uz:
            tt.append(f"{i:06b}1")
    print(len(tt))
    make_file(tt,tt_name,ep_name,s)
def equal():
    tt_name="equal.txt"
    ep_name="equal_espresso.txt"
    s="a0 a1"
    tt=["001","111"]
    print(tt)
    make_file(tt,tt_name,ep_name,s)

# AES_sbox()
# AES_sbox_AS()
# AES_sbox_DCSAT()
# AES_sbox_lim()
# xor_2bit()
# xor_3bit()
# xor_not_3bit()
# xor_4bit()
# xor_5bit()
# xor_6bit()
# xor_7bit()
# mc2_time()
# mc3_time()
# A_mul_x()
# A_invmul_x()
# B_mul_x()
# B_invmul_x()
# addition_32()
# addition_4()
# weight_32()
# weight_4()
# carry_2bit()
# up_3bit()
# modulo_4()
# xor_2in_4bit_v1()
# xor_2in_4bit_v2()
# aes_modulo()
# iv_lim()
# iv_hw2_lim()
# key_lim()
# viA_mul_x()
# viB_mul_x()
# mix_7()
# mix_346()
# mix_0125()
# addition_2()
# weight_2()
# snowvi_key_lim()
# snowvi_key_lim2()
# and_2bit()
# and_2bit_weight()
# and_16bit()
# comp_7to3()
# comp_15to4()
# or_2bit()
# v_addition()
equal()