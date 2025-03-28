def Update_LogFile(f,solution,Var,rounds,num,var_name,split_num):
    #print("%s[%d] : "%(var_name,rounds),end="")
    f.write("%s[%d]"%(var_name,rounds))
    for i in range(10-len(var_name)):
        f.write(" ")
    f.write(":")
    for i in range(num):
        # print(Var[rounds][i])
        # print(Var)
        # print(i)s
        if i % split_num == 0:
            #print("|",end="")
            f.write(" ")
        if Var[rounds][i] in solution:
            # print(Var[rounds][i])
            #print("■",end="")
            f.write("■")
        else:
            # print(Var[rounds][i])
            #print("□",end="")
            f.write("□")
    #print("")
    f.write("\n")
    #f.flush()

def Update_LogFile_single(f,solution,Var,num,var_name,split_num):
    #print("%s[%d] : "%(var_name,rounds),end="")
    f.write("%s"%(var_name))
    for i in range(13-len(var_name)):
        f.write(" ")
    f.write(":")
    for i in range(num):
        # print(Var[rounds][i])
        # print(Var)
        # print(i)s
        if i % split_num == 0:
            #print("|",end="")
            f.write(" ")
        if Var[i] in solution:
            # print(Var[rounds][i])
            #print("■",end="")
            f.write("■")
        else:
            # print(Var[rounds][i])
            #print("□",end="")
            f.write("□")
    #print("")
    f.write("\n")
    #f.flush()

def Update_LogFile_single_inv(f,solution,Var,num,var_name,split_num):
    #print("%s[%d] : "%(var_name,rounds),end="")
    f.write("%s"%(var_name))
    for i in range(13-len(var_name)):
        f.write(" ")
    f.write(":")
    block = num//split_num
    # print(block)
    # print(Var)
    for i in range(block):
        f.write(" ")
        temp = Var[(block-1-i)*split_num:(block-1-i)*split_num+split_num]
        # print(temp)
        for j in range(split_num):
            if temp[j] in solution:
                f.write("■")
            else:
                f.write("□")
    #print("")
    f.write("\n")
    #f.flush()

def Update_LogFile_inv(f,solution,Var,rounds,num,var_name,split_num):
    #print("%s[%d] : "%(var_name,rounds),end="")
    f.write("%s[%d]"%(var_name,rounds))
    for i in range(10-len(var_name)):
        f.write(" ")
    f.write(":")
    f.write(" ")
    block_num=num//split_num
    # print(block_num)
    for i in range(block_num):
        for j in range(split_num):
            if Var[rounds][(block_num-i-1)*split_num+j] in solution:
                # print("■",end="")
                f.write("■")
            else:
                #print("□",end="")
                f.write("□")
        f.write(" ")
    #print("")
    f.write("\n")
    #f.flush()

def Update_LogFile_part(f,solution,Var,rounds,cell_num,num,var_name):
    # print(Var)
    f.write("%s[%d][%d]"%(var_name,rounds,cell_num))
    length=len("%s[%d]"%(var_name,cell_num))
    for i in range(10-length):
        f.write(" ")
    f.write(":")
    for i in range(num):
        if i%8==0:
            f.write(" ")
        # print(Var[i])
        if Var[i] in solution:
            # print(Var[i])
            f.write("■")
        else:
            # print(Var[i])
            f.write("□")
    f.write("\n")

def Update_LogFile_cell(f,solution,Var,rounds,var_name):
    f.write("%s[%d]"%(var_name,rounds))
    # print(Var)
    for i in range(10-len(var_name)):
        f.write(" ")
    f.write(": ")
    if Var[rounds] in solution:
        f.write("■")
    else:
        # print(Var[i])
        f.write("□")
    f.write("\n")

def Update_LogFile_w(f,solution,Var,cell_num,num,var_name):
    f.write("%s"%(var_name))
    # print(Var)
    for i in range(13-len(var_name)):
        f.write(" ")
    f.write(":  ")
    
    for i in range(cell_num-1):
        if Var[i] in solution:
            # print(Var[i])
            f.write("■")
        else:
            # print(Var[i])
            f.write("□")
    Var_copy=Var[cell_num-1:]
    for i in range(num-(cell_num-1)):
        if i%cell_num==0:
            f.write(" ")
        if Var_copy[i] in solution:
            # print(Var[i])
            f.write("■")
        else:
            # print(Var[i])
            f.write("□")
    f.write("\n")

def Update_LogFile_signed(f,solution,Var,num,var_name,split_num):
    #print("%s[%d] : "%(var_name,rounds),end="")
    f.write("%s"%(var_name))
    for i in range(13-len(var_name)):
        f.write(" ")
    f.write(":")
    for i in range(num):
        if i % split_num == 0:
            #print("|",end="")
            f.write(" ")
        for var in Var[i]: 
            if var in solution:
                f.write("■")
            else:
                f.write("□")
        f.write("\n")

def Update_LogFile_signed_s(f,solution,Var,num,var_name,split_num):
    #print("%s[%d] : "%(var_name,rounds),end="")
    f.write("%s"%(var_name))
    for i in range(13-len(var_name)):
        f.write(" ")
    f.write(":")
    for i in range(num):
        if i % split_num == 0:
            #print("|",end="")
            f.write(" ")
        if Var[i][0] not in solution and Var[i][1] not in solution:
            f.write("-")
        elif Var[i][0] in solution and Var[i][1] in solution:
            f.write("u")
        elif Var[i][0] not in solution and Var[i][1] in solution:
            f.write("n")
        else:
            f.write("error")
    #print("")
    f.write("\n")
    #f.flush()