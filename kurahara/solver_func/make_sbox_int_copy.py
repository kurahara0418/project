import itertools
import subprocess
import codecs

def read_anf(anf_path,rev):
    with open(anf_path,"r") as f:
        lines = f.readlines()
        line_size=[]
        anf_array=[]
        bit_size = len(lines)
        con=[0 for _ in range(bit_size)]

        for term in range(bit_size):
            # print(lines[term][-3:-1])
            # print(lines[term])
            if lines[term][-3:-1] == " 1":
                lines[term] = lines[term][:-4]
                # con[bit_size -1 -term] = 1
                con[term] = 1
            cnt = 0
            for char in lines[term]:
                if char == "=" or char == "+":
                    cnt+= 1
            line_size.append(cnt)

        for bit in range(bit_size):
            temp_array=[[0 for _ in range(bit_size)]for _ in range(line_size[bit])]
            anf_array.append(temp_array)
        #     print(temp_array)
        # print(anf_array)

        out_bit = -1
        for line in lines:
            out_bit += 1
            term=0
            for char in line[2:]:
                if char == "+":
                    term += 1
                if char.isdigit():
                    if rev:
                        #(y3,y2,y1,y0)
                        anf_array[out_bit][term][bit_size - int(char) -1] = 1
                    else:
                        #(y0,y1,y2,y3)
                        anf_array[out_bit][term][int(char)] = 1
    # print(anf_array)
    # print(con)
    return anf_array, con

def output_file(bit_size, output_path):
    with open(out_path,"w") as f:
        for x in range(2**bit_size):
            f.write("input:" + bin(x)[2:].zfill(bit_size))
            f.write("\n")
            for mon in (out[x]):
                for bit in mon:
                    f.write(str(bit))
                f.write("\n")
            f.write("\n")
            print(out[x])

def reverse(bit_size,num):
    num_bin = f"{num:0{bit_size}b}"
    temp = []
    for i in range(bit_size):
        temp.append(num_bin[bit_size -1 -i])
    reverse_bin = "".join(map(str,temp))
    return reverse_bin

def size_reduce(bit_size,out):
    mon_size = len(out)
    out_map = [1 for _ in range(mon_size)]
    for i in range(mon_size): 
        if out_map[i] == 0:
            continue
        for j in range(mon_size): #消す対象
            if i == j or out_map[j] == 0:
                continue
            check_flag = True
            mon1 = out[i]
            mon2 = out[j]
            # print(out)
            # print("mon1",mon1)
            # print("mon2",mon2)
            for bit in range(bit_size):
                if mon1[bit] == 1 and mon2[bit] == 0:
                    check_flag = False
                    break
            if check_flag:
                # print("remove", mon2)
                out_map[j] = 0
    out_temp = []
    for i in range(mon_size):
        if out_map[i] == 1:
            out_temp.append(out[i])
    return out_temp

def times(bit_size,y0,y1,con_n,con):
    if y0 == []:
        return y1,con
    y0y1=[]
    if con_n:
        y0y1.extend(y1)
    if con:
        y0y1.extend(y0)
    for y0_term in y0:
        # print("y0 : ",y0_term)
        for y1_term in y1:
            # print("y1 : ", y1_term)
            temp=[0 for _ in range(bit_size)]
            for y0_bit, y1_bit, bit in zip(y0_term, y1_term, [_ for _ in range(bit_size)]):
                if y0_bit == 1 or y1_bit == 1:
                    temp[bit] = 1
            # print(y0y1)
            # print(temp)
            if temp in y0y1:
                y0y1.remove(temp)
            else:
                y0y1.append(temp)
    return y0y1, 0

def make_k_bar(bit_size,k,rev):
    k_bar=[]
    k_bin=f"{k:0{bit_size}b}"
    k_arr=[int(k_bin[bit]) for bit in range(bit_size)]
    if rev:
        temp_k_arr = []
        for i in range(bit_size):
            temp_k_arr.append(k_arr[bit_size -1 -i])
        k_arr = temp_k_arr
    for bar in range(2**bit_size):
        bar_bin=f"{bar:0{bit_size}b}"
        bar_arr=[int(bar_bin[bit]) for bit in range(bit_size)]
        flag=True
        for bar_bit,k_bit in zip(bar_arr,k_arr):
            if bar_bit<k_bit:
                flag=False
        if flag:
            k_bar.append(bar_arr)
    return k_bar

def pai(bit_size,u_arr,x_arr):
    flag=True
    for u_bit, x_bit in zip(u_arr,x_arr):
        if u_bit == 1 and x_bit == 0:
            flag=False
    return flag

def make_y_arr(y,reverse,x_arr):
    y_arr=[]
    for y_form, r in zip(y,reverse):
        xor_flag = 0
        for y_term in y_form:
            and_flag = 1
            for y_bit, x_bit in zip(y_term, x_arr):
                if y_bit==1 and x_bit ==0:
                    and_flag = 0
                    break
            xor_flag ^= and_flag
        xor_flag ^= r
        y_arr.append(xor_flag)
    return y_arr

def Sbox(bit_size,anf_path):
    out=[[]for _ in range(2**bit_size)]
    y, cons = read_anf(anf_path, rev = False)
    # print(y)
    # print(cons)
    # cons = [1,0,0,0]
    con_n = 0
    # print(y)
    # for k in range(2**bit_size):
    for k in range(1):
        F_x = make_k_bar(bit_size,k,rev = False)
        # print(F_x)
        for u in range(16):
            # u_bin=f"{u:0{bit_size}b}"
            u_bin = reverse(bit_size,u)
            u_arr = [int(u_bin[bit]) for bit in range(bit_size)]
            F_y = []
            for u_bit, y_term, con in zip(u_arr, y, cons):
                if u_bit == 1:
                    F_y, con_n = times(bit_size, F_y, y_term, con_n, con)
            print("u = ",u)
            print(len(F_y))
            print(F_y)
            print("")
            # print(F_y)
            for y_term in F_y:
                # print(y_term)
                if y_term in F_x:
                    D_k = int(reverse(bit_size,k),2)
                    rev_u_arr = []
                    for i in range(bit_size):
                        rev_u_arr.append(u_arr[bit_size -1 -i])
                    # if size_reduce(bit_size,D_k,rev_u_arr,out):
                    out[D_k].append(rev_u_arr)
                    # out[k].append(u_arr)
    return out

# anf_path="solver_func/sbox_integral/anf/Orthros_Sbox_anf.txt"
# anf_array, con = read_anf(anf_path,rev=False)
# # print(anf_array)
# bit_size = 4
# c_path="solver_func/sbox_integral/anf_c/Orthros_Sbox_anf_c.txt"
# with open(c_path,"w") as f:
#     f.write("{\n")
#     for y in range(len(anf_array)):
#         f.write("{")
#         for nom in range(len(anf_array[y])):
#             f.write("{")
#             for bit in range(bit_size):
#                 f.write(str(anf_array[y][nom][bit]))
#                 if bit != bit_size-1:
#                     f.write(",")
#             f.write("}")
#             if nom == len(anf_array[y])-1:
#                 f.write("}")
#             else:
#                 f.write(",")
#         if y != len(anf_array)-1:
#             f.write(",\n")
#     f.write("\n}")
#     f.write("\n{")
#     for bit in range(bit_size):
#         f.write(str(con[bit]))
#         if bit != bit_size-1:
#             f.write(",")
#     f.write("}")

        # f.write("input:" + bin(x)[2:].zfill(bit_size))
        # f.write("\n")
        # for mon in (out[x]):
        #     for bit in mon:
        #         f.write(str(bit))
        #     f.write("\n")
        # f.write("\n")
        # print(out[x])



anf_path="solver_func/sbox_integral/anf/Orthros_Sbox_anf.txt"
out=Sbox(4,anf_path)


# for x in range(2**4):
#     out[x] = [list(t) for t in set(tuple(sublist) for sublist in out[x])]
#     out[x] = size_reduce(4,out[x])
#     print(f"{x:04b}")
#     print(out[x])

# out_path = "solver_func/sbox_integral/out_table/AES_out_table"
# output_file(8, out_path)