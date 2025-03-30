import sys
sys.path.append('/Users/kurahararikuto/Documents/python')

from pysat.card import *
from pysat.formula import CNF
from solver_func.integral_cnf import *
import itertools 
import time
import solver_func.solver
import solver_func.extract_solution
import solver_func.update_logfile

def init(cnf,max_round,Sin,shifted,in_row,out_row):
    inp = list(itertools.chain.from_iterable(Sin[0]))
    for bit in range(128):
        if bit == in_row:
            cnf.append([-inp[bit]])
        else:
            cnf.append([inp[bit]])
    out = list(itertools.chain.from_iterable(shifted[max_round-1]))
    for bit in range(128):
        if bit == out_row:
            cnf.append([out[bit]])
        else:
            cnf.append([-out[bit]])

def AES_int(max_round):
    cnfpath="Kurahara_project/projects/AES/cnf_file/round{}.cnf".format(max_round)
    logpath="Kurahara_project/projects/AES/log_file/round{}.txt".format(max_round)
    pathfile="Kurahara_project/projects/AES/path_file/round{}.txt".format(max_round)
    Sin = [[]for _ in range(max_round+1)]
    Sout = [[]for _ in range(max_round)]
    shifted = [[]for _ in range(max_round)]
    num = 1
    for round in range(max_round):
        for cell in range(16):
            Sin[round].append([_ for _ in range(num,num + 8)])
            num += 8
        for cell in range(16):
            Sout[round].append([_ for _ in range(num,num + 8)])
            num += 8
        for i in range(4):
            shifted[round].append(Sout[round][(i*4)%16])
            shifted[round].append(Sout[round][(i*4+5)%16])
            shifted[round].append(Sout[round][(i*4+10)%16])
            shifted[round].append(Sout[round][(i*4+15)%16])
    num_temp = num
    for in_row in range(128):
        balance_flag = 0
        for out_row in range(128):
            sat_flag = 0
            cnf = []
            num = num_temp
            init(cnf,max_round,Sin,shifted,in_row,out_row)
            for round in range(max_round-1):
                for cell in range(16):
                    cnf.extend(get_espresso_result_cnf("solver_func/espresso/integral/AES_sbox_espresso.txt",Sin[round][cell]+Sout[round][cell]))
                for i in range(4):
                    x = list(itertools.chain.from_iterable(shifted[round][i*4:(i+1)*4]))
                    y = list(itertools.chain.from_iterable(Sin[round+1][i*4:(i+1)*4]))
                    num = XOR_92(cnf,num,x,y)
            for cell in range(16):
                cnf.extend(get_espresso_result_cnf("solver_func/espresso/integral/AES_sbox_espresso.txt",Sin[max_round-1][cell]+Sout[max_round-1][cell]))
            aes_cnf = CNF(from_clauses = cnf)
            aes_cnf.to_file(cnfpath)
            s = solver_func.solver.Solver(cnfpath,logpath)
            s.kissat_sc2024()
            result = s.CheckResult()
            if result == True:
                sat_flag += 1

            if sat_flag == 0:
                balance_flag += 1

            if sat_flag > 0:
                print(f"AES_{max_round}round","input:",in_row,"output:",out_row,"-> Unknown",flush=True)
                solution = solver_func.extract_solution.Extract_Solution(logpath)
                if out_row == 2:
                    with open(pathfile,"w") as f:
                        for round in range(max_round-1):
                            f.write("round {}\n".format(round))
                            Sin_ = list(itertools.chain.from_iterable(Sin[round]))
                            Sout_ = list(itertools.chain.from_iterable(Sout[round]))
                            shifted_ = list(itertools.chain.from_iterable(shifted[round]))
                            solver_func.update_logfile.Update_LogFile_single(f,solution,Sin_,128,"Sin",8)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,Sout_,128,"Sout",8)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,shifted_,128,"shifted",8)
                            f.write("==============================================================================================\n")
                        f.write("round {}\n".format(max_round-1))
                        Sin_ = list(itertools.chain.from_iterable(Sin[max_round-1]))
                        Sout_ = list(itertools.chain.from_iterable(Sout[max_round-1]))
                        shifted_ = list(itertools.chain.from_iterable(shifted[max_round-1]))
                        solver_func.update_logfile.Update_LogFile_single(f,solution,Sin_,128,"Sin",8)
                        solver_func.update_logfile.Update_LogFile_single(f,solution,Sout_,128,"Sout",8)
                        solver_func.update_logfile.Update_LogFile_single(f,solution,shifted_,128,"shifted",8)
            if sat_flag == 0:
                print(f"AES_{max_round}round","input:",in_row,"output:",out_row,"-> Blance",flush=True)
    print(f"AES_{max_round}round end")

AES_int(1)
