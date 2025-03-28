from itertools import chain, product
import subprocess
import codecs

def Orthros_Integral(cnf,in0,in1,in2,in3,out0,out1,out2,out3):
    #石川さんのコード
    cnf.append([in0,-out1,-out3])
    cnf.append([in2,-out0,-out2])
    cnf.append([in3,-out0,-out1])
    cnf.append([in0,-out1,-out2])
    cnf.append([in0,in1,in2,in3,-out3])
    cnf.append([in0,in1,in2,in3,-out2])
    cnf.append([in0,in1,in2,in3,-out0])
    cnf.append([in0,in1,in2,in3,-out1])
    cnf.append([-in0,out0,out1,out2,out3])
    cnf.append([-in2,out0,out1,out2,out3])
    cnf.append([-in1,out0,out1,out2,out3])
    cnf.append([-in3,out0,out1,out2,out3])
    cnf.append([-out0,out2,-out3])
    cnf.append([out0,-out2,-out3])
    cnf.append([in1,-out1,-out3])
    cnf.append([in0,-in2,-in3,-out0])
    cnf.append([-in0,-in1,out1,-out3])
    cnf.append([-in0,-in1,-in2,-in3,out3])
    cnf.append([-in0,in2,-in3,-out1,out3])
    cnf.append([in3,-out0,-out2])
    cnf.append([-in0,-in2,-in3,out0,-out1,out2])
    cnf.append([-in0,-in2,out0,out1,out3])
    cnf.append([in3,-out1,-out2])
    cnf.append([-out0,-out1,-out2,out3])
    cnf.append([in3,-out1,-out3])
    cnf.append([out1,-out2,-out3])
    cnf.append([-in2,-in3,out1,out2,out3])
    cnf.append([in2,-out0,-out1])

def get_espresso_result_cnf(espresso_result_file, vars, espresso_cnf_out=None):
    with open(espresso_result_file, 'r') as fileobj:
        espresso_output = fileobj.readlines()
    # Parse the output of ESPRESSO
    #
    bd = len(vars)
    sat_clauses = []
    starting_point = 0
    end_point = 0
    for i in range(len(espresso_output)):
        if ".p" in espresso_output[i]:
            starting_point = i + 1
        if ".e" in espresso_output[i]:
            end_point = i
    for l in espresso_output[starting_point:end_point]:
        line = l[0:bd]
        orclause = []
        for i in range(bd):
            if line[i] == '0':
                orclause.append(vars[i])
            elif line[i] == '1':
                orclause.append(-vars[i])
        sat_clauses.append(orclause)
    if espresso_cnf_out != None:
        print(*sat_clauses, sep='\n', file=codecs.open(espresso_cnf_out, 'w', 'utf-8'))
    return sat_clauses

def Copy2(cnf,input0,output0,output1):
    cnf.append([-output0,-output1])
    cnf.append([input0,-output1])
    cnf.append([input0,-output0])
    cnf.append([-input0,output0,output1])

def Copy3(cnf,input0,output0,output1,output2):
    cnf.append([-output1,-output2])
    cnf.append([-output0,-output2])
    cnf.append([input0,-output2])
    cnf.append([-output0,-output1])
    cnf.append([input0,-output1])
    cnf.append([input0,-output0])
    cnf.append([-input0,output0,output1,output2])

def Copy4(cnf,input0,output0,output1,output2,output3):
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/integral/Copy_4bit_espresso.txt", [input0,output0,output1,output2,output3]))

def Copy5(cnf,input0,output0,output1,output2,output3,output4):
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/integral/Copy_5bit_espresso.txt", [input0,output0,output1,output2,output3,output4]))

def Copy8(cnf,input0,output0,output1,output2,output3,output4,output5,output6,output7):
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/integral/Copy_8bit_espresso.txt", [input0,output0,output1,output2,output3,output4,output5,output6,output7]))

def Copy9(cnf,input0,output0,output1,output2,output3,output4,output5,output6,output7,output8):
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/integral/Copy_9bit_espresso.txt", [input0,output0,output1,output2,output3,output4]))

def And(cnf,input0,input1,output):
    cnf.append([-input1,output])
    cnf.append([-input0,output])
    cnf.append([input0,input1,-output])    

def XOR_2bit(cnf,input0,input1,output):
    cnf.append([-input0,-input1])
    cnf.append([-input1,output])
    cnf.append([-input0,output])
    cnf.append([input0,input1,-output])

def XOR_3bit(cnf,input0,input1,input2,output):
    cnf.append([-input1,-input2])
    cnf.append([-input0,-input2])
    cnf.append([-input0,-input1])
    cnf.append([-input2,output])
    cnf.append([-input1,output])
    cnf.append([-input0,output])
    cnf.append([input0,input1,input2,-output])

def XOR_4bit(cnf,input0,input1,input2,input3,output):
    vars=[input0,input1,input2,input3,output]
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/integral/XOR_4bit_espresso.txt",vars))

def Copy2_array(cnf,input0,output0,output1):
    n=len(input0)
    if not len(input0) == len(output0) == len(output1):
        print("copy2 error")
    for bit in range(n):
        Copy2(cnf,input0[bit],output0[bit],output1[bit])

def Copy3_array(cnf,input0,output0,output1,output2):
    n=len(input0)
    for bit in range(n):
        Copy3(cnf,input0[bit],output0[bit],output1[bit],output2[bit])

def Copy9_array(cnf,input0,output0,output1,output2,output3,output4,output5,output6,output7,output8):
    n=len(input0)
    for bit in range(n):
        Copy9(cnf,input0,output0,output1,output2,output3,output4,output5,output6,output7,output8)

def And_array(cnf,input0,input1,output):
    n=len(input0)
    for bit in range(n):
        And(cnf,input0[bit],input1[bit],output[bit])

def XOR_2bit_array(cnf,input0,input1,output):
    n=len(input0)
    for bit in range(n):
        XOR_2bit(cnf,input0[bit],input1[bit],output[bit])

def XOR_3bit_array(cnf,input0,input1,input2,output):
    n=len(input0)
    if not len(input0) == len(input1) == len(input2) == len(output):
        print("copy2 error")
    for bit in range(n):
        XOR_3bit(cnf,input0[bit],input1[bit],input2[bit],output[bit])

def XOR_4bit_array(cnf,input0,input1,input2,input3,output):
    n=len(input0)
    for bit in range(n):
        XOR_4bit(cnf,input0[bit],input1[bit],input2[bit],input3[bit],output[bit])

def ADDITION(cnf,num,a,b,d):
    BIT_LEN=len(a)
    a_copy=[]
    b_copy=[]
    for i in range(2):
        a_copy.append([_ for _ in range(num,num+BIT_LEN-1)])
        num+=BIT_LEN-1
        b_copy.append([_ for _ in range(num,num+BIT_LEN-1)])
        num+=BIT_LEN-1
    a_copy.append([_ for _ in range(num,num+BIT_LEN-2)])
    num+=BIT_LEN-2
    b_copy.append([_ for _ in range(num,num+BIT_LEN-2)])
    num+=BIT_LEN-2

    v,m,g,r,q,carry = [],[],[],[],[],[]
    v += [_ for _ in range(num,num+BIT_LEN-2)]
    num += BIT_LEN-2
    m += [_ for _ in range(num,num+BIT_LEN-2)]
    num += BIT_LEN-2
    g += [_ for _ in range(num,num+BIT_LEN-2)]
    num += BIT_LEN-2
    r += [_ for _ in range(num,num+BIT_LEN-2)]
    num += BIT_LEN-2
    q += [_ for _ in range(num,num+BIT_LEN-2)]
    num += BIT_LEN-2
    carry += [_ for _ in range(num,num+(BIT_LEN-1))]
    num += BIT_LEN-1

    #最下位bitの処理
    n=len(a)-1
    Copy2(cnf,a[n],a_copy[0][n-1],a_copy[1][n-1])
    Copy2(cnf,b[n],b_copy[0][n-1],b_copy[1][n-1])
    XOR_2bit(cnf,a_copy[0][n-1],b_copy[0][n-1],d[n])
    And(cnf,a_copy[1][n-1],b_copy[1][n-1],carry[n-1])
    #中間bitの処理
    for bit in range(1,n):
        Copy2(cnf,carry[bit],g[bit-1],r[bit-1])
        Copy3(cnf,a[bit],a_copy[0][bit-1],a_copy[1][bit-1],a_copy[2][bit-1])
        Copy3(cnf,b[bit],b_copy[0][bit-1],b_copy[1][bit-1],b_copy[2][bit-1])
        XOR_3bit(cnf,a_copy[0][bit-1],b_copy[0][bit-1],g[bit-1],d[bit])
        And(cnf,a_copy[1][bit-1],b_copy[1][bit-1],v[bit-1])
        XOR_2bit(cnf,a_copy[2][bit-1],b_copy[2][bit-1],m[bit-1])
        And(cnf,m[bit-1],r[bit-1],q[bit-1])
        XOR_2bit(cnf,v[bit-1],q[bit-1],carry[bit-1])
        # Copy2(cnf,carry[bit-1],g[bit-2],r[bit-2])
    #最上位bitの処理
    XOR_3bit(cnf,a[0],b[0],carry[0],d[0])
    return num

def XOR_92(cnf,num,x,y):
    c_num = [2, 2, 2, 2, 2, 3, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 3, 2, 5, 5, 2, 2, 2, 2, 2, 3, 3, 4, 3, 2, 3, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1]
    c = [[]for _ in range(len(c_num))]
    for i in range(len(c_num)):
        for j in range(c_num[i]):
            c[i].append(num)
            num += 1
    y_t = []
    t = []
    for i in range(60):
        t.append(num)
        num += 1
    for i in range(10):
        y_t.append(num)
        num += 1
    Copy2(cnf,x[24], c[0][0], c[0][1])
    Copy2(cnf,x[8], c[1][0], c[1][1])
    Copy2(cnf,x[3], c[2][0], c[2][1])
    Copy2(cnf,x[18], c[3][0], c[3][1])
    Copy2(cnf,x[14], c[4][0], c[4][1])
    Copy3(cnf,x[28], c[5][0], c[5][1], c[5][2])
    Copy2(cnf,x[27], c[6][0], c[6][1])
    Copy2(cnf,x[2], c[7][0], c[7][1])
    Copy2(cnf,x[31], c[8][0], c[8][1])
    Copy3(cnf,x[0], c[9][0], c[9][1], c[9][2])
    Copy2(cnf,x[6], c[10][0], c[10][1])
    Copy2(cnf,x[1], c[11][0], c[11][1])
    Copy2(cnf,x[23], c[12][0], c[12][1])
    Copy2(cnf,x[17], c[13][0], c[13][1])
    Copy2(cnf,x[15], c[14][0], c[14][1])
    Copy2(cnf,x[29], c[15][0], c[15][1])
    Copy2(cnf,x[25], c[16][0], c[16][1])
    Copy3(cnf,x[13], c[17][0], c[17][1], c[17][2])
    Copy2(cnf,x[26], c[18][0], c[18][1])
    Copy2(cnf,x[20], c[19][0], c[19][1])
    Copy2(cnf,x[19], c[20][0], c[20][1])
    Copy2(cnf,x[4], c[21][0], c[21][1])
    Copy3(cnf,x[5], c[22][0], c[22][1], c[22][2])
    Copy2(cnf,x[30], c[23][0], c[23][1])
    Copy5(cnf,t[0], c[24][0], c[24][1], c[24][2], c[24][3], c[24][4])
    Copy5(cnf,t[1], c[25][0], c[25][1], c[25][2], c[25][3], c[25][4])
    Copy2(cnf,t[2], c[26][0], c[26][1])
    Copy2(cnf,t[3], c[27][0], c[27][1])
    Copy2(cnf,t[4], c[28][0], c[28][1])
    Copy2(cnf,t[5], c[29][0], c[29][1])
    Copy2(cnf,t[6], c[30][0], c[30][1])
    Copy3(cnf,t[7], c[31][0], c[31][1], c[31][2])
    Copy3(cnf,t[8], c[32][0], c[32][1], c[32][2])
    Copy4(cnf,t[9], c[33][0], c[33][1], c[33][2], c[33][3])
    Copy3(cnf,t[10], c[34][0], c[34][1], c[34][2])
    Copy2(cnf,t[11], c[35][0], c[35][1])
    Copy3(cnf,t[13], c[36][0], c[36][1], c[36][2])
    Copy2(cnf,t[14], c[37][0], c[37][1])
    Copy2(cnf,t[15], c[38][0], c[38][1])
    Copy3(cnf,t[16], c[39][0], c[39][1], c[39][2])
    Copy2(cnf,t[17], c[40][0], c[40][1])
    Copy2(cnf,t[18], c[41][0], c[41][1])
    Copy2(cnf,t[19], c[42][0], c[42][1])
    Copy2(cnf,t[21], c[43][0], c[43][1])
    Copy2(cnf,t[22], c[44][0], c[44][1])
    Copy2(cnf,t[23], c[45][0], c[45][1])
    Copy2(cnf,t[25], c[46][0], c[46][1])
    Copy2(cnf,t[26], c[47][0], c[47][1])
    Copy2(cnf,t[27], c[48][0], c[48][1])
    Copy2(cnf,t[28], c[49][0], c[49][1])
    Copy2(cnf,t[29], c[50][0], c[50][1])
    Copy2(cnf,t[31], c[51][0], c[51][1])
    Copy2(cnf,t[34], c[52][0], c[52][1])
    Copy2(cnf,t[37], c[53][0], c[53][1])
    Copy2(cnf,t[42], c[54][0], c[54][1])
    Copy2(cnf,t[43], c[55][0], c[55][1])
    Copy2(cnf,t[44], c[56][0], c[56][1])
    Copy2(cnf,t[45], c[57][0], c[57][1])
    Copy2(cnf,t[47], c[58][0], c[58][1])
    Copy2(cnf,t[50], c[59][0], c[59][1])
    Copy2(cnf,t[52], c[60][0], c[60][1])
    Copy2(cnf,t[56], c[61][0], c[61][1])
    Copy2(cnf,t[57], c[62][0], c[62][1])
    Copy2(cnf,t[58], c[63][0], c[63][1])
    Copy2(cnf,y_t[0], c[64][0], y[2])
    Copy2(cnf,y_t[1], c[65][0], y[13])
    Copy2(cnf,y_t[2], c[66][0], y[7])
    Copy2(cnf,y_t[3], c[67][0], y[4])
    Copy2(cnf,y_t[4], c[68][0], y[16])
    Copy2(cnf,y_t[5], c[69][0], y[9])
    Copy2(cnf,y_t[6], c[70][0], y[27])
    Copy2(cnf,y_t[7], c[71][0], y[1])
    Copy3(cnf,y_t[8], c[72][0], c[72][1], y[31])
    Copy2(cnf,y_t[9], c[73][0], y[17])


    XOR_2bit(cnf,x[16],c[0][0],t[0])
    XOR_2bit(cnf,c[1][0],c[0][1],t[1])
    XOR_2bit(cnf,c[2][0],x[11],t[2])
    XOR_2bit(cnf,x[10],c[3][0],t[3])
    XOR_2bit(cnf,c[4][0],x[22],t[4])
    XOR_2bit(cnf,x[12],c[5][0],t[5])
    XOR_2bit(cnf,c[2][1],c[6][0],t[6])
    XOR_2bit(cnf,c[7][0],c[3][1],t[7])
    XOR_2bit(cnf,x[7],c[8][0],t[8])
    XOR_2bit(cnf,c[9][0],c[1][1],t[9])
    XOR_2bit(cnf,c[10][0],c[4][1],t[10])
    XOR_2bit(cnf,c[11][0],x[9],t[11])
    XOR_2bit(cnf,c[12][0],c[8][1],t[12])
    XOR_2bit(cnf,c[11][1],c[13][0],t[13])
    XOR_2bit(cnf,c[12][1],c[25][0],t[14])
    XOR_2bit(cnf,c[14][0],t[12],t[15])
    XOR_2bit(cnf,x[21],c[15][0],t[16])
    XOR_2bit(cnf,c[13][1],c[16][0],t[17])
    XOR_2bit(cnf,c[17][0],c[15][1],t[18])
    XOR_2bit(cnf,c[14][1],c[24][0],t[19])
    XOR_2bit(cnf,c[16][1],c[27][0],t[20])
    XOR_2bit(cnf,c[27][1],c[18][0],t[21])
    XOR_2bit(cnf,c[7][1],c[43][0],t[22])
    XOR_2bit(cnf,c[18][1],c[30][0],t[23])
    XOR_2bit(cnf,c[29][0],c[30][1],t[24])
    XOR_2bit(cnf,c[29][1],c[19][0],t[25])
    XOR_2bit(cnf,c[26][0],c[43][1],y_t[0])
    XOR_2bit(cnf,c[19][1],c[24][1],t[26])
    XOR_2bit(cnf,t[24],c[25][1],t[27])
    XOR_2bit(cnf,c[26][1],c[20][0],t[28])
    XOR_2bit(cnf,c[6][1],c[49][0],t[29])
    XOR_2bit(cnf,c[20][1],c[5][1],t[30])
    XOR_2bit(cnf,t[30],c[47][0],t[31])
    XOR_2bit(cnf,c[5][2],c[25][2],t[32])
    XOR_2bit(cnf,c[49][1],c[33][0],t[33])
    XOR_2bit(cnf,t[32],c[21][0],t[34])
    XOR_2bit(cnf,c[21][1],c[46][0],t[35])
    XOR_2bit(cnf,c[46][1],c[22][0],t[36])
    XOR_2bit(cnf,c[47][1],c[39][0],t[37])
    XOR_2bit(cnf,t[36],c[17][1],t[38])
    XOR_2bit(cnf,c[17][2],c[39][1],t[39])
    XOR_2bit(cnf,c[39][2],c[22][1],t[40])
    XOR_2bit(cnf,t[39],c[34][0],y[5])
    XOR_2bit(cnf,c[22][2],c[34][1],t[41])
    XOR_2bit(cnf,t[40],c[28][0],y_t[1])
    XOR_2bit(cnf,c[28][1],c[23][0],t[42])
    XOR_2bit(cnf,c[10][1],c[54][0],t[43])
    XOR_2bit(cnf,c[23][1],c[38][0],t[44])
    XOR_2bit(cnf,c[34][2],c[42][0],t[45])
    XOR_2bit(cnf,c[38][1],c[33][1],y_t[2])
    XOR_2bit(cnf,t[38],c[33][2],y_t[3])
    XOR_2bit(cnf,c[42][1],c[32][0],y[23])
    XOR_2bit(cnf,c[33][3],c[24][2],t[46])
    XOR_2bit(cnf,c[54][1],c[37][0],t[47])
    XOR_2bit(cnf,c[37][1],c[32][1],t[48])
    XOR_2bit(cnf,c[32][2],c[25][3],t[49])
    XOR_2bit(cnf,t[48],c[24][3],y[15])
    XOR_2bit(cnf,c[24][4],c[36][0],t[50])
    XOR_2bit(cnf,c[25][4],c[9][1],t[51])
    XOR_2bit(cnf,t[51],c[40][0],y_t[4])
    XOR_2bit(cnf,t[20],c[36][1],y_t[5])
    XOR_2bit(cnf,c[9][2],c[35][0],t[52])
    XOR_2bit(cnf,c[35][1],c[31][0],t[53])
    XOR_2bit(cnf,c[36][2],c[44][0],t[54])
    XOR_2bit(cnf,c[40][1],c[31][1],t[55])
    XOR_2bit(cnf,c[44][1],c[45][0],y[26])
    XOR_2bit(cnf,c[31][2],c[50][0],t[56])
    XOR_2bit(cnf,c[45][1],c[61][0],y[10])
    XOR_2bit(cnf,c[61][1],c[64][0],y[18])
    XOR_2bit(cnf,t[33],c[52][0],y_t[6])
    XOR_2bit(cnf,c[52][1],c[41][0],t[57])
    XOR_2bit(cnf,c[50][1],c[51][0],y[19])
    XOR_2bit(cnf,c[51][1],c[48][0],y[11])
    XOR_2bit(cnf,c[41][1],c[55][0],t[58])
    XOR_2bit(cnf,t[53],c[69][0],y_t[7])
    XOR_2bit(cnf,c[48][1],c[70][0],y[3])
    XOR_2bit(cnf,t[35],c[53][0],y[20])
    XOR_2bit(cnf,c[53][1],c[62][0],y[12])
    XOR_2bit(cnf,c[55][1],c[56][0],t[59])
    XOR_2bit(cnf,t[49],c[66][0],y_t[8])
    XOR_2bit(cnf,t[59],c[72][0],y[30])
    XOR_2bit(cnf,t[41],c[63][0],y[21])
    XOR_2bit(cnf,c[56][1],c[57][0],y[22])
    XOR_2bit(cnf,t[46],c[60][0],y[0])
    XOR_2bit(cnf,c[60][1],c[59][0],y[8])
    XOR_2bit(cnf,t[54],c[71][0],y_t[9])
    XOR_2bit(cnf,c[57][1],c[58][0],y[14])
    XOR_2bit(cnf,c[59][1],c[68][0],y[24])
    XOR_2bit(cnf,c[63][1],c[65][0],y[29])
    XOR_2bit(cnf,t[55],c[73][0],y[25])
    XOR_2bit(cnf,c[58][1],c[72][1],y[6])
    XOR_2bit(cnf,c[62][1],c[67][0],y[28])
    # print(c)
    # print(t)
    # print(y_t)
    return num



cnf = []
x = [_ for _ in range(64)]
y = [_ for _ in range(64)]
XOR_92(cnf,0,x,y)