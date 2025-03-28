import sys
sys.path.append('Kurahara_project')

from pysat.card import *
from pysat.formula import CNF
from solver_func.append_cnf import get_espresso_result_cnf,XOR92
from itertools import chain
import time
import solver_func.solver
import solver_func.extract_solution
import solver_func.update_logfile

Sigma=[0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15]
BIT_SIZE=16*8
P_NUM=16*7
W_NUM=16*8-4

def swap(data):
    tmp=[]
    tmp.extend(data[8:])
    tmp.extend(data[:8])
    return tmp

def addition(cnf,In1,In2,Out,w):
    for i in range(4):
        in1=[]
        in2=[]
        out=[]
        for j in range(4):
            in1.extend(In1[i*32+(3-j)*8:i*32+(3-j)*8+8])
            in2.extend(In2[i*32+(3-j)*8:i*32+(3-j)*8+8])
            out.extend(Out[i*32+(3-j)*8:i*32+(3-j)*8+8])
        vars=in1+in2+out
        # print(vars)
        cnf+=(get_espresso_result_cnf("./snow/espresso/addition_32.txt",vars))
        cnf+=[[-in1[-1],-in2[-1],-out[-1]]]
        cnf+=[[-in1[-1],in2[-1],out[-1]]]
        cnf+=[[in1[-1],-in2[-1],out[-1]]]
        cnf+=[[in1[-1],in2[-1],-out[-1]]]
        vars+=w[i*31:i*31+31]
        # print(vars)
        cnf+=(get_espresso_result_cnf("./snow/espresso/weight_32.txt",vars))

def permuteR1(R1):
    tmpR1=[]
    for i in range(16):
        for j in range(8):
            tmpR1.append(R1[Sigma[i]*8+j])
    return tmpR1

class snowv_Rkey:
    def __init__(self,max_round,weight,upper,up,key,lim,dc,matsui,par):
        self.max_round=max_round
        self.weight=weight
        self.upper=upper
        self.up=up
        self.key=key
        self.lim=lim
        self.dc=dc
        self.matsui=matsui
        self.par=par

    def make_file(self):
        if self.dc:
            dc="DC_"
        else:
            dc=""
        if self.lim:
            l="lim_"
        else:
            l=""
        cnfpath= "Kurahara_project/projects/SNOW/SNOWV/cnffile/dif/Rkey_%s%sR%d_DCP%d.cnf"%(dc,l,self.max_round,self.weight)
        logpath1="Kurahara_project/projects/SNOW/SNOWV/logfile/dif/Rkey_%s%sprob_R%d_DCP%d.txt"%(dc,l,self.max_round,self.weight)
        logpath2="Kurahara_project/projects/SNOW/SNOWV/logfile/dif/Rkey_%s%slocal_R%d_DCP%d.txt"%(dc,l,self.max_round,self.weight)
        logpath3="Kurahara_project/projects/SNOW/SNOWV/logfile/dif/Rkey_%s%slocal2_R%d_DCP%d.txt"%(dc,l,self.max_round,self.weight)
        logpath4="Kurahara_project/projects/SNOW/SNOWV/logfile/dif/Rkey_%s%scheckR1_R%d_DCP%d.txt"%(dc,l,self.max_round,self.weight)
        return cnfpath,logpath1,logpath2,logpath3,logpath4

    def make_w(self):
        if self.key:
            if self.max_round==5:
                w=[0,0,0,10]
            elif self.max_round==6:
                w=[0,0,0,10,21]
        else:
            if self.max_round==4:
                w=[0,6,13]
            elif self.max_round==5:
                w=[0,6,13,73]
        return w

    def block_init(self,beA,A_mul,A_invmul,afA,B,B_mul,B_invmul,T1,T2,R1,perR1,R2,R3,R1T1,R3T2,w1,w2,R2_sboxed,R2_shifted,R2_temp,R2_prob,R3_sboxed,R3_shifted,R3_temp,R3_prob,z):
        num=2
        if self.key:
            if not self.lim:
                afA[0]=[i for i in range(num,16*16+num)]
                num+=16*16
            B[0][16*8:]=[i for i in range(num,16*8+num)]
            num+=16*8
        else:
            afA[0][:16*8]=[i for i in range(num,16*8+num)]
            num+=16*8

        for n in range(1,self.max_round+1):
            beA[n][:16*8]=afA[n-1][16*8:]
            beA[n][16*8:]=[i for i in range(num,num+16*8)]
            num+=16*8
            afA[n][:16*8]=beA[n][:16*8]
            afA[n][16*8:]=[i for i in range(num,num+16*8)]
            num+=16*8
            
        for n in range(self.max_round+1):
            T2[n]=afA[n][:16*8]

        for n in range(1,self.max_round+1):
            A_mul[n]=[i for i in range(num,num+16*8)]
            num+=16*8
            A_invmul[n]=[i for i in range(num,num+16*8)]
            num+=16*8

        for n in range(1,self.max_round+1):
            B[n][:16*8]=B[n-1][16*8:]
            B[n][16*8:]=[i for i in range(num,num+16*8)]
            num+=16*8
        
        for n in range(self.max_round+1):
            T1[n]=B[n][16*8:]
            
        for n in range(1,self.max_round+1):
            B_mul[n]=[i for i in range(num,num+16*8)]
            num+=16*8
            B_invmul[n]=[i for i in range(num,num+16*8)]
            num+=16*8

        for n in range(1,self.max_round+2):
            R1T1[n]=[i for i in range(num,num+16*8)]
            num+=16*8
            if n!=self.max_round+1:
                R3T2[n]=[i for i in range(num,num+16*8)]
                num+=16*8

        for n in range(1,self.max_round+1):
            R1[n]=[i for i in range(num,num+16*8)]
            num+=16*8
            perR1[n]=permuteR1(R1[n])

        for n in range(1,self.max_round+1):
            R2_sboxed[n]=[i for i in range(num,num+16*8)]
            num+=16*8
            for i in range(4):
                for j in range(4):
                    R2_shifted[n][i*32+(j*8):i*32+((j+1)*8)]=R2_sboxed[n][((i+j)%4)*32+(j*8):((i+j)%4)*32+(j+1)*8]
            R2_temp[n]=[i for i in range(num,num+60*4)]
            num+=60*4
            R2[n]=[i for i in range(num,num+16*8)]
            num+=16*8

        for n in range(1,self.max_round+1):
            R3_sboxed[n]=[i for i in range(num,num+16*8)]
            num+=16*8
            for i in range(4):
                for j in range(4):
                    R3_shifted[n][i*32+(j*8):i*32+((j+1)*8)]=R3_sboxed[n][((i+j)%4)*32+(j*8):((i+j)%4)*32+(j+1)*8]
            R3_temp[n]=[i for i in range(num,num+60*4)]
            num+=60*4
            R3[n]=[i for i in range(num,num+16*8)]
            num+=16*8

        for n in range(1,self.max_round+2):
            z[n]=[i for i in range(num,num+16*8)]
            num+=16*8

        for n in range(1,self.max_round+2):
            w1[n]=[i for i in range(num,num+16*8-4)]
            num+=16*8-4

        for n in range(1,self.max_round+1):
            w2[n]=[i for i in range(num,num+16*8-4)]
            num+=16*8-4
        
        perR1[self.max_round-1]=[i for i in range(num,num+16*8)]
        num+=16*8
        perR1[self.max_round]=[i for i in range(num,num+16*8)]
        num+=16*8

        if self.dc:
            for n in range(1,self.max_round+1):
                R2_prob[n]=[i for i in range(num,num+16*2)]
                num+=16*2
                R3_prob[n]=[i for i in range(num,num+16*2)]
                num+=16*2
        else:
            for n in range(1,self.max_round+1):
                R2_prob[n]=[i for i in range(num,num+16*7)]
                num+=16*7
                R3_prob[n]=[i for i in range(num,num+16*7)]
                num+=16*7

    def aes(self,cnf,Sin,Sout,sboxed,prob,shifted,temp,n):
        for i in range(16):
            if self.dc:
                vars=Sin[n-1][i*8:(i+1)*8]+sboxed[n][i*8:(i+1)*8]+prob[n][i*2:(i+1)*2]
                cnf+=(get_espresso_result_cnf("./snow/espresso/AES_sbox_DCSAT_espresso.txt",vars))
            else:
                vars=Sin[n-1][i*8:(i+1)*8]+sboxed[n][i*8:(i+1)*8]+prob[n][i*7:(i+1)*7]
                cnf+=(get_espresso_result_cnf("./snow/espresso/AES_sbox_espresso.txt",vars))
        for i in range(4):
            XOR92(cnf,shifted[n][32*i:32*i+32],temp[n][60*i:60*i+60],Sout[n][32*i:32*i+32])

    def fsm_update(self,cnf,T2,R1,perR1,R2,R3,R3T2,R2_sboxed,R2_shifted,R2_temp,R2_prob,R3_sboxed,R3_shifted,R3_temp,R3_prob,w2,n):
        for i in range(16*8):
            vars=[R3[n-1][i],T2[n-1][i],R3T2[n][i]]
            cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))
        addition(cnf,R2[n-1],R3T2[n],R1[n],w2[n])
        self.aes(cnf,perR1,R2,R2_sboxed,R2_prob,R2_shifted,R2_temp,n)
        self.aes(cnf,R2,R3,R3_sboxed,R3_prob,R3_shifted,R3_temp,n)

    def lfsr_update(self,cnf,beA,A_mul,A_invmul,afA,B,B_mul,B_invmul,n):
        for i in range(8):
            t=i*16
            vars=swap(afA[n-1][t:t+16])+A_mul[n][t:t+16]
            cnf+=(get_espresso_result_cnf("./snow/espresso/A_mul_x_espresso.txt",vars))
            vars=swap(afA[n-1][t+8*16:t+9*16])+A_invmul[n][t:t+16]
            cnf+=(get_espresso_result_cnf("./snow/espresso/A_invmul_x_espresso.txt",vars))
            vars=swap(B[n-1][t:t+16])+B_mul[n][t:t+16]
            cnf+=(get_espresso_result_cnf("./snow/espresso/B_mul_x_espresso.txt",vars))
            vars=swap(B[n-1][t+8*16:t+9*16])+B_invmul[n][t:t+16]
            cnf+=(get_espresso_result_cnf("./snow/espresso/B_invmul_x_espresso.txt",vars))

            a1=swap(B[n-1][t:t+16])
            a2=A_mul[n][t:t+16]
            a3=swap(afA[n-1][t+1*16:t+2*16])
            a4=A_invmul[n][t:t+16]
            a=swap(beA[n][t+8*16:t+9*16])

            b1=swap(afA[n-1][t:t+16])
            b2=B_mul[n][t:t+16]
            b3=swap(B[n-1][t+3*16:t+4*16])
            b4=B_invmul[n][t:t+16]
            b=swap(B[n][t+8*16:t+9*16])

            for j in range(16):
                vars=[a1[j],a2[j],a3[j],a4[j],a[j]]
                cnf+=(get_espresso_result_cnf("./snow/espresso/xor_4bit_espresso.txt",vars))
                vars=[b1[j],b2[j],b3[j],b4[j],b[j]]
                cnf+=(get_espresso_result_cnf("./snow/espresso/xor_4bit_espresso.txt",vars))

    def sat_snowv_Rkey_DCP(self):
        if self.dc:
            print("DC")
        if self.matsui:
            print("matsui")
        if self.key:
            print("key")
            if self.lim:
                print("lim")
        start = time.perf_counter()
        total = time.perf_counter()
        while self.weight< self.upper:
            cnfpath,logpath1,logpath2,logpath3,logpath4=self.make_file()
            d0=1
            beA=[[d0 for _ in range(32*8)]for _ in range(self.max_round+1)]
            A_mul=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            A_invmul=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            afA=[[d0 for _ in range(32*8)]for _ in range(self.max_round+1)]
            B=[[d0 for _ in range(32*8)]for _ in range(self.max_round+1)]
            B_mul=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            B_invmul=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            T1=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            T2=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R1=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            perR1=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R2=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R3=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R1T1=[[d0 for _ in range(16*8)]for _ in range(self.max_round+2)]
            R3T2=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            w1=[[d0 for _ in range(16*8-4)]for _ in range(self.max_round+2)]
            w2=[[d0 for _ in range(16*8-4)]for _ in range(self.max_round+1)]
            R2_sboxed=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R2_shifted=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R2_temp=[[d0 for _ in range(60*4)]for _ in range(self.max_round+1)]
            R2_prob=[[d0 for _ in range(16*7)]for _ in range(self.max_round+1)]
            R3_sboxed=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R3_shifted=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R3_temp=[[d0 for _ in range(60*4)]for _ in range(self.max_round+1)]
            R3_prob=[[d0 for _ in range(16*7)]for _ in range(self.max_round+1)]
            z=[[d0 for _ in range(16*8)]for _ in range(self.max_round+2)]
            if self.dc:
                R2_prob=[[d0 for _ in range(16*2)]for _ in range(self.max_round+1)]
                R3_prob=[[d0 for _ in range(16*2)]for _ in range(self.max_round+1)]
            cnf=[]
            self.block_init(beA,A_mul,A_invmul,afA,B,B_mul,B_invmul,T1,T2,R1,perR1,R2,R3,R1T1,R3T2,w1,w2,R2_sboxed,R2_shifted,R2_temp,R2_prob,R3_sboxed,R3_shifted,R3_temp,R3_prob,z)
            cnf+=[[-1]]

            if self.key and not self.lim:
                K=afA[0][16*8:]+B[0][16*8:]
                cnf+=[afA[0][:16*8]+K]
            elif self.key and self.lim:
                K=afA[0][16*8:]+B[0][16*8:]
                cnf+=[B[0][16*8:]]
            elif not self.key and self.lim:
                cnf+=[afA[0][:16*8]]
                IV=afA[0][:16*8]
                lim_encode = CardEnc.atmost(lits = IV,bound = 2,top_id = R3_prob[-1][-1],encoding = 6)
                cnf+=lim_encode
            elif not self.key and not self.lim:
                cnf+=[afA[0][:16*8]]

            for n in range(1,self.max_round+1):
                addition(cnf,perR1[n-1],T1[n-1],R1T1[n],w1[n])
                for i in range(16*8):
                    vars=[R1T1[n][i],R2[n-1][i],z[n][i]]
                    cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))
                self.fsm_update(cnf,T2,R1,perR1,R2,R3,R3T2,R2_sboxed,R2_shifted,R2_temp,R2_prob,R3_sboxed,R3_shifted,R3_temp,R3_prob,w2,n)
                self.lfsr_update(cnf,beA,A_mul,A_invmul,afA,B,B_mul,B_invmul,n)
                for i in range(16*8):
                    vars=[beA[n][16*8+i],z[n][i],afA[n][16*8+i]]
                    cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))
                if n==self.max_round-1:
                    R1_temp=permuteR1(R1[n])
                    for i in range(16*8):
                        vars=[R1_temp[i]]+[K[i]]+[perR1[n][i]]
                        cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))
                if n==self.max_round:
                    R1_temp=permuteR1(R1[n])
                    for i in range(16*8):
                        vars=[R1_temp[i]]+[K[16*8+i]]+[perR1[n][i]]
                        cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))
            addition(cnf,perR1[self.max_round],T1[self.max_round],R1T1[self.max_round+1],w1[self.max_round+1])
            for i in range(16*8):
                vars=[R1T1[self.max_round+1][i],R2[self.max_round][i],z[self.max_round+1][i]]
                cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))
            prob=[]
            snowv_cnf = CNF(from_clauses = cnf)
            if self.matsui:
                w=self.make_w()
                if self.dc:#DC_matsui
                    for n in range(self.max_round,0,-1):
                        if n == 2:
                            continue
                        if(n == 3 or n==4)and self.key:
                            continue
                        prob=[]
                        sv=[]
                        prob.extend(w1[self.max_round+1])
                        for i in range(n,self.max_round+1):
                            prob.extend(w2[i])
                            sv.extend(R2_prob[i])
                            if i<self.max_round-1:
                                prob.extend(w1[i])
                            if i!=self.max_round:
                                sv.extend(R3_prob[i])
                        if n>1:
                            prob.extend(w1[n-1])
                            sv.extend(R3_prob[n-1])
                        if n>2:
                            prob.extend(w1[n-2])
                        msv=[sv[d] for d in range(0, len(sv), 2)]
                        lsv=[sv[d] for d in range(1, len(sv), 2)]
                        prob.extend(list(msv) + 6 * list(lsv))
                        print("n=",n)
                        rw=self.weight-w[n-2]
                        if n==1:
                            rw=self.weight
                        print("rw=",rw)
                        encode = CardEnc.atmost(lits = prob,bound = rw,top_id = snowv_cnf.nv,encoding = 6)
                        snowv_cnf.extend(encode)
                else: #matsui
                    for n in range(self.max_round,0,-1):
                        if n == 2:
                            continue
                        if(n == 3 or n==4)and self.key:
                            continue
                        prob=[]
                        prob.extend(w1[self.max_round+1])
                        for i in range(n,self.max_round+1):
                            prob.extend(w2[i])
                            prob.extend(R2_prob[i])
                            if i<self.max_round-1:
                                prob.extend(w1[i])
                            if i!=self.max_round:
                                prob.extend(R3_prob[i])
                        if n>1:
                            prob.extend(w1[n-1])
                            prob.extend(R3_prob[n-1])
                        if n>2:
                            prob.extend(w1[n-2])
                        rw=self.weight-w[n-2]
                        if n==1:
                            rw=self.weight
                        print("n=",n)
                        print("rw=",rw)
                        encode = CardEnc.atmost(lits = prob,bound = rw,top_id = snowv_cnf.nv,encoding = 6)
                        snowv_cnf.extend(encode)
            else:
                if self.dc:#DC
                    sv=[]
                    for n in range(1,self.max_round+1):
                        prob.extend(w2[n])
                        sv.extend(R2_prob[n])
                        if n<self.max_round-1:
                            prob.extend(w1[n])
                        if n!=self.max_round:
                            sv.extend(R3_prob[n])
                    msv = [sv[d] for d in range(0, len(sv), 2)]
                    lsv = [sv[d] for d in range(1, len(sv), 2)]
                    prob.extend(list(msv) + 6 * list(lsv))
                else: #nomal
                    for n in range(1,self.max_round+1):
                        if n<self.max_round-1:
                            prob.extend(w1[n])                 
                        prob.extend(w2[n])
                        prob.extend(R2_prob[n])
                        if n!=self.max_round:
                            prob.extend(R3_prob[n])
                prob.extend(w1[self.max_round+1])
                encode = CardEnc.atmost(lits = prob,bound = self.weight,top_id = snowv_cnf.nv,encoding = 6)
                cnf+=encode
                snowv_cnf = CNF(from_clauses = cnf)
            snowv_cnf.to_file(cnfpath)
            if self.par:
                s = solver_func.solver.Solver(cnfpath,logpath1)
                s.ParKissat()
                result = s.CheckResult()
            else:
                s = solver_func.solver.Solver(cnfpath,logpath1)
                s.kissat_MAB_HyWalk()
                result = s.CheckResult()

            if result == True:
                solution = solver_func.extract_solution.Extract_Solution(logpath1)
                with open(logpath1,"w") as f:
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,afA[:16*8],0,BIT_SIZE,"iv",8)
                    if self.key:
                        K=[K]
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,K,0,BIT_SIZE*2,"k",8)
                    f.write("==============================================================================================\n")
                    if self.dc:
                        for r in range(1,self.max_round+1):
                            if r<self.max_round-1:                    
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,w1,r,W_NUM,"w1",31)
                            f.write("\n")
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,w2,r,W_NUM,"w2",31)
                            f.write("\n")
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,r-1,BIT_SIZE,"R1",8)
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,R2_sboxed,r,BIT_SIZE,"R2_Sout",8)
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,R2_prob,r,16*2,"R2_prob",2)
                            f.write("\n")
                            if r!=self.max_round:
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,R2,r-1,BIT_SIZE,"R2",8)
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,R3_sboxed,r,BIT_SIZE,"R3_Sout",8)
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,R3_prob,r,16*2,"R3_prob",2)
                            f.write("==============================================================================================\n")
                    else:
                        for r in range(1,self.max_round+1):
                            if r<self.max_round-1:                    
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,w1,r,W_NUM,"w1",31)
                            f.write("\n")
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,w2,r,W_NUM,"w2",31)
                            f.write("\n")
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,r-1,BIT_SIZE,"R1",8)
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,R2_sboxed,r,BIT_SIZE,"R2_Sout",8)
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,R2_prob,r,P_NUM,"R2_prob",7)
                            f.write("\n")
                            if r!=self.max_round:
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,R2,r-1,BIT_SIZE,"R2",8)
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,R3_sboxed,r,BIT_SIZE,"R3_Sout",8)
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,R3_prob,r,P_NUM,"R3_prob",7)
                            f.write("==============================================================================================\n")
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,w1,self.max_round+1,W_NUM,"w1",31)
                with open(logpath2,"w") as f:
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,afA[:16*8],0,BIT_SIZE,"iv",8)
                    if self.key:
                        k=[afA[0][16*8:]+B[0][16*8:]]
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,k,0,BIT_SIZE*2,"k",8)
                    f.write("==============================================================================================\n")
                    for r in range(self.max_round+1):
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,afA,r,BIT_SIZE*2,"a",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,B,r,BIT_SIZE*2,"b",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,r,BIT_SIZE,"R1",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,R2,r,BIT_SIZE,"R2",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,R3,r,BIT_SIZE,"R3",8)
                        f.write("==============================================================================================\n")
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,z,self.max_round+1,BIT_SIZE,"z",8)
                with open(logpath3,"w") as f:
                    for r in range(1,self.max_round+1):
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,T1,r-1,BIT_SIZE,"b",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,r-1,BIT_SIZE,"R1",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,R1T1,r,BIT_SIZE,"R1+b",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,w1,r,W_NUM,"w1",31)
                        f.write("\n")
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,T2,r-1,BIT_SIZE,"a",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,R2,r-1,BIT_SIZE,"R2",8)                          
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,R3,r-1,BIT_SIZE,"R3",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,R1,r,BIT_SIZE,"R2+a",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,w2,r,W_NUM,"w2",31)
                        f.write("==============================================================================================\n")
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,T1,self.max_round,BIT_SIZE,"b",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,self.max_round,BIT_SIZE,"R1",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,R2,self.max_round,BIT_SIZE,"R2",8) 
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,z,self.max_round+1,BIT_SIZE,"z",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,w1,self.max_round+1,W_NUM,"w1",31)
                with open(logpath4,"w") as f:
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,K,0,BIT_SIZE*2,"k",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,R1,self.max_round-1,BIT_SIZE,"R1",8)
                    R1_temp=[permuteR1(R1[self.max_round-1])]
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,R1_temp,0,BIT_SIZE,"R1_temp",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,self.max_round-1,BIT_SIZE,"perR1",8)
                    f.write("\n")
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,K,0,BIT_SIZE*2,"k",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,R1,self.max_round,BIT_SIZE,"R1",8)
                    R1_temp=[permuteR1(R1[self.max_round])]
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,R1_temp,0,BIT_SIZE,"R1_temp",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,self.max_round,BIT_SIZE,"perR1",8)

            if result == True:
                end = time.perf_counter()
                print("Round%d , weight %d : SAT   | elapsed_time = %lf[s]  total_time = %lf[s]"%(self.max_round,self.weight,(end-start),(end-total)),flush = True)
                start = time.perf_counter()
                self.weight += self.up
                break
            else:
                end = time.perf_counter()
                print("Round%d , weight %d : UNSAT | elapsed_time = %lf[s]  total_time = %lf[s]"%(self.max_round,self.weight,(end-start),(end-total)),flush = True)
                start = time.perf_counter()
                self.weight += self.up

class snowvi_Rkey:
    def __init__(self,max_round,weight,upper,up,key,lim,dc,matsui,par):
        self.max_round=max_round
        self.weight=weight
        self.upper=upper
        self.up=up
        self.key=key
        self.lim=lim
        self.dc=dc
        self.matsui=matsui
        self.par=par

    def make_file(self):
        if self.dc:
            dc="DC_"
        else:
            dc=""
        if self.lim:
            l="lim_"
        else:
            l=""
        cnfpath= "Kurahara_project/projects/SNOW/SNOWVI/cnffile/dif/Rkey_%s%sR%d_DCP%d.cnf"%(dc,l,self.max_round,self.weight)
        logpath1="Kurahara_project/projects/SNOW/SNOWVI/logfile/dif/Rkey_%s%sprob_R%d_DCP%d.txt"%(dc,l,self.max_round,self.weight)
        logpath2="Kurahara_project/projects/SNOW/SNOWVI/logfile/dif/Rkey_%s%slocal_R%d_DCP%d.txt"%(dc,l,self.max_round,self.weight)
        logpath3="Kurahara_project/projects/SNOW/SNOWVI/logfile/dif/Rkey_%s%slocal2_R%d_DCP%d.txt"%(dc,l,self.max_round,self.weight)
        logpath4="Kurahara_project/projects/SNOW/SNOWVI/logfile/dif/Rkey_%s%scheckR1_R%d_DCP%d.txt"%(dc,l,self.max_round,self.weight)
        return cnfpath,logpath1,logpath2,logpath3,logpath4

    def make_w(self):
        if self.key:
            if self.max_round==4:
                w=[0,0,2]
            elif self.max_round==5:
                w=[0,0,2,14]
            elif self.max_round==6:
                w=[0,0,2,14,28]
            elif self.max_round==7:
                w=[0,0,2,14,28,52]
            elif self.max_round==8:
                w=[0,0,2,14,28,52,87]
        else:
            if self.max_round==4:
                w=[0,0,9]
            elif self.max_round==5:
                w=[0,0,9,32]
        return w

    def block_init(self,beA,A_mul,afA,B,B_mul,T1,T2,R1,perR1,R2,R3,R1T1,R3T2,w1,w2,R2_sboxed,R2_shifted,R2_temp,R2_prob,R3_sboxed,R3_shifted,R3_temp,R3_prob,z):
        num=2
        if self.lim:
            num=34
        if self.key:
            if not self.lim:
                afA[0][16*8:]=[i for i in range(num,16*8+num)]
                num+=16*8
            afA[0][:16*8]=[i for i in range(num,16*8+num)]
            num+=16*8    
            B[0][16*8:]=[i for i in range(num,16*8+num)]
            num+=16*8
        else:
            afA[0][:16*8]=[i for i in range(num,16*8+num)]
            num+=16*8

        for n in range(1,self.max_round+1):
            beA[n][:16*8]=afA[n-1][16*8:]
            beA[n][16*8:]=[i for i in range(num,num+16*8)]
            num+=16*8
            afA[n][:16*8]=beA[n][:16*8]
            afA[n][16*8:]=[i for i in range(num,num+16*8)]
            num+=16*8
            
        for n in range(self.max_round+1):
            T2[n]=afA[n][16*8:]

        for n in range(1,self.max_round+1):
            A_mul[n]=[i for i in range(num,num+16*8)]
            num+=16*8

        for n in range(1,self.max_round+1):
            B[n][:16*8]=B[n-1][16*8:]
            B[n][16*8:]=[i for i in range(num,num+16*8)]
            num+=16*8
        
        for n in range(self.max_round+1):
            T1[n]=B[n][16*8:]
            
        for n in range(1,self.max_round+1):
            B_mul[n]=[i for i in range(num,num+16*8)]
            num+=16*8

        for n in range(1,self.max_round+2):
            R1T1[n]=[i for i in range(num,num+16*8)]
            num+=16*8
            if n!=self.max_round+1:
                R3T2[n]=[i for i in range(num,num+16*8)]
                num+=16*8

        for n in range(1,self.max_round+1):
            R1[n]=[i for i in range(num,num+16*8)]
            num+=16*8
            perR1[n]=permuteR1(R1[n])

        for n in range(1,self.max_round+1):
            R2_sboxed[n]=[i for i in range(num,num+16*8)]
            num+=16*8
            for i in range(4):
                for j in range(4):
                    R2_shifted[n][i*32+(j*8):i*32+((j+1)*8)]=R2_sboxed[n][((i+j)%4)*32+(j*8):((i+j)%4)*32+(j+1)*8]
            R2_temp[n]=[i for i in range(num,num+60*4)]
            num+=60*4
            R2[n]=[i for i in range(num,num+16*8)]
            num+=16*8

        for n in range(1,self.max_round+1):
            R3_sboxed[n]=[i for i in range(num,num+16*8)]
            num+=16*8
            for i in range(4):
                for j in range(4):
                    R3_shifted[n][i*32+(j*8):i*32+((j+1)*8)]=R3_sboxed[n][((i+j)%4)*32+(j*8):((i+j)%4)*32+(j+1)*8]
            R3_temp[n]=[i for i in range(num,num+60*4)]
            num+=60*4
            R3[n]=[i for i in range(num,num+16*8)]
            num+=16*8

        for n in range(1,self.max_round+2):
            z[n]=[i for i in range(num,num+16*8)]
            num+=16*8

        for n in range(1,self.max_round+2):
            w1[n]=[i for i in range(num,num+16*8-4)]
            num+=16*8-4

        for n in range(1,self.max_round+1):
            w2[n]=[i for i in range(num,num+16*8-4)]
            num+=16*8-4

        perR1[self.max_round-1]=[i for i in range(num,num+16*8)]
        num+=16*8
        perR1[self.max_round]=[i for i in range(num,num+16*8)]
        num+=16*8

        if self.dc:
            for n in range(1,self.max_round+1):
                R2_prob[n]=[i for i in range(num,num+16*2)]
                num+=16*2
                R3_prob[n]=[i for i in range(num,num+16*2)]
                num+=16*2
        else:
            for n in range(1,self.max_round+1):
                R2_prob[n]=[i for i in range(num,num+16*7)]
                num+=16*7
                R3_prob[n]=[i for i in range(num,num+16*7)]
                num+=16*7

        # print(num)

    def aes(self,cnf,Sin,Sout,sboxed,prob,shifted,temp,n):
        for i in range(16):
            if self.dc:
                vars=Sin[n-1][i*8:(i+1)*8]+sboxed[n][i*8:(i+1)*8]+prob[n][i*2:(i+1)*2]
                cnf+=(get_espresso_result_cnf("./snow/espresso/AES_sbox_DCSAT_espresso.txt",vars))
            else:                
                vars=Sin[n-1][i*8:(i+1)*8]+sboxed[n][i*8:(i+1)*8]+prob[n][i*7:(i+1)*7]
                cnf+=(get_espresso_result_cnf("./snow/espresso/AES_sbox_espresso.txt",vars))
        for i in range(4):
            XOR92(cnf,shifted[n][32*i:32*i+32],temp[n][60*i:60*i+60],Sout[n][32*i:32*i+32])

    def fsm_update(self,cnf,T2,R1,perR1,R2,R3,R3T2,R2_sboxed,R2_shifted,R2_temp,R2_prob,R3_sboxed,R3_shifted,R3_temp,R3_prob,w2,n):
        for i in range(16*8):
            vars=[R3[n-1][i],T2[n-1][i],R3T2[n][i]]
            cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))
        addition(cnf,R2[n-1],R3T2[n],R1[n],w2[n])
        self.aes(cnf,perR1,R2,R2_sboxed,R2_prob,R2_shifted,R2_temp,n)
        self.aes(cnf,R2,R3,R3_sboxed,R3_prob,R3_shifted,R3_temp,n)

    def lfsr_update(self,cnf,beA,A_mul,afA,B,B_mul,n):
        for i in range(8):
            t=i*16
            vars=swap(afA[n-1][t:t+16])+A_mul[n][t:t+16]
            cnf+=(get_espresso_result_cnf("./snow/espresso/viA_mul_x_espresso.txt",vars))
            vars=swap(B[n-1][t:t+16])+B_mul[n][t:t+16]
            cnf+=(get_espresso_result_cnf("./snow/espresso/viB_mul_x_espresso.txt",vars))

            a1=swap(B[n-1][t:t+16])
            a2=A_mul[n][t:t+16]
            a3=swap(afA[n-1][t+7*16:t+8*16])
            a=swap(beA[n][t+8*16:t+9*16])

            b1=swap(afA[n-1][t:t+16])
            b2=B_mul[n][t:t+16]
            b3=swap(B[n-1][t+8*16:t+9*16])
            b=swap(B[n][t+8*16:t+9*16])

            for j in range(16):
                vars=[a1[j],a2[j],a3[j],a[j]]
                cnf+=(get_espresso_result_cnf("./snow/espresso/xor_3bit_espresso.txt",vars))
                vars=[b1[j],b2[j],b3[j],b[j]]
                cnf+=(get_espresso_result_cnf("./snow/espresso/xor_3bit_espresso.txt",vars))

    def sat_snowvi_Rkey_DCP(self):
        start = time.perf_counter()
        total = time.perf_counter()
        if self.dc:
            print("DC")
        if self.matsui:
            print("matsui")
        if self.key:
            print("key")
            if self.lim:
                print("lim")
        while self.weight< self.upper:
            cnfpath,logpath1,logpath2,logpath3,logpath4=self.make_file()
            d0=1
            lim_flag=[i for i in range(2,34)]
            beA=[[d0 for _ in range(32*8)]for _ in range(self.max_round+1)]
            A_mul=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            afA=[[d0 for _ in range(32*8)]for _ in range(self.max_round+1)]
            B=[[d0 for _ in range(32*8)]for _ in range(self.max_round+1)]
            B_mul=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            T1=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            T2=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R1=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            perR1=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R2=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R3=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R1T1=[[d0 for _ in range(16*8)]for _ in range(self.max_round+2)]
            R3T2=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            w1=[[d0 for _ in range(16*8-4)]for _ in range(self.max_round+2)]
            w2=[[d0 for _ in range(16*8-4)]for _ in range(self.max_round+1)]
            R2_sboxed=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R2_shifted=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R2_temp=[[d0 for _ in range(60*4)]for _ in range(self.max_round+1)]
            R2_prob=[[d0 for _ in range(16*7)]for _ in range(self.max_round+1)]
            R3_sboxed=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R3_shifted=[[d0 for _ in range(16*8)]for _ in range(self.max_round+1)]
            R3_temp=[[d0 for _ in range(60*4)]for _ in range(self.max_round+1)]
            R3_prob=[[d0 for _ in range(16*7)]for _ in range(self.max_round+1)]
            z=[[d0 for _ in range(16*8)]for _ in range(self.max_round+2)]
            if self.dc:
                R2_prob=[[d0 for _ in range(16*2)]for _ in range(self.max_round+1)]
                R3_prob=[[d0 for _ in range(16*2)]for _ in range(self.max_round+1)]
            cnf=[]
            self.block_init(beA,A_mul,afA,B,B_mul,T1,T2,R1,perR1,R2,R3,R1T1,R3T2,w1,w2,R2_sboxed,R2_shifted,R2_temp,R2_prob,R3_sboxed,R3_shifted,R3_temp,R3_prob,z)
            cnf+=[[-1]]

            if self.key and not self.lim:
                K=afA[0][16*8:]+B[0][16*8:]
                cnf+=[afA[0][:16*8]+afA[0][16*8:]+B[0][16*8:]]
            elif self.key and self.lim:
                K=afA[0][16*8:]+B[0][16*8:]
                cnf+=[afA[0][:16*8]+B[0][16*8:]]
                for i in range(16):
                    vars=afA[0][i*8:i*8+8]+[lim_flag[i]]
                    cnf+=get_espresso_result_cnf("snow/espresso/snowvi_key_lim2_espresso.txt",vars)
                for i in range(16):
                    vars=B[0][16*8+i*8:16*8+i*8+8]+[lim_flag[16+i]]
                    cnf+=get_espresso_result_cnf("snow/espresso/snowvi_key_lim2_espresso.txt",vars)
                lim_encode = CardEnc.atmost(lits = lim_flag,bound = 4,top_id = R3_prob[-1][-1],encoding = 6)
                cnf+=lim_encode
            elif not self.key and self.lim:
                cnf+=[afA[0][:16*8]]
                IV=afA[0][:16*8]
                lim_encode = CardEnc.atmost(lits = IV,bound = 1,top_id = R3_prob[-1][-1],encoding = 6)
                cnf+=lim_encode
            elif not self.key and not self.lim:
                cnf+=[afA[0][:16*8]]

            for n in range(1,self.max_round+1):
                addition(cnf,perR1[n-1],T1[n-1],R1T1[n],w1[n])
                for i in range(16*8):
                    vars=[R1T1[n][i],R2[n-1][i],z[n][i]]
                    cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))
                self.fsm_update(cnf,T2,R1,perR1,R2,R3,R3T2,R2_sboxed,R2_shifted,R2_temp,R2_prob,R3_sboxed,R3_shifted,R3_temp,R3_prob,w2,n)
                self.lfsr_update(cnf,beA,A_mul,afA,B,B_mul,n)
                for i in range(16*8):
                    vars=[beA[n][16*8+i],z[n][i],afA[n][16*8+i]]
                    cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))
                if n==self.max_round-1:
                    R1_temp=permuteR1(R1[n])
                    for i in range(16*8):
                        vars=[R1_temp[i]]+[K[i]]+[perR1[n][i]]
                        cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))
                if n==self.max_round:
                    R1_temp=permuteR1(R1[n])
                    for i in range(16*8):
                        vars=[R1_temp[i]]+[K[16*8+i]]+[perR1[n][i]]
                        cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))
            addition(cnf,perR1[self.max_round],T1[self.max_round],R1T1[self.max_round+1],w1[self.max_round+1])
            for i in range(16*8):
                vars=[R1T1[self.max_round+1][i],R2[self.max_round][i],z[self.max_round+1][i]]
                cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))
            prob=[]
            snowvi_cnf = CNF(from_clauses = cnf)
            if self.matsui:
                w=self.make_w()
                if self.dc:  #DC_matsui
                    for n in range(self.max_round,0,-1):
                        if n ==2 or n==3:
                            continue
                        prob=[]
                        sv=[]
                        prob.extend(w1[self.max_round+1])
                        for i in range(n,self.max_round+1):
                            prob.extend(w2[i])
                            sv.extend(R2_prob[i])
                            if i!=self.max_round:
                                prob.extend(w1[i])
                                sv.extend(R3_prob[i])
                        if n>1:
                            prob.extend(w1[n-1])
                            sv.extend(R3_prob[n-1])
                        msv = [sv[d] for d in range(0, len(sv), 2)]
                        lsv = [sv[d] for d in range(1, len(sv), 2)]
                        prob.extend(list(msv) + 6 * list(lsv))
                        s=0
                        rw=self.weight-w[n-2]
                        if n==1:
                            rw=self.weight
                        encode = CardEnc.atmost(lits = prob,bound = rw,top_id = snowvi_cnf.nv,encoding = 6)
                        snowvi_cnf.extend(encode)
                else:  #matsui
                    for n in range(self.max_round,0,-1):
                        if n ==2 or n==3:
                            continue
                        prob=[]
                        prob.extend(w1[self.max_round+1])
                        for i in range(n,self.max_round+1):
                            prob.extend(w2[i])
                            prob.extend(R2_prob[i])
                            if i!=self.max_round:
                                prob.extend(w1[i])
                                prob.extend(R3_prob[i])
                        if n>1:
                            prob.extend(w1[n-1])
                            prob.extend(R3_prob[n-1])
                        rw=self.weight-w[n-2]
                        if n==1:
                            rw=self.weight
                        encode = CardEnc.atmost(lits = prob,bound = rw,top_id = snowvi_cnf.nv,encoding = 6)
                        snowvi_cnf.extend(encode)
            else:        
                if self.dc: #DC
                    sv=[]
                    for n in range(1,self.max_round+1):               
                        prob.extend(w2[n])
                        sv.extend(R2_prob[n])
                        if n!=self.max_round:
                            prob.extend(w1[n])
                            sv.extend(R3_prob[n])
                    msv = [sv[d] for d in range(0, len(sv), 2)]
                    lsv = [sv[d] for d in range(1, len(sv), 2)]
                    prob.extend(list(msv) + 6 * list(lsv))
                else: #nomal
                    for n in range(1,self.max_round+1):               
                        prob.extend(w2[n])
                        prob.extend(R2_prob[n])
                        if n!=self.max_round:
                            prob.extend(w1[n])
                            prob.extend(R3_prob[n])
                prob.extend(w1[self.max_round+1])
                encode = CardEnc.atmost(lits = prob,bound = self.weight,top_id = snowvi_cnf.nv,encoding = 6)
                cnf+=encode
                snowvi_cnf = CNF(from_clauses = cnf)
            snowvi_cnf.to_file(cnfpath)
            if self.par:
                s = solver_func.solver.Solver(cnfpath,logpath1)
                s.ParKissat()
                result = s.CheckResult()
            else:
                s = solver_func.solver.Solver(cnfpath,logpath1)
                s.kissat_MAB_HyWalk()
                result = s.CheckResult()
            lim_flag=[lim_flag]

            if result == True:
                solution = solver_func.extract_solution.Extract_Solution(logpath1)
                with open(logpath1,"w") as f:
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,afA[:16*8],0,BIT_SIZE,"iv",8)
                    if self.key:
                        k=[afA[0][16*8:]+B[0][16*8:]]
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,k,0,BIT_SIZE*2,"k",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,lim_flag,0,32,"lim_flag",8)
                    f.write("==============================================================================================\n")
                    if self.dc:
                        for r in range(1,self.max_round+1):
                            if r!=self.max_round-1:                    
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,w1,r,W_NUM,"w1",31)
                            f.write("\n")
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,w2,r,W_NUM,"w2",31)
                            f.write("\n")
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,r-1,BIT_SIZE,"R1",8)
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,R2_sboxed,r,BIT_SIZE,"R2_Sout",8)
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,R2_prob,r,16*2,"R2_prob",2)
                            f.write("\n")
                            if r!=self.max_round:
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,R2,r-1,BIT_SIZE,"R2",8)
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,R3_sboxed,r,BIT_SIZE,"R3_Sout",8)
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,R3_prob,r,16*2,"R3_prob",2)
                                f.write("==============================================================================================\n")
                    else:
                        for r in range(1,self.max_round+1):
                            if r!=self.max_round:                    
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,w1,r,W_NUM,"w1",31)
                            f.write("\n")
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,w2,r,W_NUM,"w2",31)
                            f.write("\n")
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,r-1,BIT_SIZE,"R1",8)
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,R2_sboxed,r,BIT_SIZE,"R2_Sout",8)
                            solver_func.update_logfile.Update_LogFile_inv(f,solution,R2_prob,r,P_NUM,"R2_prob",7)
                            f.write("\n")
                            if r!=self.max_round:
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,R2,r-1,BIT_SIZE,"R2",8)
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,R3_sboxed,r,BIT_SIZE,"R3_Sout",8)
                                solver_func.update_logfile.Update_LogFile_inv(f,solution,R3_prob,r,P_NUM,"R3_prob",7)
                                f.write("==============================================================================================\n")
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,w1,self.max_round+1,W_NUM,"w1",31)
                with open(logpath2,"w") as f:
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,afA[:16*8],0,BIT_SIZE,"iv",8)
                    if self.key:
                        k=[afA[0][16*8:]+B[0][16*8:]]
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,k,0,BIT_SIZE*2,"k",8)
                    f.write("==============================================================================================\n")
                    for r in range(self.max_round+1):
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,afA,r,BIT_SIZE*2,"a",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,B,r,BIT_SIZE*2,"b",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,r,BIT_SIZE,"R1",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,R2,r,BIT_SIZE,"R2",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,R3,r,BIT_SIZE,"R3",8)
                        f.write("==============================================================================================\n")
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,z,self.max_round+1,BIT_SIZE,"z",8)
                with open(logpath3,"w") as f:
                    for r in range(1,self.max_round+1):
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,T1,r-1,BIT_SIZE,"b",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,r-1,BIT_SIZE,"R1",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,R1T1,r,BIT_SIZE,"R1+b",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,w1,r,W_NUM,"w1",31)
                        f.write("\n")
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,T2,r-1,BIT_SIZE,"a",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,R2,r-1,BIT_SIZE,"R2",8)                          
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,R3,r-1,BIT_SIZE,"R3",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,R1,r,BIT_SIZE,"R2+a",8)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,w2,r,W_NUM,"w2",31)
                        f.write("==============================================================================================\n")
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,T1,self.max_round,BIT_SIZE,"b",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,self.max_round,BIT_SIZE,"R1",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,R2,self.max_round,BIT_SIZE,"R2",8) 
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,z,self.max_round+1,BIT_SIZE,"z",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,w1,self.max_round+1,W_NUM,"w1",31)
                with open(logpath4,"w") as f:
                    K=[K]
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,K,0,BIT_SIZE*2,"k",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,R1,self.max_round-1,BIT_SIZE,"R1",8)
                    R1_temp=[permuteR1(R1[self.max_round-1])]
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,R1_temp,0,BIT_SIZE,"R1_temp",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,self.max_round-1,BIT_SIZE,"perR1",8)
                    f.write("\n")
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,K,0,BIT_SIZE*2,"k",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,R1,self.max_round,BIT_SIZE,"R1",8)
                    R1_temp=[permuteR1(R1[self.max_round])]
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,R1_temp,0,BIT_SIZE,"R1_temp",8)
                    solver_func.update_logfile.Update_LogFile_inv(f,solution,perR1,self.max_round,BIT_SIZE,"perR1",8)

            if result == True:
                end = time.perf_counter()
                print("Round%d , weight %d : SAT   | elapsed_time = %lf[s]  total_time = %lf[s]"%(self.max_round,self.weight,(end-start),(end-total)),flush = True)
                start = time.perf_counter()
                self.weight += self.up
                break
            else:
                end = time.perf_counter()
                print("Round%d , weight %d : UNSAT | elapsed_time = %lf[s]  total_time = %lf[s]"%(self.max_round,self.weight,(end-start),(end-total)),flush = True)
                start = time.perf_counter()
                self.weight += self.up


