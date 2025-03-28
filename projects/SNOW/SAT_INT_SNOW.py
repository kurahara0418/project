import sys
sys.path.append('Kurahara_project')

from pysat.card import *
from pysat.formula import CNF
# from solver_func.integral_cnf import *
from solver_func.append_cnf import *
from solver_func.integral_cnf import *
import itertools 
import time
import solver_func.solver
import solver_func.extract_solution
import solver_func.update_logfile

Sigma=[15,11,7,3,14,10,6,2,13,9,5,1,12,8,4,0]

def permute(R,T):
    # print(T)
    R_temp = []
    for i in range(16):
        for j in range(8):
            R_temp.append(T[Sigma[i]*8+j])
    R.append(R_temp)

def R_convert(R):
    #R[3210,7654,89ba,fedc] -> R_temp[0123,4567,89sb,cdef]
    R_temp = []
    # for i in range(4):
    #     for j in range(4):
    #         cell = i*32+(3-j)*8
    #         R_temp.extend(R[cell:cell+8])
    for i in range(16):
        cell = (15-i)*8
        R_temp.extend(R[cell:cell+8])
    return R_temp

class SNOWV_INTEGRAL:
    def __init__(self,max_round,start):
        self.max_round = max_round
        self.start = start

    def block_init(self,max_round,A,B,T1,T2,R1,R2,R3,R1_copy,R2_copy,z):
        num = 2
        #初期値
        A[0].extend([[],[],[1 for _ in range(128)] + [_ for _ in range(num,num+128)]])
        num += 128
        B[0].extend([[],[1 for _ in range(256)]])
        R1_copy[0].extend([[1 for _ in range(128)],[1 for _ in range(128)]])
        R2_copy[0].extend([[1 for _ in range(128)],[1 for _ in range(128)],[1 for _ in range(128)]])
        R3[0].extend([1 for _ in range(128)])
        z[0].extend([1 for _ in range(128)])
        #ラウンド
        for round in range(1, self.max_round+1):
            A[round].append(A[round-1][2][:128] + [_ for _ in range(num,num+128)])   #copy
            num += 128
            A[round].append([_ for _ in range(num,num+256)])   #LFSR後
            num += 256
            A[round].append([_ for _ in range(num,num+128)] + A[round][1][128:])   #zとのXOR後
            num += 128
            B[round].append( [_ for _ in range(num,num+128)] + B[round-1][1][:128])    #copy
            num += 128
            B[round].append([_ for _ in range(num,num+256)])   #LFSR後
            num += 256
            T1[round].append([_ for _ in range(num,num+128)]) #copy
            num += 128
            T1[round].append([_ for _ in range(num,num+128)]) #Additionの結果
            num += 128
            T2[round].append([_ for _ in range(num,num+128)]) #copy
            num += 128
            T2[round].append([_ for _ in range(num,num+128)]) #XORの結果
            num += 128
            T2[round].append([_ for _ in range(num,num+128)]) #Additionの結果
            num += 128
            permute(R1[round],T2[round][2])                 #permute済み
            R2[round].extend([_ for _ in range(num,num+128)])
            num += 128
            R3[round].extend([_ for _ in range(num,num+128)]) 
            num += 128
            for i in range(2):
                R1_copy[round].append([_ for _ in range(num,num+128)]) #上,右
                num += 128
            for i in range(3):
                R2_copy[round].append([_ for _ in range(num,num+128)]) #上,右,下
                num += 128
            z[round].extend([_ for _ in range(num,num+128)])
            num += 128
        A[self.max_round+1].append(A[self.max_round+1-1][2][:128] + [_ for _ in range(num,num+128)])   #copy
        num += 128
        A[self.max_round+1].append([_ for _ in range(num,num+256)])   #LFSR後
        num += 256
        B[self.max_round+1].append( [_ for _ in range(num,num+128)] + B[self.max_round][1][:128])    #copy
        num += 128
        B[self.max_round+1].append([_ for _ in range(num,num+256)])   #LFSR後
        num += 256
        T1[self.max_round+1].append([_ for _ in range(num,num+128)]) #copy
        num += 128
        T1[self.max_round+1].append([_ for _ in range(num,num+128)]) #Additionの結果
        num += 128
        T2[self.max_round+1].append([_ for _ in range(num,num+128)]) #copy
        num += 128
        T2[self.max_round+1].append([_ for _ in range(num,num+128)]) #XORの結果
        num += 128
        T2[self.max_round+1].append([1 for _ in range(num,num+128)]) #Additionの結果
        permute(R1[self.max_round+1],T2[self.max_round+1][2])                 #permute済み
        R2[self.max_round+1].extend([1 for _ in range(num,num+128)])
        R3[self.max_round+1].extend([1 for _ in range(num,num+128)]) 
        z[self.max_round+1].extend([_ for _ in range(num,num+128)])
        num += 128
        # for i in range(2):
        #     R1_copy[max_round+1].append([_ for _ in range(num,num+128)]) #上,右
        #     num += 128
        # for i in range(3):
        #     R2_copy[max_round+1].append([_ for _ in range(num,num+128)]) #上,右,下
        #     num += 128
        # B[max_round+1].append([_ for _ in range(num,num+128)] + B[max_round][1][128:])    #copy
        # num += 128
        # T1[max_round+1].append([_ for _ in range(num,num+128)]) #copy
        # num += 128
        # T1[max_round+1].append([_ for _ in range(num,num+128)])
        # num += 128
        # z[max_round+1].extend([_ for _ in range(num,num+128)])
        # num += 128
        return num

    def integral_init(self,cnf,IV,z_key,in_row,out_row):
        # print(z_key)
        inp = IV
        # print(IV)
        for bit in range(128):
            if bit == in_row:
                cnf.append([-inp[bit]])
            else:
                cnf.append([inp[bit]])
        out = z_key
        for bit in range(128):
            if bit == out_row:
                cnf.append([out[bit]])
            else:
                cnf.append([-out[bit]])

    def Copy_RT(self,cnf,round,max_round,A,B,T1,T2,R1,R2,R1_copy,R2_copy):
        solver_func.integral_cnf.Copy2_array(cnf,B[round-1][1][:128],B[round][0][:128],T1[round][0])
        solver_func.integral_cnf.Copy2_array(cnf,A[round-1][2][128:],A[round][0][128:],T2[round][0])
        if round != self.max_round+1:
            solver_func.integral_cnf.Copy2_array(cnf,R1[round][0],R1_copy[round][0],R1_copy[round][1])
            solver_func.integral_cnf.Copy3_array(cnf,R2[round],R2_copy[round][0],R2_copy[round][1],R2_copy[round][2])

    def Copy_LFSR(self,cnf,num,A_in,B_in):
        #copy変数の用意
        a0_copy = []
        a1_copy = []
        a8_copy = []
        b0_copy = []
        b3_copy = []
        b8_copy = []
        for i in range(2):
            a0_copy.append([])
            a1_copy.append([])
            a8_copy.append([])
            b0_copy.append([])
            b3_copy.append([])
            b8_copy.append([])
            for j in range(8):
                a0_copy[i].append([_ for _ in range(num,num+16)])
                num+=16
                a1_copy[i].append([_ for _ in range(num,num+16)])
                num+=16
                a8_copy[i].append([_ for _ in range(num,num+16)])
                num+=16
                b0_copy[i].append([_ for _ in range(num,num+16)])
                num+=16
                b3_copy[i].append([_ for _ in range(num,num+16)])
                num+=16
                b8_copy[i].append([_ for _ in range(num,num+16)])
                num+=16
        #Copy
        a0_root = A_in[15:] + a1_copy[1][:7]
        a1_root = list(reversed(A_in[8:15]))+ a8_copy[1][:1]
        a8_root = list(reversed(A_in[:8]))
        b0_root = list(reversed(B_in[13:])) + b3_copy[1][:5]
        b3_root = list(reversed(B_in[8:13]))+ b8_copy[1][:3]
        b8_root = list(reversed(B_in[:8]))
        # print( A_in[15:])
        # print(a1_copy[1][:7])
        # print(a1_root)
        # print(a0_copy)
        for t in range(8):
            # print(a1_root[t])
            # print(a1_copy[0][t])
            # print(a1_copy[1][t])
            solver_func.integral_cnf.Copy2_array(cnf,a0_root[t],a0_copy[0][t],a0_copy[1][t])
            # print("コピー前", len(cnf))
            solver_func.integral_cnf.Copy2_array(cnf,a1_root[t],a1_copy[0][t],a1_copy[1][t])
            # print("コピー後", len(cnf))
            # print("コピー後", cnf[-1])
            solver_func.integral_cnf.Copy2_array(cnf,a8_root[t],a8_copy[0][t],a8_copy[1][t])
            solver_func.integral_cnf.Copy2_array(cnf,b0_root[t],b0_copy[0][t],b0_copy[1][t])
            solver_func.integral_cnf.Copy2_array(cnf,b3_root[t],b3_copy[0][t],b3_copy[1][t])
            solver_func.integral_cnf.Copy2_array(cnf,b8_root[t],b8_copy[0][t],b8_copy[1][t])
        return num,a0_copy,a1_copy,a8_copy,b0_copy,b3_copy,b8_copy

    def LFSR_update(self,cnf,num,round,A,B):
        A_in = []
        B_in = []
        A_out = []
        B_out = []
        for i in range(16):
            A_in.append(A[round][0][i*16:i*16+16])
            B_in.append(B[round][0][i*16:i*16+16])
        num,a0_copy,a1_copy,a8_copy,b0_copy,b3_copy,b8_copy = self.Copy_LFSR(cnf,num,A_in,B_in)
        A_out = [[_ for _ in range(num+i*16,num+(i+1)*16)]for i in range(8)] + list(reversed(a8_copy[1][1:])) + a1_copy[1][7:] 
        num += 128
        B_out = [[_ for _ in range(num+i*16,num+(i+1)*16)]for i in range(8)] + list(reversed(b8_copy[1][3:])) + list(reversed(b3_copy[1][5:]))
        num += 128
        A_mul = [[] for _ in range(8)]
        B_mul = [[] for _ in range(8)]
        A_mul_inv = [[] for _ in range(8)]
        B_mul_inv = [[] for _ in range(8)]
        for t in range(8):
            rp=[1,0,0,1,1,0,0,1,0,0,0,0,1,1,1,1]
            num,A_mul[t] = self.x_mul(cnf,num,a0_copy[0][t],rp)
            rp=[1,1,0,0,1,0,0,1,0,1,1,0,0,0,1,1]
            num,B_mul[t] = self.x_mul(cnf,num,b0_copy[0][t],rp)
            rp=[1,1,0,0,1,1,0,0,1,0,0,0,0,1,1,1]
            num,A_mul_inv[t] = self.x_mul_inv(cnf,num,a8_copy[0][t],rp)
            rp=[1,1,1,0,0,1,0,0,1,0,1,1,0,0,0,1]
            num,B_mul_inv[t] = self.x_mul_inv(cnf,num,b8_copy[0][t],rp)
        for t in range(8):
            solver_func.integral_cnf.XOR_4bit_array(cnf,A_mul[t],A_mul_inv[t],a1_copy[0][t],b0_copy[1][t],A_out[7-t])
            solver_func.integral_cnf.XOR_4bit_array(cnf,B_mul[t],B_mul_inv[t],b3_copy[0][t],a0_copy[1][t],B_out[7-t])
        A_out = list(itertools.chain.from_iterable(A_out))
        B_out = list(itertools.chain.from_iterable(B_out))
        # print(len(B_out))
        for bit in range(256):
            vars = [A[round][1][bit]] + [A_out[bit]]
            cnf.extend(get_espresso_result_cnf("solver_func/espresso/equal_espresso.txt",vars))
            vars = [B[round][1][bit]] + [B_out[bit]]
            cnf.extend(get_espresso_result_cnf("solver_func/espresso/equal_espresso.txt",vars))
        # A[round].append(list(itertools.chain.from_iterable(A_out)))
        # B[round].append(list(itertools.chain.from_iterable(B_out)))
        return num,a0_copy,a1_copy,a8_copy,b0_copy,b3_copy,b8_copy,A_mul,B_mul,A_mul_inv,B_mul_inv, A_out, B_out

    def x_mul(self,cnf,num,Input,rp):
        Out = []
        copy = [_ for _ in range(num,num+8)]
        num += 8
        solver_func.integral_cnf.Copy8(cnf,Input[0],copy[0],copy[1],copy[2],copy[3],copy[4],copy[5],copy[6],copy[7])
        cnt = 0
        for bit in range(15):
            if rp[bit]:
                Out.append(num)
                num += 1
                solver_func.integral_cnf.XOR_2bit(cnf,Input[bit+1],copy[cnt],Out[bit])
                cnt += 1
            else:
                Out.append(Input[bit+1])
        Out.append(copy[7])
        # print(len(Out))
        # print(cnt)
        return num,Out

    def x_mul_inv(self,cnf,num,Input,rp):
        Out = []
        copy = [_ for _ in range(num,num+8)]
        num += 8
        solver_func.integral_cnf.Copy8(cnf,Input[15],copy[0],copy[1],copy[2],copy[3],copy[4],copy[5],copy[6],copy[7])
        cnt = 0
        Out.append(copy[7])
        for bit in range(1,16):
            if rp[bit]:
                Out.append(num)
                num += 1
                solver_func.integral_cnf.XOR_2bit(cnf,Input[bit-1],copy[cnt],Out[bit])
                cnt += 1
            else:
                Out.append(Input[bit-1])
        # print(cnt)
        return num,Out

    def Addition32_4(self,cnf,num,R,T,Out):
        for i in range(4):
            cell = i*32
            num = solver_func.integral_cnf.ADDITION(cnf,num,R[cell:cell+32],T[cell:cell+32],Out[cell:cell+32])
        return num
    
    def aes(self,cnf,num,R_in,R_out):
        shifted = []
        Sin = R_convert(R_in)
        Sout = [_ for _ in range(num,num+128)]
        num += 128
        R_out_temp = R_convert(R_out)
        for i in range(16):
            cell = i*8
            vars = Sin[cell:cell+8]+Sout[cell:cell+8]
            cnf.extend((get_espresso_result_cnf("solver_func/espresso/integral/AES_sbox_espresso.txt",vars)))
        for i in range(4):
                for j in range(4):
                    shifted.extend(Sout[((i+j)%4)*32+(j*8):((i+j)%4)*32+(j+1)*8])
        for i in range(4):
            block = 32*i
            num =  solver_func.integral_cnf.XOR_92(cnf,num,shifted[block:block+32],R_out_temp[block:block+32])
        return num

    def FSM_update(self,cnf,num,round,T2,R1_copy,R2_copy,R2,R3):
        solver_func.integral_cnf.XOR_2bit_array(cnf,R3[round-1],T2[round][0],T2[round][1])
        num = self.Addition32_4(cnf,num,R2_copy[round-1][2],T2[round][1],T2[round][2])
        num = self.aes(cnf,num,R1_copy[round-1][1],R2[round])
        num = self.aes(cnf,num,R2_copy[round-1][1],R3[round])
        return num

    def snowv_integral(self):
        cnfpath =  "Kurahara_project/projects/SNOW/SNOWV/int_cnffile/R{}.cnf".format(self.max_round)
        logpath =  "Kurahara_project/projects/SNOW/SNOWV/int_logfile/R{}.txt".format(self.max_round)
        logpath2 = "Kurahara_project/projects/SNOW/SNOWV/int_logfile/LFSR_R{}.txt".format(self.max_round)
        A = [[]for _ in range(self.max_round+2)]
        B = [[]for _ in range(self.max_round+2)]
        A_out = [[]for _ in range(self.max_round+2)]
        B_out = [[]for _ in range(self.max_round+2)]
        a0_copy = [[]for _ in range(self.max_round+2)]
        a1_copy = [[]for _ in range(self.max_round+2)]
        a8_copy = [[]for _ in range(self.max_round+2)]
        b0_copy = [[]for _ in range(self.max_round+2)]
        b3_copy = [[]for _ in range(self.max_round+2)]
        b8_copy = [[]for _ in range(self.max_round+2)]
        A_mul = [[]for _ in range(self.max_round+2)]
        B_mul = [[]for _ in range(self.max_round+2)]
        A_mul_inv = [[]for _ in range(self.max_round+2)]
        B_mul_inv = [[]for _ in range(self.max_round+2)]
        T1 = [[]for _ in range(self.max_round+2)]
        T2 = [[]for _ in range(self.max_round+2)]
        R1 = [[]for _ in range(self.max_round+2)]
        R2 = [[]for _ in range(self.max_round+2)]
        R3 = [[]for _ in range(self.max_round+2)]
        R1_copy = [[]for _ in range(self.max_round+2)]
        R2_copy = [[]for _ in range(self.max_round+2)]
        z = [[]for _ in range(self.max_round+2)]
        cnf=[]
        num_temp = self.block_init(self.max_round,A,B,T1,T2,R1,R2,R3,R1_copy,R2_copy,z)
        end = self.start+10
        if end > 128:
            end = 128
        # for in_row in range(128):
        # for in_row in range(1):
        for in_row in range(self.start,end):
            balance_flag = 0
            for out_row in range(128):
            # for out_row in range(60,61):
                sat_flag = 0
                cnf = []
                num = num_temp
                IV = A[0][2][128:]
                z_key = z[self.max_round+1]
                self.integral_init(cnf,IV,z_key,in_row,out_row)
                cnf.append([-1])
                for a in A[self.max_round+1][1]:
                    cnf.append([-a])
                for b in B[self.max_round+1][1]:
                    cnf.append([-b])
                # print
                for round in range(1,self.max_round+2):
                    self.Copy_RT(cnf,round,self.max_round,A,B,T1,T2,R1,R2,R1_copy,R2_copy)
                    num = self.Addition32_4(cnf,num,R1_copy[round-1][0],T1[round][0],T1[round][1])
                    solver_func.integral_cnf.XOR_2bit_array(cnf,R2_copy[round-1][0],T1[round][1],z[round])
                    num = self.FSM_update(cnf,num,round,T2,R1_copy,R2_copy,R2,R3)
                    num,a0_copy[round],a1_copy[round],a8_copy[round],b0_copy[round],b3_copy[round],b8_copy[round],A_mul[round],B_mul[round],A_mul_inv[round],B_mul_inv[round], A_out[round], B_out[round] = self.LFSR_update(cnf,num,round,A,B)
                    if round != self.max_round +1:
                        solver_func.integral_cnf.XOR_2bit_array(cnf,z[round],A[round][1][:128],A[round][2][:128])

                aes_cnf = CNF(from_clauses = cnf)
                aes_cnf.to_file(cnfpath)
                s = solver_func.solver.Solver(cnfpath,logpath)
                s.kissat_sc2024()
                result = s.CheckResult()

                if result == True:
                    sat_flag += 1
                    solution = solver_func.extract_solution.Extract_Solution(logpath)
                    with open(logpath,"w") as f:
                        solver_func.update_logfile.Update_LogFile_single(f,solution,A[0][2][:16*8],128,"iv",8)
                        solver_func.update_logfile.Update_LogFile_single(f,solution,A[0][2],256,"A[0][2]",8)
                        solver_func.update_logfile.Update_LogFile_single(f,solution,B[0][1],256,"B[0][1]",8)
                        # solver_func.update_logfile.Update_LogFile_single(f,solution,R1[0],128,"R1",8)
                        # solver_func.update_logfile.Update_LogFile_single(f,solution,R2[0],128,"R2",8)
                        # solver_func.update_logfile.Update_LogFile_single(f,solution,R3[0],128,"R3",8)
                        f.write("==============================================================================================\n")
                        for r in range(1,self.max_round+2):
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,A[r][i],256,"A[{}][{}]".format(r,i),8)
                            if r != self.max_round+1:
                                solver_func.update_logfile.Update_LogFile_single(f,solution,A[r][2],256,"A[{}][2]".format(r),8)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,B[r][i],256,"B[{}][{}]".format(r,i),8)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,T1[r][i],128,"T1[{}][{}]".format(r,i),8)
                            for i in range(3):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,T2[r][i],128,"T2[{}][{}]".format(r,i),8)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,R1[r][0],128,"R1",8)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,R2[r],128,"R2",8)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,R3[r],128,"R3",8)
                            if r != self.max_round+1:
                                for i in range(2):
                                    solver_func.update_logfile.Update_LogFile_single(f,solution,R1_copy[r][i],128,"R1_copy[{}][{}]".format(r,i),8)
                                for i in range(3):
                                    solver_func.update_logfile.Update_LogFile_single(f,solution,R2_copy[r][i],128,"R2_copy[{}][{}]".format(r,i),8)
                            # solver_func.update_logfile.Update_LogFile_single(f,solution,R2[r-1][0],128,"R2[r-1]",8)
                                f.write("\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,z[r],128,"z[{}]".format(r),8)
                            f.write("==============================================================================================\n")
                        # solver_func.update_logfile.Update_LogFile_single(f,solution,B[self.max_round+1][0][128:],128,"B[{}][0]".format(r),8)
                        # solver_func.update_logfile.Update_LogFile_single(f,solution,R1_copy[self.max_round][0],128,"R1_copy[{}][0]".format(self.max_round),8)
                        # for i in range(2):
                        #     solver_func.update_logfile.Update_LogFile_single(f,solution,T1[self.max_round+1][i],128,"T1[{}][{}]".format(self.max_round+1,i),8)
                        # solver_func.update_logfile.Update_LogFile_single(f,solution,z[self.max_round+1],128,"z",8)
                    with open(logpath2,"w") as f:
                        for r in range(1,self.max_round+2):
                            A_in = []
                            B_in = []
                            for i in range(16):
                                A_in.append(A[r][0][i*16:i*16+16])
                                B_in.append(B[r][0][i*16:i*16+16])
                            a0_root = A_in[15:] + a1_copy[r][1][:7]
                            a1_root = list(reversed(A_in[8:15]))+ a8_copy[r][1][:1]
                            a8_root = list(reversed(A_in[:8]))
                            b0_root = list(reversed(B_in[13:])) + b3_copy[r][1][:5]
                            b3_root = list(reversed(B_in[8:13]))+ b8_copy[r][1][:3]
                            b8_root = list(reversed(B_in[:8]))
                            solver_func.update_logfile.Update_LogFile_single(f,solution,A[r][0],256,"A[{}][0]".format(r),16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,B[r][0],256,"B[{}][0]".format(r),16)
                            # print(a0_copy[r])
                            # print(A_in[15:])
                            # print(a1_copy[round][1][:7])
                            # print(a1_root)
                            f.write("a0_root = A_in[15:] + a1_copy[r][1][:7]\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a0_root)),128,"a0_root".format(r),16)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a0_copy[r][i])),128,"a0_copy[{}]".format(i),16)
                            f.write("\n")
                            f.write("a1_root = list(reversed(A_in[8:15]))+ a8_copy[r][1][:1]\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a1_root)),128,"a1_root",16)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a1_copy[r][i])),128,"a1_copy[{}]".format(i),16)
                            f.write("\n")
                            f.write("a8_root = list(reversed(A_in[8:]))\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a8_root)),128,"a8_root",16)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a8_copy[r][i])),128,"a8_copy[{}]".format(i),16)
                            f.write("\n")
                            f.write("b0_root = list(reversed(B_in[13:])) + b3_copy[r][1][:5]\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b0_root)),128,"b0_root",16)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b0_copy[r][i])),128,"b0_copy[{}]".format(i),16)
                            f.write("\n")
                            f.write("b3_root = list(reversed(B_in[8:13]))+ b8_copy[r][1][:3]\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b3_root)),128,"b3_root",16)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b3_copy[r][i])),128,"b3_copy[{}]".format(i),16)
                            f.write("\n")
                            f.write("b8_root = list(reversed(B_in[:8]))\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b8_root)),128,"b8_root",16)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b8_copy[r][i])),128,"b8_copy[{}]".format(i),16)
                            f.write("\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a0_copy[r][0])),128,"a0_copy[0]",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(A_mul[r])),128,"A_mul",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a8_copy[r][0])),128,"a8_copy[0]",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(A_mul_inv[r])),128,"A_mul_inv",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b0_copy[r][0])),128,"b0_copy[0]",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(B_mul[r])),128,"B_mul",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b8_copy[r][0])),128,"b8_copy[0]",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(B_mul_inv[r])),128,"B_mul_inv",16)
                            f.write("\n")
                            # solver_func.integral_cnf.XOR_4bit_array(cnf,A_mul[t],A_mul_inv[t],a1_copy[0][t],b0_copy[0][t],A_out[7-t])
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(A_mul[r])),128,"A_mul",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(A_mul_inv[r])),128,"A_mul_inv",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a1_copy[r][0])),128,"a1_copy[0]",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b0_copy[r][1])),128,"b0_copy[0]",16)
                            solver_func.update_logfile.Update_LogFile_single_inv(f,solution,A_out[r][:128],128,"A_out[128]",16)
                            f.write("\n")
                            # solver_func.integral_cnf.XOR_4bit_array(cnf,B_mul[t],B_mul_inv[t],b3_copy[0][t],a0_copy[0][t],B_out[7-t])
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(B_mul[r])),128,"B_mul",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(B_mul_inv[r])),128,"B_mul_inv",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b3_copy[r][0])),128,"b3_copy[0]",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a0_copy[r][1])),128,"a0_copy[0]",16)                        
                            solver_func.update_logfile.Update_LogFile_single_inv(f,solution,B_out[r][:128],128,"B_out[128]",16)
                            f.write("\n")
                            # A_out = [[_ for _ in range(num+i*16,num+(i+1)*16)]for i in range(8)] + list(reversed(a8_copy[1][1:])) + a1_copy[1][7:] 
                            # B_out = [[_ for _ in range(num+i*16,num+(i+1)*16)]for i in range(8)] + list(reversed(b8_copy[1][3:])) + list(reversed(b3_copy[1][5:]))
                            f.write("list(reversed(a8_copy[1][1:])) + a1_copy[1][7:]\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,A_out[r],256,"A_out[{}]".format(r),16)
                            f.write("list(reversed(b8_copy[1][3:])) + list(reversed(b3_copy[1][5:]))\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,B_out[r],256,"B_out[{}]".format(r),16)
                            f.write("==============================================================================================\n")


                if sat_flag == 0:
                    balance_flag += 1
                if sat_flag > 0:
                    print(f"SNOWV {self.max_round} round","input:",in_row,"output:",out_row,"-> Unknown",flush=True)
                if sat_flag == 0:
                    print(f"SNOWV {self.max_round} round","input:",in_row,"output:",out_row,"-> Blance",flush=True)
                    exit()

class SNOWVI_INTEGRAL:
    def __init__(self,max_round,start,end):
        self.max_round = max_round
        self.start = start
        self.end = end

    def block_init(self,max_round,A,B,T1,T2,R1,R2,R3,R1_copy,R2_copy,z):
        num = 2
        #初期値
        A[0].extend([[],[],[1 for _ in range(128)] + [_ for _ in range(num,num+128)]])
        num += 128
        B[0].extend([[],[1 for _ in range(256)]])
        R1_copy[0].extend([[1 for _ in range(128)],[1 for _ in range(128)]])
        R2_copy[0].extend([[1 for _ in range(128)],[1 for _ in range(128)],[1 for _ in range(128)]])
        R3[0].extend([1 for _ in range(128)])
        z[0].extend([1 for _ in range(128)])
        #ラウンド
        for round in range(1, self.max_round+1):
            A[round].append([_ for _ in range(num,num+128)] + A[round-1][2][128:])   #copy
            num += 128
            A[round].append([_ for _ in range(num,num+256)])   #LFSR後
            num += 256
            A[round].append([_ for _ in range(num,num+128)] + A[round][1][128:])   #zとのXOR後
            num += 128
            B[round].append( [_ for _ in range(num,num+128)] + B[round-1][1][:128])    #copy
            num += 128
            B[round].append([_ for _ in range(num,num+256)])   #LFSR後
            num += 256
            T1[round].append([_ for _ in range(num,num+128)]) #copy
            num += 128
            T1[round].append([_ for _ in range(num,num+128)]) #Additionの結果
            num += 128
            T2[round].append([_ for _ in range(num,num+128)]) #copy
            num += 128
            T2[round].append([_ for _ in range(num,num+128)]) #XORの結果
            num += 128
            T2[round].append([_ for _ in range(num,num+128)]) #Additionの結果
            num += 128
            permute(R1[round],T2[round][2])                 #permute済み
            R2[round].extend([_ for _ in range(num,num+128)])
            num += 128
            R3[round].extend([_ for _ in range(num,num+128)]) 
            num += 128
            for i in range(2):
                R1_copy[round].append([_ for _ in range(num,num+128)]) #上,右
                num += 128
            for i in range(3):
                R2_copy[round].append([_ for _ in range(num,num+128)]) #上,右,下
                num += 128
            z[round].extend([_ for _ in range(num,num+128)])
            num += 128
        A[self.max_round+1].append([_ for _ in range(num,num+128)] + A[self.max_round+1-1][2][:128])   #copy
        num += 128
        A[self.max_round+1].append([_ for _ in range(num,num+256)])   #LFSR後
        num += 256
        B[self.max_round+1].append( [_ for _ in range(num,num+128)] + B[self.max_round][1][:128])    #copy
        num += 128
        B[self.max_round+1].append([_ for _ in range(num,num+256)])   #LFSR後
        num += 256
        T1[self.max_round+1].append([_ for _ in range(num,num+128)]) #copy
        num += 128
        T1[self.max_round+1].append([_ for _ in range(num,num+128)]) #Additionの結果
        num += 128
        T2[self.max_round+1].append([_ for _ in range(num,num+128)]) #copy
        num += 128
        T2[self.max_round+1].append([_ for _ in range(num,num+128)]) #XORの結果
        num += 128
        T2[self.max_round+1].append([1 for _ in range(num,num+128)]) #Additionの結果
        permute(R1[self.max_round+1],T2[self.max_round+1][2])                 #permute済み
        R2[self.max_round+1].extend([1 for _ in range(num,num+128)])
        R3[self.max_round+1].extend([1 for _ in range(num,num+128)]) 
        z[self.max_round+1].extend([_ for _ in range(num,num+128)])
        num += 128
        return num

    def integral_init(self,cnf,IV,z_key,in_row,out_row):
        # print(z_key)
        inp = IV
        # print(IV)
        for bit in range(128):
            if bit == in_row:
                cnf.append([-inp[bit]])
            else:
                cnf.append([inp[bit]])
        out = z_key
        for bit in range(128):
            if bit == out_row:
                cnf.append([out[bit]])
            else:
                cnf.append([-out[bit]])

    def Copy_RT(self,cnf,round,max_round,A,B,T1,T2,R1,R2,R1_copy,R2_copy):
        solver_func.integral_cnf.Copy2_array(cnf,B[round-1][1][:128],B[round][0][:128],T1[round][0])
        solver_func.integral_cnf.Copy2_array(cnf,A[round-1][2][:128],A[round][0][:128],T2[round][0])
        if round != self.max_round+1:
            solver_func.integral_cnf.Copy2_array(cnf,R1[round][0],R1_copy[round][0],R1_copy[round][1])
            solver_func.integral_cnf.Copy3_array(cnf,R2[round],R2_copy[round][0],R2_copy[round][1],R2_copy[round][2])

    def Copy_LFSR(self,cnf,num,A_in,B_in):
        #copy変数の用意
        a0_copy = []
        a7_copy = []
        b0_copy = []
        b8_copy = []
        for i in range(2):
            a0_copy.append([])
            a7_copy.append([])
            b0_copy.append([])
            b8_copy.append([])
            for j in range(8):
                a0_copy[i].append([_ for _ in range(num,num+16)])
                num+=16
                a7_copy[i].append([_ for _ in range(num,num+16)])
                num+=16
                b0_copy[i].append([_ for _ in range(num,num+16)])
                num+=16
                b8_copy[i].append([_ for _ in range(num,num+16)])
                num+=16
        #Copy
        a0_root = list(reversed(A_in[9:])) + a7_copy[1][:1]
        a7_root = list(reversed(A_in[1:9]))
        b0_root = list(reversed(B_in[8:]))
        b8_root = list(reversed(B_in[:8]))
        for t in range(8):
            solver_func.integral_cnf.Copy2_array(cnf,a0_root[t],a0_copy[0][t],a0_copy[1][t])
            solver_func.integral_cnf.Copy2_array(cnf,a7_root[t],a7_copy[0][t],a7_copy[1][t])
            solver_func.integral_cnf.Copy2_array(cnf,b0_root[t],b0_copy[0][t],b0_copy[1][t])
            solver_func.integral_cnf.Copy2_array(cnf,b8_root[t],b8_copy[0][t],b8_copy[1][t])
        return num,a0_copy,a7_copy,b0_copy,b8_copy

    def LFSR_update(self,cnf,num,round,A,B):
        A_in = []
        B_in = []
        A_out = []
        B_out = []
        for i in range(16):
            A_in.append(A[round][0][i*16:i*16+16])
            B_in.append(B[round][0][i*16:i*16+16])
        num,a0_copy,a7_copy,b0_copy,b8_copy = self.Copy_LFSR(cnf,num,A_in,B_in)
        A_out = [[_ for _ in range(num+i*16,num+(i+1)*16)]for i in range(8)] + A_in[:1] + list(reversed(a7_copy[1][1:]))
        num += 128
        B_out = [[_ for _ in range(num+i*16,num+(i+1)*16)]for i in range(8)] + list(reversed(b8_copy[1]))
        num += 128
        A_mul = [[] for _ in range(8)]
        B_mul = [[] for _ in range(8)]
        for t in range(8):
            rp=[0,1,0,0,1,0,1,0,0,1,1,0,1,1,0,1]
            num,A_mul[t] = self.x_mul(cnf,num,a0_copy[0][t],rp)
            rp=[1,1,0,0,1,1,0,0,1,0,0,0,0,1,1,1]
            num,B_mul[t] = self.x_mul(cnf,num,b0_copy[0][t],rp)
        for t in range(8):
            solver_func.integral_cnf.XOR_3bit_array(cnf,A_mul[t],a7_copy[0][t],b0_copy[1][t],A_out[7-t])
            solver_func.integral_cnf.XOR_3bit_array(cnf,B_mul[t],b8_copy[0][t],a0_copy[1][t],B_out[7-t])
        A_out = list(itertools.chain.from_iterable(A_out))
        B_out = list(itertools.chain.from_iterable(B_out))
        for bit in range(256):
            vars = [A[round][1][bit]] + [A_out[bit]]
            cnf.extend(get_espresso_result_cnf("solver_func/espresso/equal_espresso.txt",vars))
            vars = [B[round][1][bit]] + [B_out[bit]]
            cnf.extend(get_espresso_result_cnf("solver_func/espresso/equal_espresso.txt",vars))
        return num,a0_copy,a7_copy,b0_copy,b8_copy,A_mul,B_mul,A_out,B_out

    def x_mul(self,cnf,num,Input,rp):
        Out = []
        copy = [_ for _ in range(num,num+8)]
        num += 8
        solver_func.integral_cnf.Copy8(cnf,Input[0],copy[0],copy[1],copy[2],copy[3],copy[4],copy[5],copy[6],copy[7])
        cnt = 0
        for bit in range(15):
            if rp[bit]:
                Out.append(num)
                num += 1
                solver_func.integral_cnf.XOR_2bit(cnf,Input[bit+1],copy[cnt],Out[bit])
                cnt += 1
            else:
                Out.append(Input[bit+1])
        Out.append(copy[7])
        # print(len(Out))
        # print(cnt)
        return num,Out

    def Addition32_4(self,cnf,num,R,T,Out):
        for i in range(4):
            cell = i*32
            num = solver_func.integral_cnf.ADDITION(cnf,num,R[cell:cell+32],T[cell:cell+32],Out[cell:cell+32])
        return num
    
    def aes(self,cnf,num,R_in,R_out):
        shifted = []
        Sin = R_convert(R_in)
        Sout = [_ for _ in range(num,num+128)]
        num += 128
        R_out_temp = R_convert(R_out)
        for i in range(16):
            cell = i*8
            vars = Sin[cell:cell+8]+Sout[cell:cell+8]
            cnf.extend((get_espresso_result_cnf("solver_func/espresso/integral/AES_sbox_espresso.txt",vars)))
        for i in range(4):
                for j in range(4):
                    shifted.extend(Sout[((i+j)%4)*32+(j*8):((i+j)%4)*32+(j+1)*8])
        for i in range(4):
            block = 32*i
            num =  solver_func.integral_cnf.XOR_92(cnf,num,shifted[block:block+32],R_out_temp[block:block+32])
        return num

    def FSM_update(self,cnf,num,round,T2,R1_copy,R2_copy,R2,R3):
        solver_func.integral_cnf.XOR_2bit_array(cnf,R3[round-1],T2[round][0],T2[round][1])
        num = self.Addition32_4(cnf,num,R2_copy[round-1][2],T2[round][1],T2[round][2])
        num = self.aes(cnf,num,R1_copy[round-1][1],R2[round])
        num = self.aes(cnf,num,R2_copy[round-1][1],R3[round])
        return num

    def snowvi_integral(self):
        cnfpath = "Kurahara_project/projects/SNOW/SNOWVI/int_cnffile/R{}.cnf".format(self.max_round)
        logpath = "Kurahara_project/projects/SNOW/SNOWVI/int_logfile/R{}.txt".format(self.max_round)
        logpath2 = "Kurahara_project/projects/SNOW/SNOWVI/int_logfile/LFSR_R{}.txt".format(self.max_round)
        A = [[]for _ in range(self.max_round+2)]
        B = [[]for _ in range(self.max_round+2)]
        A_out = [[]for _ in range(self.max_round+2)]
        B_out = [[]for _ in range(self.max_round+2)]
        a0_copy = [[]for _ in range(self.max_round+2)]
        a7_copy = [[]for _ in range(self.max_round+2)]
        b0_copy = [[]for _ in range(self.max_round+2)]
        b8_copy = [[]for _ in range(self.max_round+2)]
        A_mul = [[]for _ in range(self.max_round+2)]
        B_mul = [[]for _ in range(self.max_round+2)]
        T1 = [[]for _ in range(self.max_round+2)]
        T2 = [[]for _ in range(self.max_round+2)]
        R1 = [[]for _ in range(self.max_round+2)]
        R2 = [[]for _ in range(self.max_round+2)]
        R3 = [[]for _ in range(self.max_round+2)]
        R1_copy = [[]for _ in range(self.max_round+2)]
        R2_copy = [[]for _ in range(self.max_round+2)]
        z = [[]for _ in range(self.max_round+2)]
        cnf=[]
        num_temp = self.block_init(self.max_round,A,B,T1,T2,R1,R2,R3,R1_copy,R2_copy,z)
        end = self.start+10
        if end > 128:
            end = 128
        # for in_row in range(128):
        # for in_row in range(1):
        for in_row in range(self.start,end):
            balance_flag = 0
            # for out_row in range(128):
            for out_row in range(48,49):
                sat_flag = 0
                cnf = []
                num = num_temp
                IV = A[0][2][128:]
                z_key = z[self.max_round+1]
                self.integral_init(cnf,IV,z_key,in_row,out_row)
                cnf.append([-1])
                for a in A[self.max_round+1][1]:
                    cnf.append([-a])
                for b in B[self.max_round+1][1]:
                    cnf.append([-b])
                # print
                for round in range(1,self.max_round+2):
                    self.Copy_RT(cnf,round,self.max_round,A,B,T1,T2,R1,R2,R1_copy,R2_copy)
                    num = self.Addition32_4(cnf,num,R1_copy[round-1][0],T1[round][0],T1[round][1])
                    solver_func.integral_cnf.XOR_2bit_array(cnf,R2_copy[round-1][0],T1[round][1],z[round])
                    num = self.FSM_update(cnf,num,round,T2,R1_copy,R2_copy,R2,R3)
                    num,a0_copy[round],a7_copy[round],b0_copy[round],b8_copy[round],A_mul[round],B_mul[round],A_out[round],B_out[round] = self.LFSR_update(cnf,num,round,A,B)
                    if round != self.max_round +1:
                        solver_func.integral_cnf.XOR_2bit_array(cnf,z[round],A[round][1][:128],A[round][2][:128])

                aes_cnf = CNF(from_clauses = cnf)
                aes_cnf.to_file(cnfpath)
                s = solver_func.solver.Solver(cnfpath,logpath)
                s.kissat_sc2024()
                result = s.CheckResult()

                if result == True:
                    sat_flag += 1
                    solution = solver_func.extract_solution.Extract_Solution(logpath)
                    with open(logpath,"w") as f:
                        solver_func.update_logfile.Update_LogFile_single(f,solution,A[0][2][:16*8],128,"iv",8)
                        solver_func.update_logfile.Update_LogFile_single(f,solution,A[0][2],256,"A[0][2]",8)
                        solver_func.update_logfile.Update_LogFile_single(f,solution,B[0][1],256,"B[0][1]",8)
                        # solver_func.update_logfile.Update_LogFile_single(f,solution,R1[0],128,"R1",8)
                        # solver_func.update_logfile.Update_LogFile_single(f,solution,R2[0],128,"R2",8)
                        # solver_func.update_logfile.Update_LogFile_single(f,solution,R3[0],128,"R3",8)
                        f.write("==============================================================================================\n")
                        for r in range(1,self.max_round+2):
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,A[r][i],256,"A[{}][{}]".format(r,i),8)
                            if r != self.max_round+1:
                                solver_func.update_logfile.Update_LogFile_single(f,solution,A[r][2],256,"A[{}][2]".format(r),8)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,B[r][i],256,"B[{}][{}]".format(r,i),8)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,T1[r][i],128,"T1[{}][{}]".format(r,i),8)
                            for i in range(3):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,T2[r][i],128,"T2[{}][{}]".format(r,i),8)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,R1[r][0],128,"R1",8)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,R2[r],128,"R2",8)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,R3[r],128,"R3",8)
                            if r != self.max_round+1:
                                for i in range(2):
                                    solver_func.update_logfile.Update_LogFile_single(f,solution,R1_copy[r][i],128,"R1_copy[{}][{}]".format(r,i),8)
                                for i in range(3):
                                    solver_func.update_logfile.Update_LogFile_single(f,solution,R2_copy[r][i],128,"R2_copy[{}][{}]".format(r,i),8)
                            # solver_func.update_logfile.Update_LogFile_single(f,solution,R2[r-1][0],128,"R2[r-1]",8)
                                f.write("\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,z[r],128,"z[{}]".format(r),8)
                            f.write("==============================================================================================\n")
                        # solver_func.update_logfile.Update_LogFile_single(f,solution,B[self.max_round+1][0][128:],128,"B[{}][0]".format(r),8)
                        # solver_func.update_logfile.Update_LogFile_single(f,solution,R1_copy[self.max_round][0],128,"R1_copy[{}][0]".format(self.max_round),8)
                        # for i in range(2):
                        #     solver_func.update_logfile.Update_LogFile_single(f,solution,T1[self.max_round+1][i],128,"T1[{}][{}]".format(self.max_round+1,i),8)
                        # solver_func.update_logfile.Update_LogFile_single(f,solution,z[self.max_round+1],128,"z",8)
                    with open(logpath2,"w") as f:
                        for r in range(1,self.max_round+2):
                            A_in = []
                            B_in = []
                            for i in range(16):
                                A_in.append(A[r][0][i*16:i*16+16])
                                B_in.append(B[r][0][i*16:i*16+16])
                            
                            a0_root = list(reversed(A_in[9:])) + a7_copy[r][1][:1]
                            a7_root = list(reversed(A_in[1:9]))
                            b0_root = list(reversed(B_in[8:]))
                            b8_root = list(reversed(B_in[:8]))
                            solver_func.update_logfile.Update_LogFile_single(f,solution,A[r][0],256,"A[{}][0]".format(r),16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,B[r][0],256,"B[{}][0]".format(r),16)

                            f.write("a0_root = list(reversed(A_in[9:])) + a7_copy[1][:1]\n")
                            # print(len(list(itertools.chain.from_iterable(a0_root))))
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a0_root)),128,"a0_root".format(r),16)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a0_copy[r][i])),128,"a0_copy[{}]".format(i),16)
                            f.write("\n")
                            f.write("a7_root = list(reversed(A_in[1:9]))\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a7_root)),128,"a7_root",16)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a7_copy[r][i])),128,"a7_copy[{}]".format(i),16)
                            f.write("\n")
                            f.write("b0_root = list(reversed(B_in[8:]))\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b0_root)),128,"b0_root",16)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b0_copy[r][i])),128,"b0_copy[{}]".format(i),16)
                            f.write("\n")
                            f.write("b8_root = list(reversed(B_in[:8]))\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b8_root)),128,"b8_root",16)
                            for i in range(2):
                                solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b8_copy[r][i])),128,"b8_copy[{}]".format(i),16)
                            f.write("\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a0_copy[r][0])),128,"a0_copy[0]",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(A_mul[r])),128,"A_mul",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b0_copy[r][0])),128,"b0_copy[0]",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(B_mul[r])),128,"B_mul",16)
                            f.write("\n")
                            # solver_func.integral_cnf.XOR_4bit_array(cnf,A_mul[t],A_mul_inv[t],a1_copy[0][t],b0_copy[0][t],A_out[7-t])
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(A_mul[r])),128,"A_mul",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a7_copy[r][0])),128,"a7_copy[0]",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b0_copy[r][1])),128,"b0_copy[0]",16)
                            solver_func.update_logfile.Update_LogFile_single_inv(f,solution,A_out[r][:128],128,"A_out[128]",16)
                            f.write("\n")
                            # solver_func.integral_cnf.XOR_4bit_array(cnf,B_mul[t],B_mul_inv[t],b3_copy[0][t],a0_copy[0][t],B_out[7-t])
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(B_mul[r])),128,"B_mul",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(b8_copy[r][0])),128,"b8_copy[0]",16)
                            solver_func.update_logfile.Update_LogFile_single(f,solution,list(itertools.chain.from_iterable(a0_copy[r][1])),128,"a0_copy[0]",16)                        
                            solver_func.update_logfile.Update_LogFile_single_inv(f,solution,B_out[r][:128],128,"B_out[128]",16)
                            f.write("\n")
                            # A_out = [[_ for _ in range(num+i*16,num+(i+1)*16)]for i in range(8)] + list(reversed(a8_copy[1][1:])) + a1_copy[1][7:] 
                            # B_out = [[_ for _ in range(num+i*16,num+(i+1)*16)]for i in range(8)] + list(reversed(b8_copy[1][3:])) + list(reversed(b3_copy[1][5:]))
                            f.write("list(reversed(a8_copy[1][1:])) + a1_copy[1][7:]\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,A_out[r],256,"A_out[{}]".format(r),16)
                            f.write("list(reversed(b8_copy[1][3:])) + list(reversed(b3_copy[1][5:]))\n")
                            solver_func.update_logfile.Update_LogFile_single(f,solution,B_out[r],256,"B_out[{}]".format(r),16)
                            f.write("==============================================================================================\n")

                if sat_flag == 0:
                    balance_flag += 1
                if sat_flag > 0:
                    print(f"SNOWVI {self.max_round} round","input:",in_row,"output:",out_row,"-> Unknown",flush=True)
                if sat_flag == 0:
                    print(f"SNOWVI {self.max_round} round","input:",in_row,"output:",out_row,"-> Blance",flush=True)
                    exit()
s = SNOWV_INTEGRAL(1,0)
s.snowv_integral()
        