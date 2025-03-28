import sys
sys.path.append('Kurahara_project')

from itertools import chain, product
import subprocess
import codecs

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

def xor_2bit(cnf,input1,input2,output):
    size=len(input1)
    if not len(input1) == len(input2) ==len(output):
        print("xor_2bit error")
        return
    for i in range(size):
        vars=[input1[i]]+[input2[i]]+[output[i]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",vars))

def xor_3bit(cnf,input1,input2,input3,output):
    size=len(input1)
    if not len(input1) == len(input2) == len(input3) == len(output):
        print("xor_3bit error")
        return
    for i in range(size):
        vars=[input1[i]]+[input2[i]]+[input3[i]]+[output[i]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_3bit_espresso.txt",vars))

def xor_4bit(cnf,input1,input2,input3,input4,output):
    size=len(input1)
    if not len(input1) == len(input2) == len(input3) == len(input4) == len(output):
        print("xor_4bit error")
        return
    for i in range(size):
        vars=[input1[i]]+[input2[i]]+[input3[i]]+[input4[i]]+[output[i]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_4bit_espresso.txt",vars))

def and_2bit(cnf,input1,input2,output,weight):
    size=len(input1)
    for i in range(size):
        vars=[input1[i]]+[input2[i]]+[output[i]]+[weight[i]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/and_2bit_weight_espresso.txt",vars))

def addition(cnf,In1,In2,Out,w):
    size = len(In1)
    vars=In1+In2+Out
    # print(vars)
    if not len(In1) == len(In2) ==len(Out):
        print("addition error")
        return
    for i in range(size-1):
        vars=[In1[i]]+[In2[i]]+[Out[i]]+[In1[i+1]]+[In2[i+1]]+[Out[i+1]]
        cnf+=(get_espresso_result_cnf("solver_func/espresso/addition_espresso.txt",vars))
        vars=[In1[i+1]]+[In2[i+1]]+[Out[i+1]]+[w[i]]
        cnf+=(get_espresso_result_cnf("solver_func/espresso/weight_espresso.txt",vars))
    cnf+=[[-In1[-1],-In2[-1],-Out[-1]]]
    cnf+=[[-In1[-1],In2[-1],Out[-1]]]
    cnf+=[[In1[-1],-In2[-1],Out[-1]]]
    cnf+=[[In1[-1],In2[-1],-Out[-1]]]
    # print(In2[-1],Out[-1])
    # vars+=w
    # print(vars)
    # cnf+=(get_espresso_result_cnf("solver_func/espresso/weight_32.txt",vars))

def addition_2bit(cnf,In1,In2,Out,w,size):
    for i in range(size-1):
        vars=[In1[i]]+[In2[i]]+[Out[i]]+[In1[i+1]]+[w[i]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/addition_2_espresso.txt",vars))
        vars=[In1[i+1]]+[In2[i+1]]+[Out[i+1]]+[w[i]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/weight_2_espresso.txt",vars))
    cnf.extend([[-In1[-1],-In2[-1],-Out[-1]]])
    cnf.extend([[-In1[-1],In2[-1],Out[-1]]])
    cnf.extend([[In1[-1],-In2[-1],Out[-1]]])
    cnf.extend([[In1[-1],In2[-1],-Out[-1]]])

def add_w(cnf,In1,In2,Out,w,size):
    for i in range(size-1):
        vars=[In1[i]]+[In2[i]]+[Out[i]]+[In1[i+1]]+[In2[i+1]]+[Out[i+1]]+[w[i]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/add_w_espresso.txt",vars))
    cnf.extend([[-In1[-1],-In2[-1],-Out[-1]]])
    cnf.extend([[-In1[-1],In2[-1],Out[-1]]])
    cnf.extend([[In1[-1],-In2[-1],Out[-1]]])
    cnf.extend([[In1[-1],In2[-1],-Out[-1]]])

def addition_flag(cnf,In1,In2,Out,w,flag):
    for i in range(len(In1)-1):
        vars=[In1[i+1]]+[In2[i+1]]+[Out[i+1]]+[flag[i]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/def_add_flag_espresso.txt",vars))
        vars=[In1[i]]+[In2[i]]+[Out[i]]+[flag[i]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/add_flag_espresso.txt",vars))
        vars=[In1[i+1]]+[In2[i+1]]+[Out[i+1]]+[w[i]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/weight_espresso.txt",vars))
    cnf.extend([[-In1[-1],-In2[-1],-Out[-1]]])
    cnf.extend([[-In1[-1],In2[-1],Out[-1]]])
    cnf.extend([[In1[-1],-In2[-1],Out[-1]]])
    cnf.extend([[In1[-1],In2[-1],-Out[-1]]])

def XOR92(cnf,shifted,xor_tmp,Sout):
    x = shifted
    t = xor_tmp
    y = Sout
    # print(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[16],x[24],t[0]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[16],x[24],t[0]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[8],x[24],t[1]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[3],x[11],t[2]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[10],x[18],t[3]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[14],x[22],t[4]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[12],x[28],t[5]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[3],x[27],t[6]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[2],x[18],t[7]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[7],x[31],t[8]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[0],x[8],t[9]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[6],x[14],t[10]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[1],x[9],t[11]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[23],x[31],t[12]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[1],x[17],t[13]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[23],t[1],t[14]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[15],t[12],t[15]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[21],x[29],t[16]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[17],x[25],t[17]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[13],x[29],t[18]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[15],t[0],t[19]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[25],t[3],t[20]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[3],x[26],t[21]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[2],t[21],t[22]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[26],t[6],t[23]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[5],t[6],t[24]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[5],x[20],t[25]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[2],t[21],y[2]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[20],t[0],t[26]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[24],t[1],t[27]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[2],x[19],t[28]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[27],t[28],t[29]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[19],x[28],t[30]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[30],t[26],t[31]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[28],t[1],t[32]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[28],t[9],t[33]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[32],x[4],t[34]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[4],t[25],t[35]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[25],x[5],t[36]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[26],t[16],t[37]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[36],x[13],t[38]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[13],t[16],t[39]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[16],x[5],t[40]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[39],t[10],y[5]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[5],t[10],t[41]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[40],t[4],y[13]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[4],x[30],t[42]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[6],t[42],t[43]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[30],t[15],t[44]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[10],t[19],t[45]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[15],t[9],y[7]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[38],t[9],y[4]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[19],t[8],y[23]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[9],t[0],t[46]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[42],t[14],t[47]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[14],t[8],t[48]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[8],t[1],t[49]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[48],t[0],y[15]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[0],t[13],t[50]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[1],x[0],t[51]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[51],t[17],y[16]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[20],t[13],y[9]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[0],t[11],t[52]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[11],t[7],t[53]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[13],t[22],t[54]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[17],t[7],t[55]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[22],t[23],y[26]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[7],t[29],t[56]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[23],t[56],y[10]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[56],y[2],y[18]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[33],t[34],y[27]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[34],t[18],t[57]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[29],t[31],y[19]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[31],t[27],y[11]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[18],t[43],t[58]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[53],y[9],y[1]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[27],y[27],y[3]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[35],t[37],y[20]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[37],t[57],y[12]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[43],t[44],t[59]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[49],y[7],y[31]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[59],y[31],y[30]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[41],t[58],y[21]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[44],t[45],y[22]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[46],t[52],y[0]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[52],t[50],y[8]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[54],y[1],y[17]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[45],t[47],y[14]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[50],y[16],y[24]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[58],y[13],y[29]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[55],y[17],y[25]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[47],y[31],y[6]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[57],y[4],y[28]]))

def XOR92_num(cnf,num,shifted,out):
    x = shifted
    y = out
    t = [_ for _ in range(num, num+60)]
    num+=60
    # print(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[16],x[24],t[0]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[16],x[24],t[0]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[8],x[24],t[1]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[3],x[11],t[2]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[10],x[18],t[3]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[14],x[22],t[4]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[12],x[28],t[5]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[3],x[27],t[6]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[2],x[18],t[7]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[7],x[31],t[8]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[0],x[8],t[9]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[6],x[14],t[10]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[1],x[9],t[11]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[23],x[31],t[12]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[1],x[17],t[13]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[23],t[1],t[14]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[15],t[12],t[15]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[21],x[29],t[16]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[17],x[25],t[17]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[13],x[29],t[18]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[15],t[0],t[19]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[25],t[3],t[20]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[3],x[26],t[21]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[2],t[21],t[22]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[26],t[6],t[23]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[5],t[6],t[24]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[5],x[20],t[25]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[2],t[21],y[2]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[20],t[0],t[26]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[24],t[1],t[27]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[2],x[19],t[28]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[27],t[28],t[29]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[19],x[28],t[30]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[30],t[26],t[31]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[28],t[1],t[32]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[28],t[9],t[33]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[32],x[4],t[34]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[4],t[25],t[35]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[25],x[5],t[36]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[26],t[16],t[37]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[36],x[13],t[38]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[13],t[16],t[39]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[16],x[5],t[40]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[39],t[10],y[5]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[5],t[10],t[41]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[40],t[4],y[13]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[4],x[30],t[42]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[6],t[42],t[43]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[30],t[15],t[44]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[10],t[19],t[45]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[15],t[9],y[7]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[38],t[9],y[4]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[19],t[8],y[23]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[9],t[0],t[46]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[42],t[14],t[47]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[14],t[8],t[48]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[8],t[1],t[49]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[48],t[0],y[15]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[0],t[13],t[50]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[1],x[0],t[51]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[51],t[17],y[16]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[20],t[13],y[9]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[x[0],t[11],t[52]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[11],t[7],t[53]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[13],t[22],t[54]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[17],t[7],t[55]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[22],t[23],y[26]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[7],t[29],t[56]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[23],t[56],y[10]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[56],y[2],y[18]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[33],t[34],y[27]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[34],t[18],t[57]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[29],t[31],y[19]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[31],t[27],y[11]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[18],t[43],t[58]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[53],y[9],y[1]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[27],y[27],y[3]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[35],t[37],y[20]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[37],t[57],y[12]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[43],t[44],t[59]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[49],y[7],y[31]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[59],y[31],y[30]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[41],t[58],y[21]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[44],t[45],y[22]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[46],t[52],y[0]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[52],t[50],y[8]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[54],y[1],y[17]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[45],t[47],y[14]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[50],y[16],y[24]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[58],y[13],y[29]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[55],y[17],y[25]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[47],y[31],y[6]]))
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",[t[57],y[4],y[28]]))
    return num 

def func_alpha_0(cnf,Input,Output):
    vars=Input+Output[:8]
    cnf+=(get_espresso_result_cnf("Kurahara_project/solver_func/espresso_K2_3g/alpha_0_0_espresso.txt",vars))
    vars=Input+Output[8:16]
    cnf+=(get_espresso_result_cnf("Kurahara_project/solver_func/espresso_K2_3g/alpha_0_1_espresso.txt",vars))
    vars=Input+Output[16:24]
    cnf+=(get_espresso_result_cnf("Kurahara_project/solver_func/espresso_K2_3g/alpha_0_2_espresso.txt",vars))
    vars=Input+Output[24:]
    cnf+=(get_espresso_result_cnf("Kurahara_project/solver_func/espresso_K2_3g/alpha_0_3_espresso.txt",vars))

def func_alpha_12(cnf,Input,Output,flag):
    vars=Input+Output[:8]+[flag]
    cnf+=(get_espresso_result_cnf("Kurahara_project/solver_func/espresso_K2_3g/alpha_12_0_espresso.txt",vars))
    vars=Input+Output[8:16]+[flag]
    cnf+=(get_espresso_result_cnf("Kurahara_project/solver_func/espresso_K2_3g/alpha_12_1_espresso.txt",vars))
    vars=Input+Output[16:24]+[flag]
    cnf+=(get_espresso_result_cnf("Kurahara_project/solver_func/espresso_K2_3g/alpha_12_2_espresso.txt",vars))
    vars=Input+Output[24:]+[flag]
    cnf+=(get_espresso_result_cnf("Kurahara_project/solver_func/espresso_K2_3g/alpha_12_3_espresso.txt",vars))

def func_alpha_3(cnf,Input,Output,flag):
    vars=Input+Output[:8]+[flag]
    cnf+=(get_espresso_result_cnf("Kurahara_project/solver_func/espresso_K2_3g/alpha_3_0_espresso.txt",vars))
    vars=Input+Output[8:16]+[flag]
    cnf+=(get_espresso_result_cnf("Kurahara_project/solver_func/espresso_K2_3g/alpha_3_1_espresso.txt",vars))
    vars=Input+Output[16:24]+[flag]
    cnf+=(get_espresso_result_cnf("Kurahara_project/solver_func/espresso_K2_3g/alpha_3_2_espresso.txt",vars))
    vars=Input+Output[24:]+[flag]
    cnf+=(get_espresso_result_cnf("Kurahara_project/solver_func/espresso_K2_3g/alpha_3_3_espresso.txt",vars))

    # vars=[A[n-1][:8]+alpha_0[n]]
    # cnf+=(get_espresso_result_cnf("solver_func/espresso/K2_alpha/alpha_0_espresso.txt",vars))
    # vars=[[A[n-1][65]]+B[n-1][:8]+alpha_12[n]]
    # cnf+=(get_espresso_result_cnf("solver_func/espresso/K2_alpha/alpha_12_espresso.txt",vars))
    # vars=[[A[n-1][64]]+B[n-1][32*7:32*7+8]+alpha_3[n]]
    # cnf+=(get_espresso_result_cnf("solver_func/espresso/K2_alpha/alpha_3_espresso.txt",vars))

def func_alpha3g(cnf,Input,Output):
    vars=Input+Output[:8]
    cnf+=(get_espresso_result_cnf("solver_func/espresso_K2_3g/alpha_3g_0_espresso.txt",vars))
    vars=Input+Output[8:16]
    cnf+=(get_espresso_result_cnf("solver_func/espresso_K2_3g/alpha_3g_1_espresso.txt",vars))
    vars=Input+Output[16:24]
    cnf+=(get_espresso_result_cnf("solver_func/espresso_K2_3g/alpha_3g_2_espresso.txt",vars))
    vars=Input+Output[24:]
    cnf+=(get_espresso_result_cnf("solver_func/espresso_K2_3g/alpha_3g_3_espresso.txt",vars))

def func_alpha3g(cnf,Input,Output):
    vars=Input+Output[:8]
    cnf+=(get_espresso_result_cnf("solver_func/espresso_K2_3g/alpha_3g_0_espresso.txt",vars))
    vars=Input+Output[8:16]
    cnf+=(get_espresso_result_cnf("solver_func/espresso_K2_3g/alpha_3g_1_espresso.txt",vars))
    vars=Input+Output[16:24]
    cnf+=(get_espresso_result_cnf("solver_func/espresso_K2_3g/alpha_3g_2_espresso.txt",vars))
    vars=Input+Output[24:]
    cnf+=(get_espresso_result_cnf("solver_func/espresso_K2_3g/alpha_3g_3_espresso.txt",vars))

def func_alpha3g_inv(cnf,Input,Output):
    vars=Input+Output[:8]
    cnf+=(get_espresso_result_cnf("solver_func/espresso_K2_3g/alpha_3g_inv_0_espresso.txt",vars))
    vars=Input+Output[8:16]
    cnf+=(get_espresso_result_cnf("solver_func/espresso_K2_3g/alpha_3g_inv_1_espresso.txt",vars))
    vars=Input+Output[16:24]
    cnf+=(get_espresso_result_cnf("solver_func/espresso_K2_3g/alpha_3g_inv_2_espresso.txt",vars))
    vars=Input+Output[24:]
    cnf+=(get_espresso_result_cnf("solver_func/espresso_K2_3g/alpha_3g_inv_3_espresso.txt",vars))

def comp_7to3(cnf,prob,num):
    prob_2bit=[[],[],[]]
    pad=len(prob)%7
    for i in range(7-pad):
        prob.extend([1])
    for i in range(((len(prob)//7))):
        for b in range(3):
            prob_2bit[b].extend([num])
            num+=1
        # print(prob_2bit)
        vars=prob[7*i:7*(i+1)]+[prob_2bit[2][-1]]+[prob_2bit[1][-1]]+[prob_2bit[0][-1]]
        # print(vars)
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/comp_7to3_espresso.txt",vars))
    return prob_2bit,num,prob

def carry_bit(cnf,prob_2bit,num):
    #0bit
    xor_temp=[[],[]]
    # print(prob_2bit[2][-1])
    # print(num)
    bit_len=len(prob_2bit[0])
    xor_temp[0].extend([i for i in range(num,num+bit_len-1)])
    # print(len(xor_temp[0]))
    num+=bit_len-1
    prob_2bit[1].extend([i for i in range(num,num+bit_len-1)])
    num+=bit_len-1
    vars=[prob_2bit[0][0]]+[prob_2bit[0][1]]+[xor_temp[0][0]]
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",vars))
    vars=[prob_2bit[0][0]]+[prob_2bit[0][1]]+[prob_2bit[1][bit_len]]
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/and_2bit(sat)_espresso.txt",vars))
    for i in range(bit_len-2):
        vars=[prob_2bit[0][i+2]]+[xor_temp[0][i]]+[xor_temp[0][i+1]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",vars))
        vars=[prob_2bit[0][i+2]]+[xor_temp[0][i]]+[prob_2bit[1][bit_len+1+i]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/and_2bit(sat)_espresso.txt",vars))
    #1bit
    bit_len1=len(prob_2bit[1])
    xor_temp[1].extend([i for i in range(num,num+bit_len1-1)])
    num+=bit_len1-1
    prob_2bit[2].extend([i for i in range(num,num+bit_len1-1)])
    num+=bit_len1-1
    vars=[prob_2bit[1][0]]+[prob_2bit[1][1]]+[xor_temp[1][0]]
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",vars))
    vars=[prob_2bit[1][0]]+[prob_2bit[1][1]]+[prob_2bit[2][bit_len]]
    cnf.extend(get_espresso_result_cnf("solver_func/espresso/and_2bit(sat)_espresso.txt",vars))
    for i in range(bit_len1-2):
        vars=[prob_2bit[1][i+2]]+[xor_temp[1][i]]+[xor_temp[1][i+1]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/xor_2bit_espresso.txt",vars))
        # print([xor_temp[1][i]])
        vars=[prob_2bit[1][i+2]]+[xor_temp[1][i]]+[prob_2bit[2][bit_len+1+i]]
        cnf.extend(get_espresso_result_cnf("solver_func/espresso/and_2bit(sat)_espresso.txt",vars))
    return prob_2bit,xor_temp,num


