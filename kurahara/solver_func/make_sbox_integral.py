import itertools
import subprocess
import codecs
import ast

def get_value(term):
    value = int("".join(map(str,term)),2)
    return value

def read_anf(anf_path):
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
                    anf_array[out_bit][term][int(char)] = 1
    return anf_array, con

def reverse(bit_size,num):
    num_bin = f"{num:0{bit_size}b}"
    temp = []
    for i in range(bit_size):
        temp.append(num_bin[bit_size -1 -i])
    reverse_bin = "".join(map(str,temp))
    return reverse_bin

def times(bit_size,y0,y0_map,y0_value,y1,y1_value,con_n,con):
    F_y_map = [0 for _ in range(2**bit_size)]
    if y0 == []:
        for value in y1_value:
            F_y_map[value] = 1
        return y1, F_y_map, y1_value, con
    F_y = []
    F_y_value = []
    if con_n:
        F_y.extend(y1)
        # print(F_y)
        F_y_value.extend(y1_value)
        for value in y1_value:
            F_y_map[value] = 1
    if con:
        for i in range(len(y0)):
            if y0_map[y0_value[i]] == 1:
                if F_y_map[y0_value[i]] == 1:
                    F_y_map[y0_value[i]] = 2
                else:
                    F_y.append(y0[i])
                    F_y_value.append(y0_value[i])
                    F_y_map[y0_value[i]] = 1
    # print(len(F_y))
    # print(F_y)
    for i in range(len(y0)):
        if y0_map[y0_value[i]]%2 == 0:
            # print(y0_value[i])
            continue
        for j in range(len(y1)):
            temp=[0 for _ in range(bit_size)]
            for y0_bit, y1_bit, bit in zip(y0[i], y1[j], [_ for _ in range(bit_size)]):
                if y0_bit == 1 or y1_bit == 1:
                    temp[bit] = 1
            value = get_value(temp)
            if F_y_map[value] == 0:
                F_y.append(temp)
                F_y_value.append(value)
                F_y_map[value] = 1 
            elif F_y_map[value] == 1:
                F_y_map[value] = 2
            elif F_y_map[value] == 2:
                F_y_map[value] = 1
            # print(value)
            # print(F_y_value)
    return F_y, F_y_map, F_y_value, con*con_n

def make_anf(anf_path, out_anf, out_map):
    con_n = 0
    y, cons = read_anf(anf_path)
    bit_size = len(y)
    y_value = [[]for _ in range(bit_size)]
    for i in range(bit_size):
        for term in y[i]:
            y_value[i].append(get_value(term))
    anf = [[] for _ in range(2**bit_size)]
    anf_map = [[] for _ in range(2**bit_size)]
    for u in range(2**bit_size):
        F_y = []
        F_y_map = [0 for i in range(2**bit_size)]
        F_y_value = []
        u_rev = reverse(bit_size,u)
        for bit in range(bit_size):
            if u_rev[bit] == "1":
                F_y, F_y_map, F_y_value, con_n = times(bit_size,F_y,F_y_map,F_y_value,y[bit],y_value[bit],con_n,cons[bit])
        cnt = 0
        for i in range(2**bit_size):
            F_y_map[i] = F_y_map[i]%2
        for i in range(len(F_y)):
            if F_y_map[F_y_value[i]] == 1:
                cnt += 1
                anf[u].append(F_y[i])
        anf_map[u] = F_y_map
        print(cnt)

    with open (out_anf,"w") as f:
        for anf_part in anf:
            f.write(str(anf_part))
            f.write("\n")
    with open (out_map,"w") as f:
        for map_part in anf_map:
            f.write(str(map_part))
            f.write("\n")
    return anf

def output_file(bit_size, output_path, out):
    with open(out_path,"w") as f:
        f.write("output:\n")
        out_0 = [0 for _ in range(2*bit_size)]
        f.write(str(out_0))
        f.write("\n")
        for x in range(1,2**bit_size):
            x_bin = bin(x)[2:].zfill(bit_size)
            x_bin = [int(bit) for bit in x_bin]
            x_bin = str(x_bin)
            for mon in out[x]:
                y_bin = str(mon)
                f.write(x_bin[:-1] + ", " + y_bin[1:])
                f.write("\n")

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

def make_k_bar(bit_size,k):
    F_x = []
    F_x_map = [0 for _ in range(2**bit_size)]
    k_bin=f"{k:0{bit_size}b}"
    k_arr=[int(k_bin[bit]) for bit in range(bit_size)]
    for k_bar in range(2**bit_size):
        k_bar_bin=f"{k_bar:0{bit_size}b}"
        k_bar_arr=[int(k_bar_bin[bit]) for bit in range(bit_size)]
        flag=True
        for k_bar_bit,k_bit in zip(k_bar_arr,k_arr):
            if k_bar_bit<k_bit:
                flag=False
        if flag:
            F_x.append(k_bar_arr)
            F_x_map[k_bar] = 1
    return F_x, F_x_map

def Sbox(bit_size,map_path):
    out=[[]for _ in range(2**bit_size)]
    anf_map=[[]for _ in range(2**bit_size)]
    with open(map_path, 'r') as file:
        lines = file.readlines()  # 各行をリストに読み込む
        for i in range(len(lines)):
            anf_map[i] = ast.literal_eval(lines[i].strip())
            # print(anf_map[i])
    for k in range(2**bit_size):
        F_x, F_x_map = make_k_bar(bit_size,k)
        # print(F_x_map)
        for u in range(2**bit_size):
            F_y_map = anf_map[u]
            for i in range(2**bit_size):
                # print(i)
                # print(F_y_map)
                if F_y_map[i] == F_x_map[i] == 1:
                    D_k = int(reverse(bit_size,k),2)
                    rev_u_arr = []
                    u_bin = reverse(bit_size,u)
                    u_arr = [int(u_bin[bit]) for bit in range(bit_size)]
                    for j in range(bit_size):
                        rev_u_arr.append(u_arr[bit_size -1 -j])
                    out[D_k].append(rev_u_arr)
                    break
    return out

def test(bit_size,our_out,ref_out):
    a=[]
    with open(our_out, 'r') as file:
        lines = file.readlines()
        for i in range(1,len(lines)):
            a.append(ast.literal_eval(lines[i].strip()))
    with open(ref_out, 'r') as file:
        lines = file.readlines()
        for i in range(1,len(lines)-1):
            b=ast.literal_eval(lines[i].strip())
            if b not in a:
                print("not exist : ",b)

# our_out = "solver_func/sbox_integral/out_table/Orthros_out_table.txt"
# ref_out = "solver_func/sbox_integral/out_table_ref/Orthros.txt"
# test(4,our_out,ref_out)
# our_out = "solver_func/sbox_integral/out_table/AES_out_table.txt"
# ref_out = "solver_func/sbox_integral/out_table_ref/AES.txt"
# test(8,our_out,ref_out)

# aes_anf="solver_func/sbox_integral/anf/aes_Sbox_anf.txt"
# ort_anf="solver_func/sbox_integral/anf/Orthros_Sbox_anf.txt"
# pre_anf="solver_func/sbox_integral/anf/PRESENT_Sbox_anf.txt"
aes_map="solver_func/sbox_integral/anf_e/AES_Sbox_map.txt"
ort_map="solver_func/sbox_integral/anf_e/Orthros_Sbox_map.txt"
pre_map="solver_func/sbox_integral/anf_e/PRESENT_Sbox_map.txt"
# out=Sbox(4,ort_pre)

# out=Sbox(8,aes_map)
# for x in range(2**8):
#     out[x] = [list(t) for t in set(tuple(sublist) for sublist in out[x])]
#     out[x] = size_reduce(8,out[x])
# #     print(f"{x:08b}")
# #     print(out[x])
# out_path = "solver_func/sbox_integral/out_table/AES_out_table.txt"
# output_file(8, out_path, out)

out=Sbox(4,ort_map)
# for x in range(2**4):
#     out[x] = [list(t) for t in set(tuple(sublist) for sublist in out[x])]
#     out[x] = size_reduce(4,out[x])
# #     print(f"{x:04b}")
# #     print(out[x])
# out_path = "solver_func/sbox_integral/out_table/Orthros_out_table.txt"
# output_file(4, out_path, out)



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
