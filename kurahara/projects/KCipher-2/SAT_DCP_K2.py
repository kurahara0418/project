import sys
sys.path.append('Kurahara_project')

from pysat.card import *
from pysat.formula import CNF
from solver_func.append_cnf import get_espresso_result_cnf,addition,XOR92,func_alpha_0,func_alpha_12,func_alpha_3
import time
import solver_func.solver
import solver_func.extract_solution
import solver_func.update_logfile

IV_SIZE=32*4
A_SIZE=32*5
B_SIZE=32*11
BIT_SIZE=8*4
PROB_NUM=7*4
AS_NUM=4

class K2_DCP:
    def __init__(self,max_round,weight,upper,up,lim,lim2,key):
        self.max_round=max_round
        self.weight=weight
        self.upper=upper
        self.up=up
        self.lim=lim
        self.lim2=lim2
        self.key=key

    def gen_key(self,cnf,d0,d1,K,K_temp,K_sboxed,K_prob,K_xor_temp):
        for i in range(4,12):
            if i==4:
                #temp:Subの中身
                temp=K[32*(i-1)+8:32*i]+K[32*(i-1):32*(i-1)+8]
                for j in range(4):
                    vars=temp[j*8:j*8+8]+K_sboxed[j*8:j*8+8]+K_prob[j*7:j*7+7]
                    cnf+=(get_espresso_result_cnf("./snow/espresso/AES_sbox_espresso.txt",vars))
                XOR92(cnf,K_sboxed[:32],K_xor_temp[:60],K_temp[:32])
                #temp:0x01000000
                temp=[d0 for _ in range(7)]+[d1]+[d0 for _ in range(24)]
                for j in range(32):
                    vars=[K[32*(i-4)+j]]+[K_temp[j]]+[temp[j]]+[K[32*i+j]]
                    cnf+=(get_espresso_result_cnf("./snow/espresso/xor_3bit_espresso.txt",vars))

            elif i==8:
                #temp:Subの中身
                temp=K[32*(i-1)+8:32*i]+K[32*(i-1):32*(i-1)+8]
                for j in range(4):
                    vars=temp[j*8:j*8+8]+K_sboxed[32+j*8:32+j*8+8]+K_prob[28+j*7:28+j*7+7]
                    cnf+=(get_espresso_result_cnf("./snow/espresso/AES_sbox_espresso.txt",vars))
                XOR92(cnf,K_sboxed[32:],K_xor_temp[60:],K_temp[32:])
                #temp:0x02000000
                temp=[d0 for _ in range(6)]+[d1]+[d0 for _ in range(25)]
                for j in range(32):
                    vars=[K[32*(i-4)+j]]+[K_temp[32+j]]+[temp[j]]+[K[32*i+j]]
                    cnf+=(get_espresso_result_cnf("./snow/espresso/xor_3bit_espresso.txt",vars))

            else:
                for j in range(32):
                    vars=[K[32*(i-4)+j]]+[K[32*(i-1)+j]]+[K[32*i+j]]
                    cnf+=(get_espresso_result_cnf("./snow/espresso/xor_2bit_espresso.txt",vars))

    def make_file(self):
        if self.lim:
            l1="lim_"
        else:
            l1=""
        if self.lim2:
            l2="lim2_"
        else:
            l2=""
        if self.key:
            k="key_"
        else:
            k=""
        cnfpath ="Kurahara_project/projects/KCipher-2/cnffile/%s%s%sK2_R%d_DCP%d.cnf"%(l1,l2,k,self.max_round,self.weight)
        logpath ="Kurahara_project/projects/KCipher-2/logfile/%s%s%sK2_R%d_DCP%d.txt"%(l1,l2,k,self.max_round,self.weight)
        logpath2="Kurahara_project/projects/KCipher-2/logfile/%s%s%sK2_checkAB_R%d_DCP%d.txt"%(l1,l2,k,self.max_round,self.weight)
        logpath3="Kurahara_project/projects/KCipher-2/logfile/%s%s%sK2_addcheck_R%d_DCP%d.txt"%(l1,l2,k,self.max_round,self.weight)
        return cnfpath,logpath,logpath2,logpath3

    def block_init(self,A,B,R1,R2,L1,L2,R1_sboxed,R2_sboxed,L1_sboxed,L2_sboxed,R1_xor_temp,R2_xor_temp,L1_xor_temp,L2_xor_temp,R1_prob,R2_prob,L1_prob,L2_prob,L2B9,L2B10,R2B4,R2B0,L2B9_w,L2B10_w,R2B4_w,R2B0_w,alpha_0,alpha_12,alpha_3,alpha_3_temp,alpha_12_flag,alpha_3_flag,alpha_12_p,alpha_3_p,flag_p,z_l,z_h):
        if self.key:
            num=692
        else:
            num=2

        B[0][32*2:32*4]=[i for i in range(num,num+32*2)]
        num+=32*2
        B[0][32*6:32*8]=[i for i in range(num,num+32*2)]
        num+=32*2

        for n in range(1,self.max_round+1):
            A[n][:32*4]=A[n-1][32*1:]
            A[n][32*4:]=[i for i in range(num,num+32)]
            num+=32
            B[n][:32*10]=B[n-1][32*1:]
            B[n][32*10:]=[i for i in range(num,num+32)]
            num+=32

        for n in range(1,self.max_round+1):
            R1[n]=[i for i in range(num,num+32)]
            num+=32
            R2[n]=[i for i in range(num,num+32)]
            num+=32
            L1[n]=[i for i in range(num,num+32)]
            num+=32
            L2[n]=[i for i in range(num,num+32)]
            num+=32
            R1_sboxed[n]=[i for i in range(num,num+32)]
            num+=32
            R2_sboxed[n]=[i for i in range(num,num+32)]
            num+=32
            L1_sboxed[n]=[i for i in range(num,num+32)]
            num+=32
            L2_sboxed[n]=[i for i in range(num,num+32)]
            num+=32
            R1_xor_temp[n]=[i for i in range(num,num+60)]
            num+=60
            R2_xor_temp[n]=[i for i in range(num,num+60)]
            num+=60
            L1_xor_temp[n]=[i for i in range(num,num+60)]
            num+=60
            L2_xor_temp[n]=[i for i in range(num,num+60)]
            num+=60
            R1_prob[n]=[i for i in range(num,num+7*4)]
            num+=7*4
            R2_prob[n]=[i for i in range(num,num+7*4)]
            num+=7*4
            L1_prob[n]=[i for i in range(num,num+7*4)]
            num+=7*4
            L2_prob[n]=[i for i in range(num,num+7*4)]
            num+=7*4
            L2B9[n]=[i for i in range(num,num+32)]
            num+=32
            L2B10[n]=[i for i in range(num,num+32)]
            num+=32     
            R2B4[n]=[i for i in range(num,num+32)]
            num+=32
            R2B0[n]=[i for i in range(num,num+32)]
            num+=32
            L2B9_w[n]=[i for i in range(num,num+31)]
            num+=31
            L2B10_w[n]=[i for i in range(num,num+31)]
            num+=31     
            R2B4_w[n]=[i for i in range(num,num+31)]
            num+=31
            R2B0_w[n]=[i for i in range(num,num+31)]
            num+=31
            alpha_0[n]=[i for i in range(num,num+32)]
            num+=32
            alpha_12[n]=[i for i in range(num,num+32)]
            num+=32
            alpha_3[n]=[i for i in range(num,num+32)]
            num+=32
            alpha_3_temp[n]=[i for i in range(num,num+32)]
            num+=32
            alpha_12_flag[n]=num
            num+=1
            alpha_3_flag[n]=num
            num+=1
            alpha_12_p[n]=num
            num+=1
            alpha_3_p[n]=num
            num+=1
            if n>4 and not self.key:
                flag_p[n]=[i for i in range(num,num+2)]
                num+=2
            elif self.key:
                flag_p[n]=[i for i in range(num,num+2)]
                num+=2
        
        L2B10[self.max_round+1]=[i for i in range(num,num+32)]
        num+=32
        R2B0[self.max_round+1]=[i for i in range(num,num+32)]
        num+=32
        L2B10_w[self.max_round+1]=[i for i in range(num,num+32)]
        num+=32
        R2B0_w[self.max_round+1]=[i for i in range(num,num+32)]
        num+=32

        for n in range(1,self.max_round+2):
            z_l[n]=[i for i in range(num,num+32)]
            num+=32
            z_h[n]=[i for i in range(num,num+32)]
            num+=32
        return num

    def aes_sub_DCP(self,cnf,input,sboxed,prob,xor_temp,output):
        for i in range(4):
            vars=input[(3-i)*8:(3-i)*8+8]+sboxed[i*8:i*8+8]+prob[i*7:i*7+7]
            if self.lim2:
                cnf+=(get_espresso_result_cnf("./snow/espresso/AES_sbox_lim_espresso.txt",vars))
            else:
                cnf+=(get_espresso_result_cnf("./snow/espresso/AES_sbox_espresso.txt",vars))
        output_temp=output[24:]+output[16:24]+output[8:16]+output[:8]
        XOR92(cnf,sboxed,xor_temp,output_temp)

    def NLF_update(self,cnf,B,R1,R2,L1,L2,R1_sboxed,R2_sboxed,L1_sboxed,L2_sboxed,R1_xor_temp,R2_xor_temp,L1_xor_temp,L2_xor_temp,R1_prob,R2_prob,L1_prob,L2_prob,L2B9,R2B4,L2B9_w,R2B4_w,n):
        addition(cnf,L2[n-1],B[n-1][32*9:32*10],L2B9[n],L2B9_w[n])
        addition(cnf,R2[n-1],B[n-1][32*4:32*5],R2B4[n],R2B4_w[n])
        self.aes_sub_DCP(cnf,L2B9[n],R1_sboxed[n],R1_prob[n],R1_xor_temp[n],R1[n])
        self.aes_sub_DCP(cnf,R1[n-1],R2_sboxed[n],R2_prob[n],R2_xor_temp[n],R2[n])
        self.aes_sub_DCP(cnf,R2B4[n],L1_sboxed[n],L1_prob[n],L1_xor_temp[n],L1[n])
        self.aes_sub_DCP(cnf,L1[n-1],L2_sboxed[n],L2_prob[n],L2_xor_temp[n],L2[n])

    def DFC_update(self,cnf,d0,A,B,alpha_0,alpha_12,alpha_3,alpha_3_temp,alpha_12_flag,alpha_3_flag,alpha_12_p,alpha_3_p,z_l,z_h,n):
        if self.lim2:
            vars=B[n-1][:32]+[alpha_12_p[n]]
            cnf+=get_espresso_result_cnf("/Users/kurahararikuto/Documents/python/Kurahara_project/solver_func/espresso_K2_3g/alpha_3_p.txt",vars)
        else:
            vars=B[n-1][:8]+[alpha_12_p[n]]
            cnf+=get_espresso_result_cnf("/Users/kurahararikuto/Documents/python/Kurahara_project/solver_func/espresso_K2_3g/alpha_12_p_espresso.txt",vars)
        vars=B[n-1][32*8:32*9]+[alpha_3_p[n]]
        cnf+=get_espresso_result_cnf("/Users/kurahararikuto/Documents/python/Kurahara_project/solver_func/espresso_K2_3g/alpha_3_p.txt",vars)
        func_alpha_0(cnf,A[n-1][:8],alpha_0[n])
        func_alpha_12(cnf,B[n-1][:8],alpha_12[n],alpha_12_flag[n])
        func_alpha_3(cnf,B[n-1][32*8:32*8+8],alpha_3[n],alpha_3_flag[n])
        alpha_0_temp=A[n-1][8:32]+[d0 for _ in range(8)]
        alpha_12_temp=B[n-1][8:32]+[d0 for _ in range(8)]
        for i in range(24):
            vars=[alpha_3_flag[n]]+[B[n-1][32*8+i]]+[B[n-1][32*8+8+i]]+[alpha_3_temp[n][i]]
            cnf+=(get_espresso_result_cnf("/Users/kurahararikuto/Documents/python/Kurahara_project/solver_func/espresso_K2_3g/shift8_espresso.txt",vars))
        for i in range(8):
            vars=[alpha_3_flag[n]]+[B[n-1][24+32*8+i]]+[d0]+[alpha_3_temp[n][24+i]]
            cnf+=(get_espresso_result_cnf("/Users/kurahararikuto/Documents/python/Kurahara_project/solver_func/espresso_K2_3g/shift8_espresso.txt",vars))
        for i in range(32):
            vars=[alpha_0[n][i]]+[alpha_0_temp[i]]+[A[n-1][32*3+i]]+[z_l[n][i]]+[A[n][32*4+i]]
            cnf+=(get_espresso_result_cnf("solver_func/espresso/xor_4bit_espresso.txt",vars))
            vars=[alpha_12[n][i]]+[alpha_12_temp[i]]+[B[n-1][32*1+i]]+[B[n-1][32*6+i]]+[alpha_3[n][i]]+[alpha_3_temp[n][i]]+[z_h[n][i]]+[B[n][32*10+i]]
            cnf+=(get_espresso_result_cnf("solver_func/espresso/xor_7bit_espresso.txt",vars))

    def K2_DCP(self):
        start = time.perf_counter()
        total = time.perf_counter()
        if self.lim:
            print("lim")
        if self.lim2:
            print("lim2")
        if self.key:
            print("key")
        while self.weight< self.upper:
            cnfpath,logpath,logpath2,logpath3=self.make_file()
            d0=1
            A=[[d0 for _ in range(32*5)]for _ in range(self.max_round+1)]
            B=[[d0 for _ in range(32*11)]for _ in range(self.max_round+1)]
            R1=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            R2=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            L1=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            L2=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            R1_sboxed=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            R2_sboxed=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            L1_sboxed=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            L2_sboxed=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            R1_xor_temp=[[d0 for _ in range(60)]for _ in range(self.max_round+1)]
            R2_xor_temp=[[d0 for _ in range(60)]for _ in range(self.max_round+1)]
            L1_xor_temp=[[d0 for _ in range(60)]for _ in range(self.max_round+1)]
            L2_xor_temp=[[d0 for _ in range(60)]for _ in range(self.max_round+1)]
            R1_prob=[[d0 for _ in range(4*7)]for _ in range(self.max_round+1)]
            R2_prob=[[d0 for _ in range(4*7)]for _ in range(self.max_round+1)]
            L1_prob=[[d0 for _ in range(4*7)]for _ in range(self.max_round+1)]
            L2_prob=[[d0 for _ in range(4*7)]for _ in range(self.max_round+1)]
            L2B9=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            L2B10=[[d0 for _ in range(32)]for _ in range(self.max_round+2)]
            R2B4=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            R2B0=[[d0 for _ in range(32)]for _ in range(self.max_round+2)]
            L2B9_w=[[d0 for _ in range(31)]for _ in range(self.max_round+1)]
            L2B10_w=[[d0 for _ in range(31)]for _ in range(self.max_round+2)]
            R2B4_w=[[d0 for _ in range(31)]for _ in range(self.max_round+1)]
            R2B0_w=[[d0 for _ in range(31)]for _ in range(self.max_round+2)]
            alpha_0=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            alpha_12=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            alpha_3=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            alpha_3_temp=[[d0 for _ in range(32)]for _ in range(self.max_round+1)]
            alpha_12_flag=[d0 for _ in range(self.max_round+1)]
            alpha_3_flag=[d0 for _ in range(self.max_round+1)]
            alpha_12_p=[d0 for _ in range(self.max_round+1)]
            alpha_3_p=[d0 for _ in range(self.max_round+1)]
            flag_p=[[d0 for _ in range(2)]for _ in range(self.max_round+1)]
            z_l=[[d0 for _ in range(32)]for _ in range(self.max_round+2)]
            z_h=[[d0 for _ in range(32)]for _ in range(self.max_round+2)]
            if self.key:
                d1=2
                num=3
                K=[i for i in range(num,num+32*12)]
                num+=32*12
                K_temp=[i for i in range(num,num+32*2)]
                num+=32*2
                K_sboxed=[i for i in range(num,num+32*2)]
                num+=32*2
                K_xor_temp=[i for i in range(num,num+60*2)]
                num+=60*2
                K_prob=[i for i in range(num,num+7*4*2)]
                num+=7*4*2
                for i in range(5):
                    A[0][32*(4-i):32*(4-i)+32]=K[32*i:32*i+32]
                B[0][:32*2]=K[32*10:]
                B[0][32*4:32*6]=K[32*8:32*10]
                B[0][32*8:32*9]=K[32*7:32*8]
                B[0][32*9:]=K[32*5:32*7]
                # print(num)
            cnf=[]
            num=self.block_init(A,B,R1,R2,L1,L2,R1_sboxed,R2_sboxed,L1_sboxed,L2_sboxed,R1_xor_temp,R2_xor_temp,L1_xor_temp,L2_xor_temp,R1_prob,R2_prob,L1_prob,L2_prob,L2B9,L2B10,R2B4,R2B0,L2B9_w,L2B10_w,R2B4_w,R2B0_w,alpha_0,alpha_12,alpha_3,alpha_3_temp,alpha_12_flag,alpha_3_flag,alpha_12_p,alpha_3_p,flag_p,z_l,z_h)
            cnf+=[[-1]]
            if self.key:
                cnf+=[B[0][32*2:32*4]+B[0][32*6:32*8]+K]
                # cnf+=[K]
                self.gen_key(cnf,d0,d1,K,K_temp,K_sboxed,K_prob,K_xor_temp)
            else:
                cnf+=[B[0][32*2:32*4]+B[0][32*6:32*8]]
            if self.lim2:
                for n in range(5,self.max_round+1):
                    flag_p[n]=[i for i in range(num,num+2)]
                    num+=2
            if self.lim:
                iv=B[0][32*2:32*4]+B[0][32*6:32*8]
                for i in iv:
                    if i==B[0][32*3+8]:
                        cnf+=[[i]]
                    else:
                        cnf+=[[-i]]
            for n in range(1, self.max_round+1):
                cnf+=[[-A[n][64]]]
                cnf+=[[-A[n][65]]]
                if n>5 and not self.key:
                    cnf+=[[flag_p[n][0]]]
                    cnf+=[[flag_p[n][1]]]
                elif n>3 and self.key:
                    cnf+=[[flag_p[n][0]]]
                    cnf+=[[flag_p[n][1]]]
                addition(cnf,B[n-1][:32],R2[n-1],R2B0[n],R2B0_w[n])
                addition(cnf,B[n-1][32*10:],L2[n-1],L2B10[n],L2B10_w[n])
                for i in range(32):
                    vars=[R2B0[n][i],R1[n-1][i],A[n-1][32*4+i],z_l[n][i]]
                    cnf+=(get_espresso_result_cnf("./snow/espresso/xor_3bit_espresso.txt",vars))
                    vars=[L2B10[n][i],L1[n-1][i],A[n-1][i],z_h[n][i]]
                    cnf+=(get_espresso_result_cnf("./snow/espresso/xor_3bit_espresso.txt",vars))
                self.NLF_update(cnf,B,R1,R2,L1,L2,R1_sboxed,R2_sboxed,L1_sboxed,L2_sboxed,R1_xor_temp,R2_xor_temp,L1_xor_temp,L2_xor_temp,R1_prob,R2_prob,L1_prob,L2_prob,L2B9,R2B4,L2B9_w,R2B4_w,n)
                self.DFC_update(cnf,d0,A,B,alpha_0,alpha_12,alpha_3,alpha_3_temp,alpha_12_flag,alpha_3_flag,alpha_12_p,alpha_3_p,z_l,z_h,n)
            addition(cnf,B[self.max_round][:32],R2[self.max_round],R2B0[self.max_round+1],R2B0_w[self.max_round+1])
            addition(cnf,B[self.max_round][32*10:],L2[self.max_round],L2B10[self.max_round+1],L2B10_w[self.max_round+1])
            for i in range(32):
                vars=[R2B0[self.max_round+1][i],R1[self.max_round][i],A[self.max_round][32*4+i],z_l[self.max_round+1][i]]
                cnf+=(get_espresso_result_cnf("./snow/espresso/xor_3bit_espresso.txt",vars))
                vars=[L2B10[self.max_round+1][i],L1[self.max_round][i],A[self.max_round][i],z_h[self.max_round+1][i]]
                cnf+=(get_espresso_result_cnf("./snow/espresso/xor_3bit_espresso.txt",vars))
            prob=[]
            if self.key:
                prob.extend(K_prob)
            for n in range(1,self.max_round+1):
                prob.extend(L2_prob[n])
                prob.extend(R2_prob[n])
                prob.extend(L2B10_w[n])
                prob.extend(R2B0_w[n])
                prob.extend(L1_prob[n])
                prob.extend(R1_prob[n])
                prob.extend(L2B9_w[n])
                prob.extend(R2B4_w[n])
                prob.extend([alpha_12_p[n]])
                prob.extend([alpha_3_p[n]])
                # prob.extend(flag_p[n])
            prob.extend(L2B10_w[self.max_round+1])
            prob.extend(R2B0_w[self.max_round+1])
            encode = CardEnc.atmost(lits = prob,bound = self.weight,top_id = num-1,encoding = 6)
            cnf+=encode
            snowv_cnf = CNF(from_clauses = cnf)
            snowv_cnf.to_file(cnfpath)
            
            s = solver_func.solver.Solver(cnfpath,logpath)
            s.kissat_MAB_HyWalk()
            result = s.CheckResult()
            iv=[B[0][32*2:32*4]+B[0][32*6:32*8]]
            if self.key:
                K=[K]
                K_prob=[K_prob]
            LR=[]
            for round in range(self.max_round+1):
                LR.append(L2[round]+L1[round]+R2[round]+R1[round])

            if result == True:
                solution = solver_func.extract_solution.Extract_Solution(logpath)
                # print(solution)
                with open(logpath,"w") as f:
                    solver_func.update_logfile.Update_LogFile(f,solution,iv,0,IV_SIZE,"IV",32)
                    if self.key:
                        solver_func.update_logfile.Update_LogFile(f,solution,K,0,32*4,"IK",32)
                    f.write("==============================================================================================\n")
                    if self.key:
                        solver_func.update_logfile.Update_LogFile(f,solution,K_prob,0,7*8,"K_prob",7)
                    for r in range(1,self.max_round+1):
                        f.write("\n")
                        solver_func.update_logfile.Update_LogFile(f,solution,L2B9,r,BIT_SIZE,"R1_Sin",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,R1,r,BIT_SIZE,"R1_Sout",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,R1_prob,r,PROB_NUM,"R1_prob",7)
                        f.write("\n")
                        solver_func.update_logfile.Update_LogFile(f,solution,R1,r-1,BIT_SIZE,"R2_Sin",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,R2,r,BIT_SIZE,"R2_Sout",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,R2_prob,r,PROB_NUM,"R2_prob",7)
                        f.write("\n")
                        solver_func.update_logfile.Update_LogFile(f,solution,R2B4,r,BIT_SIZE,"L1_Sin",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,L1,r,BIT_SIZE,"L1_Sout",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,L1_prob,r,PROB_NUM,"L1_prob",7)
                        f.write("\n")
                        solver_func.update_logfile.Update_LogFile(f,solution,L1,r-1,BIT_SIZE,"L2_Sin",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,L2,r,BIT_SIZE,"L2_Sout",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,L2_prob,r,PROB_NUM,"L2_prob",7)
                        f.write("\n")
                        solver_func.update_logfile.Update_LogFile(f,solution,L2B10_w,r,31,"L2B10_w",31)
                        solver_func.update_logfile.Update_LogFile(f,solution,R2B0_w,r,31,"R2B0_w",31)
                        solver_func.update_logfile.Update_LogFile(f,solution,L2B9_w,r,31,"L2B9_w",31)
                        solver_func.update_logfile.Update_LogFile(f,solution,R2B4_w,r,31,"R2B4_w",31)
                        solver_func.update_logfile.Update_LogFile_cell(f,solution,alpha_12_p,r,"al12_p")
                        solver_func.update_logfile.Update_LogFile_cell(f,solution,alpha_3_p,r,"al3_p")
                        solver_func.update_logfile.Update_LogFile(f,solution,flag_p,r,2,"flag_p",2)
                        f.write("==============================================================================================\n")
                    solver_func.update_logfile.Update_LogFile(f,solution,L2B10_w,self.max_round+1,31,"L2B10_w",31)
                    solver_func.update_logfile.Update_LogFile(f,solution,R2B0_w,self.max_round+1,31,"R2B0_w",31)
                with open(logpath2,"w") as f:
                    solver_func.update_logfile.Update_LogFile(f,solution,iv,0,IV_SIZE,"iv",32)
                    if self.key:
                        solver_func.update_logfile.Update_LogFile(f,solution,K,0,32*4,"IK",32)
                    f.write("==============================================================================================\n")
                    for r in range(self.max_round+1):
                        solver_func.update_logfile.Update_LogFile(f,solution,A,r,A_SIZE,"A",32)
                        solver_func.update_logfile.Update_LogFile_inv(f,solution,B,r,B_SIZE,"B",32)
                        solver_func.update_logfile.Update_LogFile(f,solution,LR,r,32*4,"L2L1R2R1",32)
                        solver_func.update_logfile.Update_LogFile(f,solution,L2B10,r,32,"L2+B10",32)
                        solver_func.update_logfile.Update_LogFile(f,solution,z_h,r,32,"z_h",32)
                        solver_func.update_logfile.Update_LogFile(f,solution,z_l,r,32,"z_l",32)
                        f.write("\n")
                        solver_func.update_logfile.Update_LogFile_part(f,solution,A[r][:32],r,0,32,"A")
                        solver_func.update_logfile.Update_LogFile(f,solution,alpha_12,r,32,"al0",8)
                        solver_func.update_logfile.Update_LogFile_part(f,solution,A[r-1][8:32]+[d0 for _ in range(8)],r,0,32,"A<<8")
                        solver_func.update_logfile.Update_LogFile_part(f,solution,A[r-1][32*3:32*4],r,3,32,"A")
                        solver_func.update_logfile.Update_LogFile(f,solution,z_l,r,32,"z_l",8)
                        solver_func.update_logfile.Update_LogFile_part(f,solution,A[r][32*4:],r,4,32,"A")
                        f.write("\n")
                        solver_func.update_logfile.Update_LogFile_part(f,solution,B[r-1][:32],r-1,0,32,"B")
                        solver_func.update_logfile.Update_LogFile(f,solution,alpha_12,r,32,"al12",8)
                        solver_func.update_logfile.Update_LogFile_part(f,solution,B[r-1][8:32]+[d0 for _ in range(8)],r-1,0,32,"B<<8")
                        solver_func.update_logfile.Update_LogFile_part(f,solution,B[r-1][32*1:32*2],r-1,1,32,"B")
                        solver_func.update_logfile.Update_LogFile_part(f,solution,B[r-1][32*6:32*7],r-1,6,32,"B")
                        solver_func.update_logfile.Update_LogFile_part(f,solution,B[r-1][32*8:32*9],r-1,8,32,"B")
                        solver_func.update_logfile.Update_LogFile(f,solution,alpha_3,r,32,"al3",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,alpha_3_temp,r,32,"al3_temp",8)             
                        solver_func.update_logfile.Update_LogFile(f,solution,z_h,r,32,"z_h",8)
                        solver_func.update_logfile.Update_LogFile_part(f,solution,B[r][32*10:],r,10,32,"B")
                        solver_func.update_logfile.Update_LogFile_cell(f,solution,alpha_12_flag,r,"al12_flag")
                        solver_func.update_logfile.Update_LogFile_cell(f,solution,alpha_3_flag,r,"al3_flag")
                        f.write("==============================================================================================\n")
                    solver_func.update_logfile.Update_LogFile(f,solution,z_h,self.max_round+1,32,"z_h",32)
                    solver_func.update_logfile.Update_LogFile(f,solution,z_l,self.max_round+1,32,"z_l",32)
                with open(logpath3,"w") as f:
                    for r in range(1,self.max_round+1):
                        solver_func.update_logfile.Update_LogFile(f,solution,L2,r-1,32,"L2",8)
                        solver_func.update_logfile.Update_LogFile_part(f,solution,B[r-1][32*10:],r-1,10,32,"B")
                        solver_func.update_logfile.Update_LogFile(f,solution,L2B10,r,32,"L2+B10",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,L2B10_w,r,31,"L2B10_w",31)
                        f.write("\n")
                        solver_func.update_logfile.Update_LogFile(f,solution,L2,r-1,32,"L2",8)
                        solver_func.update_logfile.Update_LogFile_part(f,solution,B[r-1][32*9:32*10],r-1,9,32,"B")
                        solver_func.update_logfile.Update_LogFile(f,solution,L2B9,r,32,"L2+B9",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,L2B9_w,r,31,"L2B9_w",31)
                        f.write("\n")
                        solver_func.update_logfile.Update_LogFile(f,solution,R2,r-1,32,"R2",8)
                        solver_func.update_logfile.Update_LogFile_part(f,solution,B[r-1][:32*1],r-1,0,32,"B")
                        solver_func.update_logfile.Update_LogFile(f,solution,R2B0,r,32,"R2+B0",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,R2B0_w,r,31,"R2B0_w",31)
                        f.write("\n")
                        solver_func.update_logfile.Update_LogFile(f,solution,R2,r-1,32,"R2",8)
                        solver_func.update_logfile.Update_LogFile_part(f,solution,B[r-1][32*4:32*5],r-1,4,32,"B")
                        solver_func.update_logfile.Update_LogFile(f,solution,R2B4,r,32,"R2+B4",8)
                        solver_func.update_logfile.Update_LogFile(f,solution,R2B4_w,r,31,"R2B4_w",31)
                        f.write("==============================================================================================\n")
                    solver_func.update_logfile.Update_LogFile(f,solution,L2,self.max_round,32,"L2",8)
                    solver_func.update_logfile.Update_LogFile_part(f,solution,B[self.max_round][32*10:],self.max_round,10,32,"B")
                    solver_func.update_logfile.Update_LogFile(f,solution,L2B10,self.max_round+1,32,"L2+B10",8)
                    solver_func.update_logfile.Update_LogFile(f,solution,L2B10_w,self.max_round+1,31,"L2B10_w",31)
                    f.write("\n")
                    solver_func.update_logfile.Update_LogFile(f,solution,R2,self.max_round,32,"R2",8)
                    solver_func.update_logfile.Update_LogFile_part(f,solution,B[self.max_round][:32*1],self.max_round,0,32,"B")
                    solver_func.update_logfile.Update_LogFile(f,solution,R2B0,self.max_round+1,32,"R2+B0",8)
                    solver_func.update_logfile.Update_LogFile(f,solution,R2B0_w,self.max_round+1,31,"R2B0_w",31)
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


max_round = 6
weight    = 48
upper     = 100
up        = 1
lim       = 0
lim2      = 0  
key       = 0
s=K2_DCP(max_round,weight,upper,up,lim,lim2,key)
s.K2_DCP()
