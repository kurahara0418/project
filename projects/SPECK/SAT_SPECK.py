import sys
sys.path.append('/Users/kurahararikuto/Documents/python')

from pysat.card import *
from pysat.formula import CNF
from solver_func.append_cnf import get_espresso_result_cnf,addition
from itertools import chain
import time
import solver_func.solver
import solver_func.extract_solution
import solver_func.update_logfile

def SPECK32_DCP(max_round,weight,upper,up,matsui):
    if matsui:
        dcp=[0,1,3,5,9,13,18,24,30,34,38,42,45,49,54,58,63,69,74,77,81,85]
        print("matsui")
    start = time.perf_counter()
    total = time.perf_counter()
    while weight<upper:
        cnfpath="Kurahara_project/projects/SPECK/cnffile/SPECK_32_cnf/32_R%d_DCP%d.cnf"%(max_round,weight)
        logpath="Kurahara_project/projects/SPECK/logfile/SPECK_32_log/R%d_DCP%d.txt"%(max_round,weight)
        num=1
        PT1=[]
        PT2=[]
        PT1_shifted=[]
        PT2_shifted=[]
        w=[]
        cnf=[]
        for round in range(max_round):
            PT1.append([i for i in range(num,num+16)])
            num+=16
            PT2.append([i for i in range(num,num+16)])
            num+=16
            w.append([i for i in range(num,num+15)])
            num+=15
            PT1_shifted.append(PT1[round][9:]+PT1[round][:9])
            PT2_shifted.append(PT2[round][2:]+PT2[round][:2])
        PT1.append([i for i in range(num,num+16)])
        num+=16
        PT2.append([i for i in range(num,num+16)])
        num+=16

        cnf.extend([PT1[0]+PT2[0]])
        for round in range(max_round):
            addition(cnf,PT1_shifted[round],PT2[round],PT1[round+1],w[round])
            for i in range(16):
                vars=[PT1[round+1][i]]+[PT2_shifted[round][i]]+[PT2[round+1][i]]
                cnf.extend(get_espresso_result_cnf("snow/espresso/xor_2bit_espresso.txt",vars))
        SPECK32_cnf = CNF(from_clauses = cnf)
        if matsui:
            for n in range(max_round-2,-1,-1):
                SPECK32_cnf = CNF(from_clauses = cnf)
                prob=[]
                for round in range(n+1,max_round):
                    prob.extend(w[round])
                rw=weight-dcp[n]
                encode=CardEnc.atmost(lits = prob,bound = rw,top_id = SPECK32_cnf.nv,encoding = 6)
                cnf.extend(encode)
        prob=[]
        SPECK32_cnf = CNF(from_clauses = cnf)
        for round in range(max_round):
            prob.extend(w[round])
        encode = CardEnc.atmost(lits = prob,bound = weight,top_id = SPECK32_cnf.nv,encoding = 6)
        cnf.extend(encode)
        # print(list(encode))
        SPECK32_cnf = CNF(from_clauses = cnf)
        SPECK32_cnf.to_file(cnfpath)
        s = solver_func.solver.Solver(cnfpath,logpath)
        s.kissat_MAB_HyWalk()
        result = s.CheckResult()
        if result == True:
            solution = solver_func.extract_solution.Extract_Solution(logpath)
            with open(logpath,"w") as f:
                for r in range(max_round):
                    solver_func.update_logfile.Update_LogFile(f,solution,PT1,r,16,"PT1",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT2,r,16,"PT2",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT1_shifted,r,16,"PT1_shift",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT2_shifted,r,16,"PT2_shift",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,w,r,15,"w",15)
                    f.write("==============================================================================================\n")
                solver_func.update_logfile.Update_LogFile(f,solution,PT1,r,16,"PT1",4)
                solver_func.update_logfile.Update_LogFile(f,solution,PT2,r,16,"PT2",4)
        if result == True:
            end = time.perf_counter()
            print("Round%d , weight %d : SAT   | elapsed_time = %lf[s]  total_time = %lf[s]"%(max_round,weight,(end-start),(end-total)),flush = True)
            start = time.perf_counter()
            weight += up
            break
        else:
            end = time.perf_counter()
            print("Round%d , weight %d : UNSAT | elapsed_time = %lf[s]  total_time = %lf[s]"%(max_round,weight,(end-start),(end-total)),flush = True)
            start = time.perf_counter()
            weight += up

def SPECK48_DCP(max_round,weight,upper,up,matsui):
    if matsui:
        dcp=[0,1,3,6,10,14,19,26,33,40,45,49,54,58,63,68,75,82]
        print("matsui")
    start = time.perf_counter()
    total = time.perf_counter()
    while weight<upper:
        cnfpath="Kurahara_project/projects/SPECK/cnffile/SPECK_48_cnf/48_R%d_DCP%d.cnf"%(max_round,weight)
        logpath="Kurahara_project/projects/SPECK/logfile/SPECK_48_log/R%d_DCP%d.txt"%(max_round,weight)
        if matsui:
            cnfpath="Kurahara_project/projects/SPECK/cnffile/SPECK_48_cnf/ma_48_R%d_DCP%d.cnf"%(max_round,weight)
            logpath="Kurahara_project/projects/SPECK/logfile/SPECK_48_log/ma_R%d_DCP%d.txt"%(max_round,weight)
        num=1
        PT1=[]
        PT2=[]
        PT1_shifted=[]
        PT2_shifted=[]
        w=[]
        cnf=[]
        for round in range(max_round):
            PT1.append([i for i in range(num,num+24)])
            num+=24
            PT2.append([i for i in range(num,num+24)])
            num+=24
            w.append([i for i in range(num,num+23)])
            num+=23
            PT1_shifted.append(PT1[round][16:]+PT1[round][:16])
            PT2_shifted.append(PT2[round][3:]+PT2[round][:3])
        PT1.append([i for i in range(num,num+24)])
        num+=24
        PT2.append([i for i in range(num,num+24)])
        num+=24

        cnf.extend([PT1[0]+PT2[0]])
        for round in range(max_round):
            addition(cnf,PT1_shifted[round],PT2[round],PT1[round+1],w[round])
            for i in range(24):
                vars=[PT1[round+1][i]]+[PT2_shifted[round][i]]+[PT2[round+1][i]]
                cnf.extend(get_espresso_result_cnf("snow/espresso/xor_2bit_espresso.txt",vars))
        SPECK32_cnf = CNF(from_clauses = cnf)
        if matsui:
            for n in range(max_round-2,-1,-1):
                SPECK32_cnf = CNF(from_clauses = cnf)
                prob=[]
                for round in range(n+1,max_round):
                    prob.extend(w[round])
                rw=weight-dcp[n]
                encode=CardEnc.atmost(lits = prob,bound = rw,top_id = SPECK32_cnf.nv,encoding = 6)
                cnf.extend(encode)
        prob=[]
        SPECK32_cnf = CNF(from_clauses = cnf)
        for round in range(max_round):
            prob.extend(w[round])
        encode = CardEnc.atmost(lits = prob,bound = weight,top_id = SPECK32_cnf.nv,encoding = 6)
        cnf.extend(encode)
        SPECK32_cnf = CNF(from_clauses = cnf)
        SPECK32_cnf.to_file(cnfpath)
        s = solver_func.solver.Solver(cnfpath,logpath)
        s.kissat_MAB_HyWalk()
        result = s.CheckResult()
        if result == True:
            solution = solver_func.extract_solution.Extract_Solution(logpath)
            with open(logpath,"w") as f:
                for r in range(max_round):
                    solver_func.update_logfile.Update_LogFile(f,solution,PT1,r,24,"PT1",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT2,r,24,"PT2",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT1_shifted,r,24,"PT1_shift",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT2_shifted,r,24,"PT2_shift",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,w,r,15,"w",15)
                    f.write("==============================================================================================\n")
                solver_func.update_logfile.Update_LogFile(f,solution,PT1,r,24,"PT1",4)
                solver_func.update_logfile.Update_LogFile(f,solution,PT2,r,24,"PT2",4)
        if result == True:
            end = time.perf_counter()
            print("Round%d , weight %d : SAT   | elapsed_time = %lf[s]  total_time = %lf[s]"%(max_round,weight,(end-start),(end-total)),flush = True)
            start = time.perf_counter()
            weight += up
            break
        else:
            end = time.perf_counter()
            print("Round%d , weight %d : UNSAT | elapsed_time = %lf[s]  total_time = %lf[s]"%(max_round,weight,(end-start),(end-total)),flush = True)
            start = time.perf_counter()
            weight += up

def SPECK64_DCP(max_round,weight,upper,up,matsui):
    if matsui:
        dcp=[0,1,3,6,10,15,21,29,34,38,42,46,50,56,62,70,73,76,81,85,89,94,99,107,112,116,121]
        print("matsui")
    start = time.perf_counter()
    total = time.perf_counter()
    while weight<upper:
        cnfpath="Kurahara_project/projects/SPECK/cnffile/SPECK_64_cnf/64_R%d_DCP%d.cnf"%(max_round,weight)
        logpath="Kurahara_project/projects/SPECK/logfile/SPECK_64_log/R%d_DCP%d.txt"%(max_round,weight)
        num=1
        PT1=[]
        PT2=[]
        PT1_shifted=[]
        PT2_shifted=[]
        w=[]
        cnf=[]
        for round in range(max_round):
            PT1.append([i for i in range(num,num+32)])
            num+=32
            PT2.append([i for i in range(num,num+32)])
            num+=32
            w.append([i for i in range(num,num+31)])
            num+=31
            PT1_shifted.append(PT1[round][24:]+PT1[round][:24])
            PT2_shifted.append(PT2[round][3:]+PT2[round][:3])
        PT1.append([i for i in range(num,num+32)])
        num+=32
        PT2.append([i for i in range(num,num+32)])
        num+=32

        cnf.extend([PT1[0]+PT2[0]])
        for round in range(max_round):
            addition(cnf,PT1_shifted[round],PT2[round],PT1[round+1],w[round])
            for i in range(32):
                vars=[PT1[round+1][i]]+[PT2_shifted[round][i]]+[PT2[round+1][i]]
                cnf.extend(get_espresso_result_cnf("snow/espresso/xor_2bit_espresso.txt",vars))
        SPECK32_cnf = CNF(from_clauses = cnf)
        if matsui:
            for n in range(max_round-2,-1,-1):
                SPECK32_cnf = CNF(from_clauses = cnf)
                prob=[]
                for round in range(n+1,max_round):
                    prob.extend(w[round])
                rw=weight-dcp[n]
                encode=CardEnc.atmost(lits = prob,bound = rw,top_id = SPECK32_cnf.nv,encoding = 6)
                cnf.extend(encode)
        prob=[]
        SPECK32_cnf = CNF(from_clauses = cnf)
        for round in range(max_round):
            prob.extend(w[round])
        encode = CardEnc.atmost(lits = prob,bound = weight,top_id = SPECK32_cnf.nv,encoding = 6)
        cnf.extend(encode)
        SPECK32_cnf = CNF(from_clauses = cnf)
        SPECK32_cnf.to_file(cnfpath)
        s = solver_func.solver.Solver(cnfpath,logpath)
        s.kissat_MAB_HyWalk()
        result = s.CheckResult()
        if result == True:
            solution = solver_func.extract_solution.Extract_Solution(logpath)
            with open(logpath,"w") as f:
                for r in range(max_round):
                    solver_func.update_logfile.Update_LogFile(f,solution,PT1,r,32,"PT1",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT2,r,32,"PT2",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT1_shifted,r,32,"PT1_shift",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT2_shifted,r,32,"PT2_shift",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,w,r,15,"w",15)
                    f.write("==============================================================================================\n")
                solver_func.update_logfile.Update_LogFile(f,solution,PT1,r,32,"PT1",4)
                solver_func.update_logfile.Update_LogFile(f,solution,PT2,r,32,"PT2",4)
        if result == True:
            end = time.perf_counter()
            print("Round%d , weight %d : SAT   | elapsed_time = %lf[s]  total_time = %lf[s]"%(max_round,weight,(end-start),(end-total)),flush = True)
            start = time.perf_counter()
            weight += up
            break
        else:
            end = time.perf_counter()
            print("Round%d , weight %d : UNSAT | elapsed_time = %lf[s]  total_time = %lf[s]"%(max_round,weight,(end-start),(end-total)),flush = True)
            start = time.perf_counter()
            weight += up

def SPECK96_DCP(max_round,weight,upper,up,matsui):
    if matsui:
        dcp=[0,1,3,6,10,15,21,30,39,49]
        print("matsui")
    start = time.perf_counter()
    total = time.perf_counter()
    while weight<upper:
        cnfpath="Kurahara_project/projects/SPECK/cnffile/SPECK_96_cnf/96_R%d_DCP%d.cnf"%(max_round,weight)
        logpath="Kurahara_project/projects/SPECK/logfile/SPECK_96_log/R%d_DCP%d.txt"%(max_round,weight)
        num=1
        PT1=[]
        PT2=[]
        PT1_shifted=[]
        PT2_shifted=[]
        w=[]
        cnf=[]
        for round in range(max_round):
            PT1.append([i for i in range(num,num+48)])
            num+=48
            PT2.append([i for i in range(num,num+48)])
            num+=48
            w.append([i for i in range(num,num+47)])
            num+=47
            PT1_shifted.append(PT1[round][40:]+PT1[round][:40])
            PT2_shifted.append(PT2[round][3:]+PT2[round][:3])
        PT1.append([i for i in range(num,num+48)])
        num+=48
        PT2.append([i for i in range(num,num+48)])
        num+=48

        cnf.extend([PT1[0]+PT2[0]])
        for round in range(max_round):
            addition(cnf,PT1_shifted[round],PT2[round],PT1[round+1],w[round])
            for i in range(48):
                vars=[PT1[round+1][i]]+[PT2_shifted[round][i]]+[PT2[round+1][i]]
                cnf.extend(get_espresso_result_cnf("snow/espresso/xor_2bit_espresso.txt",vars))
        SPECK32_cnf = CNF(from_clauses = cnf)
        if matsui:
            for n in range(max_round-2,-1,-1):
                SPECK32_cnf = CNF(from_clauses = cnf)
                prob=[]
                for round in range(n+1,max_round):
                    prob.extend(w[round])
                rw=weight-dcp[n]
                encode=CardEnc.atmost(lits = prob,bound = rw,top_id = SPECK32_cnf.nv,encoding = 6)
                cnf.extend(encode)
        prob=[]
        SPECK32_cnf = CNF(from_clauses = cnf)
        for round in range(max_round):
            prob.extend(w[round])
        encode = CardEnc.atmost(lits = prob,bound = weight,top_id = SPECK32_cnf.nv,encoding = 6)
        cnf.extend(encode)
        SPECK32_cnf = CNF(from_clauses = cnf)
        SPECK32_cnf.to_file(cnfpath)
        s = solver_func.solver.Solver(cnfpath,logpath)
        s.kissat_MAB_HyWalk()
        result = s.CheckResult()
        if result == True:
            solution = solver_func.extract_solution.Extract_Solution(logpath)
            with open(logpath,"w") as f:
                for r in range(max_round):
                    solver_func.update_logfile.Update_LogFile(f,solution,PT1,r,48,"PT1",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT2,r,48,"PT2",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT1_shifted,r,48,"PT1_shift",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT2_shifted,r,48,"PT2_shift",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,w,r,15,"w",15)
                    f.write("==============================================================================================\n")
                solver_func.update_logfile.Update_LogFile(f,solution,PT1,r,48,"PT1",4)
                solver_func.update_logfile.Update_LogFile(f,solution,PT2,r,48,"PT2",4)
        if result == True:
            end = time.perf_counter()
            print("Round%d , weight %d : SAT   | elapsed_time = %lf[s]  total_time = %lf[s]"%(max_round,weight,(end-start),(end-total)),flush = True)
            start = time.perf_counter()
            weight += up
            break
        else:
            end = time.perf_counter()
            print("Round%d , weight %d : UNSAT | elapsed_time = %lf[s]  total_time = %lf[s]"%(max_round,weight,(end-start),(end-total)),flush = True)
            start = time.perf_counter()
            weight += up

def SPECK128_DCP(max_round,weight,upper,up,matsui):
    if matsui:
        dcp=[0,1,3,6,10,15,21,30,39]
    start = time.perf_counter()
    total = time.perf_counter()
    while weight<upper:
        cnfpath="Kurahara_project/projects/SPECK/cnffile/SPECK_128_cnf/128_R%d_DCP%d.cnf"%(max_round,weight)
        logpath="Kurahara_project/projects/SPECK/logfile/SPECK_128_log/R%d_DCP%d.txt"%(max_round,weight)
        num=1
        PT1=[]
        PT2=[]
        PT1_shifted=[]
        PT2_shifted=[]
        w=[]
        cnf=[]
        for round in range(max_round):
            PT1.append([i for i in range(num,num+64)])
            num+=64
            PT2.append([i for i in range(num,num+64)])
            num+=64
            w.append([i for i in range(num,num+63)])
            num+=63
            PT1_shifted.append(PT1[round][56:]+PT1[round][:56])
            PT2_shifted.append(PT2[round][3:]+PT2[round][:3])
        PT1.append([i for i in range(num,num+64)])
        num+=64
        PT2.append([i for i in range(num,num+64)])
        num+=64
        print(num)

        cnf.extend([PT1[0]+PT2[0]])
        for round in range(max_round):
            addition(cnf,PT1_shifted[round],PT2[round],PT1[round+1],w[round])
            for i in range(64):
                vars=[PT1[round+1][i]]+[PT2_shifted[round][i]]+[PT2[round+1][i]]
                cnf.extend(get_espresso_result_cnf("snow/espresso/xor_2bit_espresso.txt",vars))
                SPECK32_cnf = CNF(from_clauses = cnf)
        if matsui:
            for n in range(max_round-2,-1,-1):
                SPECK32_cnf = CNF(from_clauses = cnf)
                prob=[]
                for round in range(n+1,max_round):
                    prob.extend(w[round])
                rw=weight-dcp[n]
                encode=CardEnc.atmost(lits = prob,bound = rw,top_id = SPECK32_cnf.nv,encoding = 6)
                cnf.extend(encode)
        prob=[]
        SPECK32_cnf = CNF(from_clauses = cnf)
        for round in range(max_round):
            prob.extend(w[round])
        encode = CardEnc.atmost(lits = prob,bound = weight,top_id = SPECK32_cnf.nv,encoding = 6)
        cnf.extend(encode)
        SPECK32_cnf = CNF(from_clauses = cnf)
        SPECK32_cnf.to_file(cnfpath)
        s = solver_func.solver.Solver(cnfpath,logpath)
        s.kissat_MAB_HyWalk()
        result = s.CheckResult()
        if result == True:
            solution = solver_func.extract_solution.Extract_Solution(logpath)
            with open(logpath,"w") as f:
                for r in range(max_round):
                    solver_func.update_logfile.Update_LogFile(f,solution,PT1,r,64,"PT1",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT2,r,64,"PT2",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT1_shifted,r,64,"PT1_shift",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,PT2_shifted,r,64,"PT2_shift",4)
                    solver_func.update_logfile.Update_LogFile(f,solution,w,r,15,"w",15)
                    f.write("==============================================================================================\n")
                solver_func.update_logfile.Update_LogFile(f,solution,PT1,r,64,"PT1",4)
                solver_func.update_logfile.Update_LogFile(f,solution,PT2,r,64,"PT2",4)
        if result == True:
            end = time.perf_counter()
            print("Round%d , weight %d : SAT   | elapsed_time = %lf[s]  total_time = %lf[s]"%(max_round,weight,(end-start),(end-total)),flush = True)
            start = time.perf_counter()
            weight += up
            break
        else:
            end = time.perf_counter()
            print("Round%d , weight %d : UNSAT | elapsed_time = %lf[s]  total_time = %lf[s]"%(max_round,weight,(end-start),(end-total)),flush = True)
            start = time.perf_counter()
            weight += up

