from itertools import chain, product
import subprocess
import codecs

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
def make_cell(word):
    cell=[0 for _ in range(4)]
    for i in range(4):
        cell[i]=(word >> (i*8)) & 0xff
    return cell
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
def alpha_time(x,al_num):
    y=[0,0,0,0]
    x_cell=make_cell(x)
    for i in range(4):
        # print(hex(alpha[al_num][i]))
        y[i]=modulo(times(alpha[al_num][i],x_cell[3]),rp[al_num])
    # print(y)
    return (y[0]<<24)^(y[1]<<16)^(y[2]<<8)^y[3]

alpha=[[0xb6,0x08,0x6d,0x1a],[0xa0,0xf5,0xfc,0x2e],[0x5b,0xf8,0x7f,0x93],[0x45,0x59,0x56,0x8b]]
rp=[0b111000011,0b100101101,0b101001101,0b101100101]

def alpha_12_DDT(al_num1, al_num2):
    DDT=[[0 for i in range(2**8)]for j in range(2**16)]
    num1=24-8*al_num1
    num2=24-8*al_num2
    for din in range(2**8):
        for a in range(2**8):
            b=a^din
            a=a<<24
            b=b<<24
            alpha_out1=alpha_time(a,1)
            alpha_out2=alpha_time(b,2)
            # print(hex(out1))
            out1=(alpha_out1>>num1)&0xff
            out2=(alpha_out2>>num1)&0xff
            out3=(alpha_out1>>num2)&0xff
            out4=(alpha_out2>>num2)&0xff
            dout1=out1^out2
            dout2=out3^out4
            dinout1=(din<<8)^dout1
            # print("din=",end="")
            # print(hex(din))
            # print("dout1=",end="")
            # print(hex(dout1))
            # print("din+dout=",end="")
            # print(hex(dinout1))
            DDT[dinout1][dout2]+=1
    return DDT

def alpha_3_DDT(al_num1, al_num2):
    DDT=[[0 for i in range(2**8)]for j in range(2**16)]
    num1=24-8*al_num1
    num2=24-8*al_num2
    for din in range(2**8):
        for a in range(2**8):
            b=a^din
            a=a<<24
            # b=b<<24
            alpha_out1=alpha_time(a,3)
            alpha_out2=b
            out1=(alpha_out1>>num1)&0xff
            out2=(alpha_out2>>num1)&0xff
            out3=(alpha_out1>>num2)&0xff
            out4=(alpha_out2>>num2)&0xff
            dout1=out1^out2
            dout2=out3^out4
            dinout1=(din<<8)^dout1
            # print("din=",end="")
            # print(hex(din))
            # print("dout1=",end="")
            # print(hex(dout1))
            # print("din+dout=",end="")
            # print(hex(dinout1))
            DDT[dinout1][dout2]+=1
    return DDT

def alpha_12_test(byte1,byte2):
    tt_name="alpha_12_byte(%d,%d)_tt.txt"%(byte1,byte2)
    ep_name="alpha_12_byte(%d,%d)_espresso.txt"%(byte1,byte2)
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 c0 c1 c2 c3 c4 c5 c6 c7 f0"
    tt=[]
    DDT=alpha_12_DDT(byte1,byte2)
    for i in range(2**16):
        for j in range(2**8):
            if DDT[i][j]!=0:
                tt.append(f"{i:016b}{j:08b}11")
            tt.append(f"{i:016b}{j:08b}01")
    # print(tt)
    print(len(tt))
    print(len(DDT))
    make_file(tt,tt_name,ep_name,s)

def alpha_3_test(byte1,byte2):
    tt_name="alpha_3_byte(%d,%d)_tt.txt"%(byte1,byte2)
    ep_name="alpha_3_byte(%d,%d)_espresso.txt"%(byte1,byte2)
    s="a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 c0 c1 c2 c3 c4 c5 c6 c7 f0"
    tt=[]
    DDT=alpha_3_DDT(byte1,byte2)
    for i in range(2**16):
        for j in range(2**8):
            if DDT[i][j]!=0:
                tt.append(f"{i:016b}{j:08b}11")
            tt.append(f"{i:016b}{j:08b}01")
    # print(tt)
    print(len(tt))
    print(len(DDT))
    make_file(tt,tt_name,ep_name,s)

def alpha_sbox():
    tt_name="alpha_sbox_tt.txt"%(byte1,byte2)
    ep_name="alpha_sbox_espresso.txt"%(byte1,byte2)
    sbox=[]
    tt = []
    for i in range(256):
        sbox.append(modulo((i << 34), 0x14d))
    for i in range(256):
        sbox.append(modulo((i << 230), 0x12d))
    

# alpha_12_test(1,0)
# alpha_3_test(2,3)
