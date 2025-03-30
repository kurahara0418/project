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

def XOR3(cnf,Input1,Input2,Input3,Output,p):
    size=len(Input1)
    if size!= len(Input2) or size!= len(Input3) or size!= len(Output) or size!= len(p):
        print("XOR3 error")
    for i in range(size):
        vars=Input1[i]+Input2[i]+Input3[i]+Output[i]+[p[i]]
        cnf.extend(get_espresso_result_cnf("kurahara/solver_func/espresso/signed/XOR_3_espresso.txt",vars))

def XOR4(cnf,Input1,Input2,Input3,Input4,Output,p):
    size=len(Input1)
    if size!= len(Input2) or size!= len(Input3) or size!= len(Input4) or size!= len(Output) or size!= len(p):
        print("XOR4 error")
    for i in range(size):
        vars=Input1[i]+Input2[i]+Input3[i]+Input4[i]+Output[i]+[p[i]]
        cnf.extend(get_espresso_result_cnf("kurahara/solver_func/espresso/signed/XOR_4_espresso.txt",vars))

def F_addition(cnf,num,x,y,z,p):
    size=len(x)
    if size!= len(y) or size!= len(z) or size!= len(p):
        print("F_add_c error")
        return
    #table3
    c = [[1,1]]
    c_temp = [[num+(i*2),num+(i*2)+1]for i in range(size)]
    num+=size*2
    c=c_temp+c
    temp_z = [[num+(i*2),num+(i*2)+1]for i in range(size)]
    num+=size*2
    for bit in range(size):
        vars=x[bit]+y[bit]+c[bit+1]+temp_z[bit]+c[bit]
        cnf.extend(get_espresso_result_cnf("kurahara/solver_func/espresso/signed/F_add_c_espresso.txt",vars))
    #table4
    c = [[1,1]]
    c_temp = [[num+(i*2),num+(i*2)+1]for i in range(size)]
    num+=size*2
    c=c_temp+c
    for bit in range(size-1):
        vars=temp_z[bit]+c[bit+1]+z[bit]+c[bit]+[p[bit]]
        cnf.extend(get_espresso_result_cnf("kurahara/solver_func/espresso/signed/F_add_z_espresso.txt",vars))
    cnf.append([-p[size-1]])
    vars = c[size-1] + c[size]
    cnf.extend(get_espresso_result_cnf("kurahara/solver_func/espresso/signed/equal_espresso.txt",vars))
    vars = z[size-1] + temp_z[size-1]
    cnf.extend(get_espresso_result_cnf("kurahara/solver_func/espresso/signed/equal_espresso.txt",vars))
    # print(vars)
    return num

def addition_mod(cnf,num,x,y,z):
    size=len(x)
    if size!= len(y) or size!= len(z):
        print("add_mod error")
        return 
    c = [[1,1]]
    c_temp = [[num+(i*2),num+(i*2)+1]for i in range(size)]
    num+=size*2
    c=c_temp+c
    temp_z = [[num+(i*2),num+(i*2)+1]for i in range(size)]
    num+=size*2
    for bit in range(size):
        vars=x[bit]+y[bit]+c[bit+1]+temp_z[bit]+c[bit]
        cnf.extend(get_espresso_result_cnf("kurahara/solver_func/espresso/signed/F_add_c_espresso.txt",vars))
    return num 

def addition_exp(cnf,num,temp_z,z,p):
    size=len(temp_z)
    if size!= len(z) or size!= len(p):
        print("add_exp error")
        return
    c = [[1,1]]
    c_temp = [[num+(i*2),num+(i*2)+1]for i in range(size)]
    num+=size*2
    c=c_temp+c
    for bit in range(size-1):
        vars=temp_z[bit]+c[bit+1]+z[bit]+c[bit]+[p[bit]]
        cnf.extend(get_espresso_result_cnf("kurahara/solver_func/espresso/signed/F_add_z_espresso.txt",vars))
    cnf.append([-p[size-1]])
    vars = c[size-1] + c[size]
    cnf.extend(get_espresso_result_cnf("kurahara/solver_func/espresso/signed/equal_espresso.txt",vars))
    vars = z[size-1] + temp_z[size-1]
    cnf.extend(get_espresso_result_cnf("kurahara/solver_func/espresso/signed/equal_espresso.txt",vars))
    # print(vars)
    return num

def Ch(cnf,Input1,Input2,Input3,Output,p):
    size=len(Input1)
    if size!= len(Input2) or size!= len(Input3) or size!= len(Output) or size!= len(p):
        print("Ch error")
        return
    for i in range(size):
        vars=Input1[i]+Input2[i]+Input3[i]+Output[i]+p[i]
        cnf.extend(get_espresso_result_cnf("kurahara/solver_func/espresso/signed/Ch_espresso.txt",vars))
    
def Maj(cnf,Input1,Input2,Input3,Output,p):
    size=len(Input1)
    if size!= len(Input2) or size!= len(Input3) or size!= len(Output) or size!= len(p):
        print("Ch error")
        return
    for i in range(size):
        vars=Input1[i]+Input2[i]+Input3[i]+Output[i]+[p[i]]
        cnf.extend(get_espresso_result_cnf("kurahara/solver_func/espresso/signed/Maj_espresso.txt",vars))

cnf=[]
num=5
Input1=[[1,2],[3,4]]
Input2=[[1,2],[3,4]]
Input3=[[1,2],[3,4]]
Output=[[1,2],[3,4]]
p=[1,2]
# p=[[1,2],[3,4]]

# XOR3(cnf,Input1,Input2,Input3,Output,p)
# F_addition(cnf,num,Input1,Input2,Output,p)
# Ch(cnf,Input1,Input2,Input3,Output,p)
# Maj(cnf,Input1,Input2,Input3,Output,p)