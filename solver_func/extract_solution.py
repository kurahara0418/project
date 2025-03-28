def Extract_Solution(filepath):
    with open(filepath,"r") as f:
        lines = f.readlines()
        solution_str = []
        for i in range(len(lines)):
            if lines[i].find('v',0) == 0:
                lines[i] = lines[i].strip('v ')
                lines[i] = lines[i].strip('\n')
                lines[i] = lines[i].replace(' ',',')
                solution_str.append(lines[i])
        
        solution_temp = []
        for i in range(len(solution_str)):
            temp = solution_str[i].split(',')
            solution_temp.append(temp)
        
        solution_int = []
        for i in range(len(solution_temp)):
            for j in range(len(solution_temp[i])):
                solution_int.append(int(solution_temp[i][j]))
    return solution_int