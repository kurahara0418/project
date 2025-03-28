from itertools import chain, product
import subprocess
import codecs

AES = [0x63,  0x7c,   0x77,   0x7b,   0xf2,   0x6b,   0x6f,   0xc5,   0x30,   0x01,   0x67,   0x2b,   0xfe,   0xd7,   0xab,   0x76,
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

sbox_Q=[
0x25,0x24,0x73,0x67,0xD7,0xAE,0x5C,0x30,0xA4,0xEE,0x6E,0xCB,0x7D,0xB5,0x82,0xDB,
0xE4,0x8E,0x48,0x49,0x4F,0x5D,0x6A,0x78,0x70,0x88,0xE8,0x5F,0x5E,0x84,0x65,0xE2,
0xD8,0xE9,0xCC,0xED,0x40,0x2F,0x11,0x28,0x57,0xD2,0xAC,0xE3,0x4A,0x15,0x1B,0xB9,
0xB2,0x80,0x85,0xA6,0x2E,0x02,0x47,0x29,0x07,0x4B,0x0E,0xC1,0x51,0xAA,0x89,0xD4,
0xCA,0x01,0x46,0xB3,0xEF,0xDD,0x44,0x7B,0xC2,0x7F,0xBE,0xC3,0x9F,0x20,0x4C,0x64,
0x83,0xA2,0x68,0x42,0x13,0xB4,0x41,0xCD,0xBA,0xC6,0xBB,0x6D,0x4D,0x71,0x21,0xF4,
0x8D,0xB0,0xE5,0x93,0xFE,0x8F,0xE6,0xCF,0x43,0x45,0x31,0x22,0x37,0x36,0x96,0xFA,
0xBC,0x0F,0x08,0x52,0x1D,0x55,0x1A,0xC5,0x4E,0x23,0x69,0x7A,0x92,0xFF,0x5B,0x5A,
0xEB,0x9A,0x1C,0xA9,0xD1,0x7E,0x0D,0xFC,0x50,0x8A,0xB6,0x62,0xF5,0x0A,0xF8,0xDC,
0x03,0x3C,0x0C,0x39,0xF1,0xB8,0xF3,0x3D,0xF2,0xD5,0x97,0x66,0x81,0x32,0xA0,0x00,
0x06,0xCE,0xF6,0xEA,0xB7,0x17,0xF7,0x8C,0x79,0xD6,0xA7,0xBF,0x8B,0x3F,0x1F,0x53,
0x63,0x75,0x35,0x2C,0x60,0xFD,0x27,0xD3,0x94,0xA5,0x7C,0xA1,0x05,0x58,0x2D,0xBD,
0xD9,0xC7,0xAF,0x6B,0x54,0x0B,0xE0,0x38,0x04,0xC8,0x9D,0xE7,0x14,0xB1,0x87,0x9C,
0xDF,0x6F,0xF9,0xDA,0x2A,0xC4,0x59,0x16,0x74,0x91,0xAB,0x26,0x61,0x76,0x34,0x2B,
0xAD,0x99,0xFB,0x72,0xEC,0x33,0x12,0xDE,0x98,0x3B,0xC0,0x9B,0x3E,0x18,0x10,0x3A,
0x56,0xE1,0x77,0xC9,0x1E,0x9E,0x95,0xA3,0x90,0x19,0xA8,0x6C,0x09,0xD0,0xF0,0x86]

def make_file(tt,tt_name,ep_name,str):
    i=len(tt[0])-1
    with open('snow/tt/%s'%(tt_name), 'w') as f:
        f.write('.i %d\n.o 1\n.ilb %s\n.ob F\n'%(i,str))
        for t in tt:
            f.write(f'{t}\n')
        f.write('.e')
    with open('snow/espresso_K2_3g/%s'%(ep_name), 'w') as fileobj:
        subprocess.call(['/Users/kurahararikuto/sboxanalyzer/espresso/build/espresso',
                     *["-Dmany", "-estrong", "-epos", "-s", "-t", "-of"], # -Dexact
                     'snow/tt/%s'%(tt_name)], stdout=fileobj)
    print("end")
def modulo(y,rp):
  n=y.bit_length()-1
  for i in range(n, 7, -1):
    if (y>>i)&1 == 1:
       y^=(rp<<(i-8))
  return y
def times(x, m):
  n=x.bit_length()-1
  y=m<<n
  for i in reversed(range(n)):
    if (x>>i)&1==1:
      y=y^(m<<i)
  return y
def alpha_0():
    tt_name="alpha_0_tt.txt"
    ep_name="alpha_0_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15 b16 b17 b18 b19 b20 b21 b22 b23 b24 b25 b26 b27 b28 b29 b30 b31"
    tt=[]
    ans=[0,0,0,0]
    alpha=[0xb6,0x08,0x6d,0x1a]
    for i in range(2**8):
        for j in range(4):
           ans[j]=modulo(times(alpha[j],i),rp=0b111000011)
        tt.append(f"{i:08b}{ans[0]:08b}{ans[1]:08b}{ans[2]:08b}{ans[3]:08b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_0_0():
    tt_name="alpha_0_0_tt.txt"
    ep_name="alpha_0_0_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    alpha=0xb6
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b111000011)
        tt.append(f"{i:08b}{ans:08b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_0_1():
    tt_name="alpha_0_1_tt.txt"
    ep_name="alpha_0_1_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    alpha=0x08
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b111000011)
        tt.append(f"{i:08b}{ans:08b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_0_2():
    tt_name="alpha_0_2_tt.txt"
    ep_name="alpha_0_2_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    alpha=0x6d
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b111000011)
        tt.append(f"{i:08b}{ans:08b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_0_3():
    tt_name="alpha_0_3_tt.txt"
    ep_name="alpha_0_3_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    alpha=0x1a
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b111000011)
        tt.append(f"{i:08b}{ans:08b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_12():
    tt_name="alpha_12_tt.txt"
    ep_name="alpha_12_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 a8 b0 b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15 b16 b17 b18 b19 b20 b21 b22 b23 b24 b25 b26 b27 b28 b29 b30 b31"
    tt=[]
    ans=[0,0,0,0]
    alpha1=[0xa0,0xf5,0xfc,0x2e]
    alpha2=[0x5b,0xf8,0x7f,0x93]
    for i in range(2**8):
        for j in range(4):
           ans[j]=modulo(times(alpha1[j],i),rp=0b100101101)
        tt.append(f"1{i:08b}{ans[0]:08b}{ans[1]:08b}{ans[2]:08b}{ans[3]:08b}1")
    for i in range(2**8):
        for j in range(4):
           ans[j]=modulo(times(alpha2[j],i),rp=0b101001101)
        tt.append(f"0{i:08b}{ans[0]:08b}{ans[1]:08b}{ans[2]:08b}{ans[3]:08b}1")
    # print(tt)
    # print(len(tt))
    make_file(tt,tt_name,ep_name,s)
def alpha_12_0():
    tt_name="alpha_12_0_tt.txt"
    ep_name="alpha_12_0_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 f0"
    #f0=0でalpha1,f0=1でalpha2
    tt=[]
    alpha=[0xa0,0x5b]
    for i in range(2**8):
        ans=modulo(times(alpha[0],i),rp=0b100101101)
        tt.append(f"{i:08b}{ans:08b}10")
    for i in range(2**8):
        ans=modulo(times(alpha[1],i),rp=0b101001101)
        tt.append(f"{i:08b}{ans:08b}11")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_12_1():
    tt_name="alpha_12_1_tt.txt"
    ep_name="alpha_12_1_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 f0"
    #f0=0でalpha1,f0=1でalpha2
    tt=[]
    alpha=[0xf5,0xf8]
    for i in range(2**8):
        ans=modulo(times(alpha[0],i),rp=0b100101101)
        tt.append(f"{i:08b}{ans:08b}01")
    for i in range(2**8):
        ans=modulo(times(alpha[1],i),rp=0b101001101)
        tt.append(f"{i:08b}{ans:08b}11")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_12_2():
    tt_name="alpha_12_2_tt.txt"
    ep_name="alpha_12_2_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 f0"
    #f0=0でalpha1,f0=1でalpha2
    tt=[]
    alpha=[0xfc,0x7f]
    for i in range(2**8):
        ans=modulo(times(alpha[0],i),rp=0b100101101)
        tt.append(f"{i:08b}{ans:08b}01")
    for i in range(2**8):
        ans=modulo(times(alpha[1],i),rp=0b101001101)
        tt.append(f"{i:08b}{ans:08b}11")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_12_3():
    tt_name="alpha_12_3_tt.txt"
    ep_name="alpha_12_3_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 f0"
    #f0=0でalpha1,f0=1でalpha2
    tt=[]
    alpha=[0x2e,0x93]
    for i in range(2**8):
        ans=modulo(times(alpha[0],i),rp=0b100101101)
        tt.append(f"{i:08b}{ans:08b}01")
    for i in range(2**8):
        ans=modulo(times(alpha[1],i),rp=0b101001101)
        tt.append(f"{i:08b}{ans:08b}11")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_12_p():
    tt_name="alpha_12_p_tt.txt"
    ep_name="alpha_12_p_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 p0"
    #aが全0でp0が0,それ以外1
    tt=[]
    for i in range(2**8):
        if i==0:
            tt.append(f"{i:08b}01")
        else:
            tt.append(f"{i:08b}11")
    make_file(tt,tt_name,ep_name,s)
def alpha_3_p():
    with open('snow/espresso_K2_3g/alpha_3_p.txt', 'w') as f:
        f.write(".p\n")
        f.write("000000000000000000000000000000001\n")
        for i in range(32):
            s=[]
            for j in range(32):
                if j==i:
                    s.append("1")
                else:
                    s.append("-")
            s.append("0")
            s="".join(s)
            # print(s)
            f.write(s)
            f.write("\n")
        f.write(".e\n")
def alpha_3_0():
    tt_name="alpha_3_0_tt.txt"
    ep_name="alpha_3_0_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 f0"
    #f0=0でalpha3,f0=1で全0
    tt=[]
    alpha=0x45
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b101100101)
        tt.append(f"{i:08b}{ans:08b}01")
        tt.append(f"{i:08b}{0:08b}11")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_3_1():
    tt_name="alpha_3_1_tt.txt"
    ep_name="alpha_3_1_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 f0"
    #f0=0でalpha3,f0=1で全0
    tt=[]
    alpha=0x59
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b101100101)
        tt.append(f"{i:08b}{ans:08b}01")
        tt.append(f"{i:08b}{0:08b}11")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_3_2():
    tt_name="alpha_3_2_tt.txt"
    ep_name="alpha_3_2_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 f0"
    #f0=0でalpha3,f0=1で全0
    tt=[]
    alpha=0x56
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b101100101)
        tt.append(f"{i:08b}{ans:08b}01")
        tt.append(f"{i:08b}{0:08b}11")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_3_3():
    tt_name="alpha_3_3_tt.txt"
    ep_name="alpha_3_3_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 f0"
    #f0=0でalpha3,f0=1で全0
    tt=[]
    alpha=0x8b
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b101100101)
        tt.append(f"{i:08b}{ans:08b}01")
        tt.append(f"{i:08b}{0:08b}11")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def shift8():
    tt_name="shift8_tt.txt"
    ep_name="shift8_espresso.txt"
    s="f0 a0 a1 b0"
    #f0=0でシフト、1でそのまま
    #a0がそのまま、a1がシフトした場合
    tt=[]
    for i in range(4):
        a0=(i>>1)&1
        a1=i&1
        tt.append(f"0{i:02b}{a1:01b}1")    
        tt.append(f"1{i:02b}{a0:01b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def Q_DCSAT():
    tt_name="Q_DCSAT_tt.txt"
    ep_name="Q_DCSAT_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 p0 p1 p2 s0"
    tt=[]
    ddt = [[0 for x in range(256)] for _ in range(256)]
    for i,j in product(range(256),range(256)):
        ddt[i^j][sbox_Q[i]^sbox_Q[j]] += 1
    for i in range(2**8):
        for j in range(2**8):
            if ddt[i][j]==256:
                tt.append(f"{i:08b}{j:08b}00001")
            elif ddt[i][j]==2:
                tt.append(f"{i:08b}{j:08b}11101")
            elif ddt[i][j]==4:
                tt.append(f"{i:08b}{j:08b}01101")
            elif ddt[i][j]==6:
                tt.append(f"{i:08b}{j:08b}01111")
            elif ddt[i][j]==8:
                tt.append(f"{i:08b}{j:08b}00101")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def AES_TEST_DCP():
    tt_name="sbox_AES_TEST_tt.txt"
    ep_name="sbox_AES_TEST_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 p0 p1 p2 p3 p4 p5 p6"
    tt=[]
    ddt = [[0 for x in range(256)] for _ in range(256)]
    for i,j in product(range(256),range(256)):
        ddt[i^j][AES[i]^AES[j]] += 1
    for i in range(2**8):
        for j in range(2**8):
            if ddt[i][j]==256:
                tt.append(f"{i:08b}{j:08b}00000001")
            elif ddt[i][j]==2:
                tt.append(f"{i:08b}{j:08b}11111111")
            elif ddt[i][j]==4:
                tt.append(f"{i:08b}{j:08b}01111111")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def Q_mc2():
    tt_name="Q_mc2_tt.txt"
    ep_name="Q_mc2_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    for i in range(2**8):
        ans=i<<1
        if ans>>8:
            ans^=0b101101001
        tt.append(f"{i:08b}{ans:08b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def Q_mc3():
    tt_name="Q_mc3_tt.txt"
    ep_name="Q_mc3_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    for i in range(2**8):
        ans=i<<1
        ans^=i
        if ans>>8:
            ans^=0b101101001
        tt.append(f"{i:08b}{ans:08b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_3g_0():
    tt_name="alpha_3g_0_tt.txt"
    ep_name="alpha_3g_0_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    alpha=0xe1
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b110101001)
        tt.append(f"{i:08b}{ans:08b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_3g_1():
    tt_name="alpha_3g_1_tt.txt"
    ep_name="alpha_3g_1_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    alpha=0x9f
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b110101001)
        tt.append(f"{i:08b}{ans:08b}1")
    print(tt)
    # make_file(tt,tt_name,ep_name,s)
def alpha_3g_2():
    tt_name="alpha_3g_2_tt.txt"
    ep_name="alpha_3g_2_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    alpha=0xcf
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b110101001)
        tt.append(f"{i:08b}{ans:08b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_3g_3():
    tt_name="alpha_3g_3_tt.txt"
    ep_name="alpha_3g_3_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    alpha=0x13
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b110101001)
        tt.append(f"{i:08b}{ans:08b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_3g_inv_0():
    tt_name="alpha_3g_inv_0_tt.txt"
    ep_name="alpha_3g_inv_0_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    alpha=0x18
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b110101001)
        tt.append(f"{i:08b}{ans:08b}1")
    # print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_3g_inv_1():
    tt_name="alpha_3g_inv_1_tt.txt"
    ep_name="alpha_3g_inv_1_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    alpha=0x0f
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b110101001)
        tt.append(f"{i:08b}{ans:08b}1")
    print(tt)
    make_file(tt,tt_name,ep_name,s)
def alpha_3g_inv_2():
    tt_name="alpha_3g_inv_2_tt.txt"
    ep_name="alpha_3g_inv_2_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    alpha=0x40
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b110101001)
        tt.append(f"{i:08b}{ans:08b}1")
    print(tt)
    # make_file(tt,tt_name,ep_name,s)
def alpha_3g_inv_3():
    tt_name="alpha_3g_inv_3_tt.txt"
    ep_name="alpha_3g_inv_3_espresso.txt"
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7"
    tt=[]
    alpha=0xcd
    for i in range(2**8):
        ans=modulo(times(alpha,i),rp=0b110101001)
        tt.append(f"{i:08b}{ans:08b}1")
    print(tt)
    make_file(tt,tt_name,ep_name,s)
def s_add_init():
    tt_name="s_add_init_tt.txt"
    ep_name="s_add_init_espresso.txt"
    s="a0 a1 a2 a3 b0 b1 b2 b3 b4"
    #b0:繰り上がり整数,b1:0.4,b2:0.8,b3:0.2,b4;0.6
    tt=[]
    for i in range(2**4):
        cnt=0
        for j in range(4):
            cnt+=(i>>j)&1
        if cnt==0:
            tt.append(f"{i:04b}000001")
            # 0
        elif cnt==1:
            tt.append(f"{i:04b}010001")
            # 0.4
        elif cnt==2:
            tt.append(f"{i:04b}001001")
            # 0.8
        elif cnt==3:
            tt.append(f"{i:04b}100101")
            # 1.2
        elif cnt==4:
            tt.append(f"{i:04b}100011")
            # 1.6
    print(tt)
    make_file(tt,tt_name,ep_name,s)
def s_add():
    tt_name="s_add_tt.txt"
    ep_name="s_add_espresso.txt"
    s="a0 a1 a2 a3 b0 b1 b2 b3 c0 c1 c2 c3 c4 c5"
    #a0~a3:入力
    #b0:0.2,b1:0.4,b2:0.6,b3:0.8
    #c0,c1:繰り上がり整数,c2:0.2,c3:0.4,c4:0.6,c5;0.8
    tt=[]
    r=[8,6,4,2,4,4,4,4]
    for i in range(2**8):
        sum=0
        for j in range(8):
            sum+=((i>>j)&1)*r[j]
        # print(sum)
        n=sum//10
        m=sum%10
        st=f"{i:08b}"
        if n==0:
            sn="00"
        elif n==1:
            sn="01"
        elif n==2:
            sn="11"
        if m==0:
            sm="00001"
        elif m==2:
            sm="10001"
        elif m==4:
            sm="01001"
        elif m==6:
            sm="00101"
        elif m==8:
            sm="00011"
        tt.append(st+sn+sm)
    print(tt)
    # print(len(tt))
    make_file(tt,tt_name,ep_name,s)
# alpha_0()
# alpha_0_0()
# alpha_0_1()
# alpha_0_2()
# alpha_0_3()
# alpha_12()
# alpha_12_0()
# alpha_12_1()
# alpha_12_2()
# alpha_12_3()
# alpha_12_p()
# alpha_3_p()
# alpha_3_0()
# alpha_3_1()
# alpha_3_2()
# alpha_3_3()
# shift8()
Q_DCSAT()
# AES_TEST_DCP()
# Q_mc2()
# Q_mc3()
# alpha_3g_0()
# alpha_3g_1()
# alpha_3g_2()
# alpha_3g_3()
# alpha_3g_inv_0()
# alpha_3g_inv_1()
# alpha_3g_inv_2()
# alpha_3g_inv_3()
# s_add_init()
# s_add()