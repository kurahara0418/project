import sys
sys.path.append('/Users/kurahararikuto/Documents/Kurahara_project/kurahara')

from pysat.card import *
from pysat.formula import CNF
from solver_func.signed_cnf import *
import itertools 
import time
import solver_func.solver
import solver_func.extract_solution
import solver_func.update_logfile
BIT=32

def shift(A,rot_num):
    temp_A = A[rot_num:]+A[:rot_num]
    return temp_A

def func(cnf,n,A,F,F_p):
    if n<20:
        Ch(cnf,A[n+3],A[n+2],A[n+1],F[n],F_p[n])
    elif n<40:
        XOR3(cnf,A[n+3],A[n+2],A[n+1],F[n],F_p[n])
    elif n<60:
        Maj(cnf,A[n+3],A[n+2],A[n+1],F[n],F_p[n])
    elif n<80:
        XOR3(cnf,A[n+3],A[n+2],A[n+1],F[n],F_p[n])
def fix_path(cnf,state,path):
    for i in range(len(path)):
        if path[i]=="-":
            cnf.append([-state[i][0]])
            cnf.append([-state[i][1]])
        elif path[i]=="u":
            cnf.append([state[i][0]])
            cnf.append([state[i][1]])        
        elif path[i]=="n":
            cnf.append([-state[i][0]])
            cnf.append([state[i][1]]) 
        else:
            print("error")         
def input_path(cnf,M):
    path="--------------------------------"
    for i in range(13):
        fix_path(cnf,M[i],path)
    # fix_path(cnf,M[7],path)
    # path="nuuuuuuuuuuuuuuuuuuuuuuuuuuuuuun"
    # fix_path(cnf,M[13],path)
    # path="unnnnnnnnnnnnnnnnnnnnnnnnnuunnnn"
    # fix_path(cnf,M[14],path)
    # path="nuuuuuuuuuuuuuuuuuuuuuuuuuunuunu"
    # fix_path(cnf,M[15],path)
def signed_SHA(round,weight,upper,up):
    start = time.perf_counter()
    total = time.perf_counter() 
    while weight < upper:
        cnfpath = "kurahara/projects/SHA_signed/cnf_file/R{}_DCP{}.cnf".format(round,weight)
        logpath = "kurahara/projects/SHA_signed/log_file/R{}_DCP{}.txt".format(round,weight) 
        cnf = []
        num = 2
        if round<16:
            M=[[[num+(i*2)+(BIT*2*j),num+1+(i*2)+(BIT*2*j)]for i in range(BIT)]for j in range(round)]
            num+=BIT*2*round
        else:
            M=[[[num+(i*2)+(BIT*2*j),num+1+(i*2)+(BIT*2*j)]for i in range(BIT)]for j in range(16)]
            num+=BIT*2*16
        A=[[[num+(i*2)+(BIT*2*n),num+1+(i*2)+(BIT*2*n)]for i in range(BIT)]for n in range(round)]
        num+=BIT*2*round
        F=[[[num+(i*2)+(BIT*2*n),num+1+(i*2)+(BIT*2*n)]for i in range(BIT)]for n in range(round)]
        num+=BIT*2*round
        add=[[[[num+(i*2)+(BIT*2*j)+(BIT*2*3*n),num+1+(i*2)+(BIT*2*j)+(BIT*2*3*n)]for i in range(BIT)]for j in range(3)]for n in range(round)]
        num+=BIT*2*3*round
        CV=[[[1,1] for _ in range(BIT)]for _ in range(5)]
        A_p=[[[_ for _ in range(num+(i*BIT)+(BIT*4*n),num+((i+1)*BIT)+(BIT*4*n))]for i in range(4)]for n in range(round+1)]
        num+=BIT*4*round
        CV_p=[[_ for _ in range(num+(i*BIT),num+((i+1)*BIT))]for i in range(5)]
        num+=BIT*5
        W = M[:round]
        A_init=[[[1,1] for _ in range(BIT)]for _ in range(5)]
        A=A_init+A
        K = [[1,1] for _ in range(BIT)]
        if round>16:
            temp_round=round-16
            temp_W=[[[num+(i*2)+(BIT*2*n),num+1+(i*2)+(BIT*2*n)]for i in range(BIT)]for n in range(temp_round)]
            # temp_W=shift(temp_W,1)
            num+=BIT*2*temp_round
            W+=temp_W
            W_p=[[_ for _ in range(num+(BIT*n),num+(BIT*n)+BIT)]for n in range(temp_round)]
            num+=BIT*temp_round
        if round<20:
            F_p=[[[num+(i*2)+(BIT*2*n),num+1+(i*2)+(BIT*2*n)]for i in range(BIT)]for n in range(round)]
            num+=BIT*2*round
        else:
            F_p=[[[num+(i*2)+(BIT*2*n),num+1+(i*2)+(BIT*2*n)]for i in range(BIT)]for n in range(20)]
            num+=BIT*2*20
            temp_round=round-20
            XOR_p=[[_ for _ in range(num+(BIT*n),num+(BIT*n)+BIT)]for n in range(temp_round)]
            num+=BIT*round
            F_p+=XOR_p
        cnf.append([-1])
        M_ = list(itertools.chain.from_iterable(itertools.chain.from_iterable(M)))
        cnf.append(M_)
        # input_path(cnf,M)
        for n in range(round):
            if 15<n:
                XOR4(cnf,W[n-3],W[n-8],W[n-14],W[n-16],W[n],W_p[n-16])
                W[n]=shift(W[n],1)
            func(cnf,n,A,F,F_p)
            temp_A = shift(A[n+4],5)
            num = F_addition(cnf,num,temp_A,A[n],add[n][0],A_p[n][0])
            num = F_addition(cnf,num,add[n][0],K,add[n][1],A_p[n][1])
            num = F_addition(cnf,num,add[n][1],F[n],add[n][2],A_p[n][2])
            num = F_addition(cnf,num,add[n][2],W[n],A[n+5],A_p[n][3])
            # num = F_addition(cnf,num,temp_A,A[n],add[n][0],A_p[n][0])
            # num = F_addition(cnf,num,add[n][0],W[n],add[n][1],A_p[n][1])
            # num = F_addition(cnf,num,add[n][1],K,add[n][2],A_p[n][2])
            # num = F_addition(cnf,num,add[n][2],F[n],A[n+5],A_p[n][3])
            A[n+3]=shift(A[n+3],30)
        for i in range(5):
            num = F_addition(cnf,num,A[round+i],A[i],CV[i],CV_p[i])
        SHA_cnf = CNF(from_clauses = cnf)
        prob=[]
        for p in CV_p:
            prob.extend(p)
        for n in range(round):
            for p in A_p[n]:
                prob.extend(p)
        if round>16:
            for p in W_p:
                prob.extend(p)
        if round>20:
            for p in F_p[:20]:
                prob.extend(list(itertools.chain.from_iterable(p)))
            for p in F_p[20:]:
                prob.extend(p)
        else:
            for p in F_p:
                prob.extend(list(itertools.chain.from_iterable(p)))

        encode = CardEnc.atmost(lits = prob,bound = weight,top_id = SHA_cnf.nv,encoding = 6)
        cnf.extend(encode)
        SHA_cnf = CNF(from_clauses = cnf)
        SHA_cnf.to_file(cnfpath)
        s = solver_func.solver.Solver(cnfpath,logpath)
        s.kissat_sc2024()
        result = s.CheckResult()

        if result == True:
            solution = solver_func.extract_solution.Extract_Solution(logpath)
            with open(logpath,"w") as f:
                for i in range(5):
                    solver_func.update_logfile.Update_LogFile_signed_s(f,solution,A[i],32,"A[{}]".format(i),8)
                f.write("==============================================================================================\n")
                for n in range(round):
                    f.write("round {}\n".format(n))
                    for i in range(1,6):
                        if i<3:
                            temp_A=shift(A[n+5-i],2)
                        else:
                            temp_A=A[n+5-i]
                        solver_func.update_logfile.Update_LogFile_signed_s(f,solution,temp_A,32,"A[{}]".format(n-i),8)
                    temp_A=shift(A[n+4],7)
                    solver_func.update_logfile.Update_LogFile_signed_s(f,solution,temp_A,32,"A[{}]<<5".format(n-1),8)
                    solver_func.update_logfile.Update_LogFile_signed_s(f,solution,W[n],32,"W[{}]".format(n),8)
                    solver_func.update_logfile.Update_LogFile_signed_s(f,solution,F[n],32,"F[{}]".format(n),8)
                    for i in range(3):
                        solver_func.update_logfile.Update_LogFile_signed_s(f,solution,add[n][i],32,"add[{}][{}]".format(n,i),8)
                    temp_A=shift(A[n+5],2)
                    solver_func.update_logfile.Update_LogFile_signed_s(f,solution,temp_A,32,"A[{}]".format(n),8)
                    # solver_func.update_logfile.Update_LogFile_signed_s(f,solution,A[n+5],32,"A[{}]".format(n),8)
                    for i in range(4):
                        solver_func.update_logfile.Update_LogFile_single(f,solution,A_p[n][i],32,"A_p[{}][{}]".format(n,i),8)
                    F_p[n]=list(itertools.chain.from_iterable(F_p[n]))
                    solver_func.update_logfile.Update_LogFile_single(f,solution,F_p[n],64,"F_p[{}]".format(n),8)
                    f.write("==============================================================================================\n")
                for i in range(5):
                    solver_func.update_logfile.Update_LogFile_signed_s(f,solution,A[round+i],32,"A[{}]".format(round+i-5),8)
                    solver_func.update_logfile.Update_LogFile_signed_s(f,solution,A[i],32,"A[{}]".format(i-5),8)
                    solver_func.update_logfile.Update_LogFile_signed_s(f,solution,CV[i],32,"CV[{}]".format(i),8)
        if result == True:
            end = time.perf_counter()
            print("Round%d , weight %d : SAT   | elapsed_time = %lf[s]  total_time = %lf[s]"%(round,weight,(end-start),(end-total)),flush = True)
            start = time.perf_counter()
            weight += up
            if up>0:
                break
        else:
            end = time.perf_counter()
            print("Round%d , weight %d : UNSAT | elapsed_time = %lf[s]  total_time = %lf[s]"%(round,weight,(end-start),(end-total)),flush = True)
            start = time.perf_counter()
            weight += up
            if up<0:
                break

round = 16
weight = 0
upper = 50
up = 1
signed_SHA(round,weight,upper,up)
# for round in range(16):
#     signed_SHA(round,weight,upper,up)

