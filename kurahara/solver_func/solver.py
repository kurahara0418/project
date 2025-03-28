import sys
sys.path.append('/Users/kurahararikuto/Documents/python')
import subprocess

class Solver:
    def __init__(self,CNF_PATH,LOG_PATH):
        self.cnfpath = CNF_PATH
        self.logpath = LOG_PATH
    
    def kissat_MAB_HyWalk(self):
        solverpath = 'sat_solver/Kissat_MAB-HyWalk/build/kissat'
        cmd = "%s %s > %s"%(solverpath,self.cnfpath,self.logpath)
        subprocess.run(cmd,shell = True)

    def kissat_MAB_ESA(self):
        solverpath = './solver/Kissat_MAB_ESA/build/kissat'
        cmd = "%s %s > %s"%(solverpath,self.cnfpath,self.logpath)
        subprocess.run(cmd,shell = True)

    def kissat_ver3(self):
        solverpath = './solver/kissat-rel-3.0.0/build/kissat'
        cmd = "%s %s > %s"%(solverpath,self.cnfpath,self.logpath)
        subprocess.run(cmd,shell = True)

    def ParKissat(self):
        solverpath = './solver/ParKissat-RS/base/parkissat/parkissat'
        cmd = f"{solverpath} -c={40} -simp -shr-sleep=500000 -shr-lit=1500 {self.cnfpath} -initshuffle > {self.logpath}"
        subprocess.run(cmd,shell = True)
    
    def kissat_sc2024(self):
        solverpath = 'sat_solver/kissat-sc2024/build/kissat/build/kissat'
        cmd = "%s %s > %s"%(solverpath,self.cnfpath,self.logpath)
        subprocess.run(cmd,shell = True)

    def CheckResult(self):
        with open(self.logpath) as f:
            result = f.read()
            if "s UNSATISFIABLE" in result:
                cmd = "rm %s"%self.cnfpath
                # subprocess.run(cmd,shell = True)
                cmd = "rm %s"%self.logpath
                subprocess.run(cmd,shell = True)
                return False
            elif "s SATISFIABLE" in result:
                cmd = "rm %s"%self.cnfpath
                # subprocess.run(cmd,shell = True)
                return True