import sys
sys.path.append('Kurahara_project')

from projects.SNOW.SAT_DCP_SNOW import snowv
from projects.SNOW.SAT_DCP_SNOW import snowvi
from projects.SNOW.SAT_DCP_SNOW_Rkey import snowv_Rkey
from projects.SNOW.SAT_DCP_SNOW_Rkey import snowvi_Rkey
key=0
lim=0
dc=0
matsui=0
par=0

def main_snowv():
    print("snowv")
    round=3
    weight=16
    upper=100
    up=1
    s=snowv(round,weight,upper,up,key,lim,dc,matsui,par)
    s.sat_snowv_DCP()

def main_snowv_lim():
    print("snowv_lim")
    round=3
    weight=16
    upper=100
    up=1
    lim=1
    s=snowv(round,weight,upper,up,key,lim,dc,matsui,par)
    s.sat_snowv_DCP()

def main_snowv_Rkey():
    print("snowv_Rkey")
    round=6
    weight=112
    upper=121
    up=1
    key=1
    dc=1
    s=snowv_Rkey(round,weight,upper,up,key,lim,dc,matsui,par)
    s.sat_snowv_Rkey_DCP()

def main_snowv_Rkey_lim():
    print("snowv_Rkey_lim")
    round=4
    weight=94
    upper=121
    up=1
    key=1
    lim=1
    dc=1
    s=snowv_Rkey(round,weight,upper,up,key,lim,dc,matsui,par)
    s.sat_snowv_Rkey_DCP()


def main_snowvi():
    print("snowvi")
    round=5
    weight=116
    upper=198
    up=1
    key=1
    dc=1
    matsui=1
    s=snowvi(round,weight,upper,up,key,lim,dc,matsui,par)
    s.sat_snowvi_DCP()

def main_snowvi_lim():
    print("snowvi_lim")
    round=1
    weight=0
    upper=100
    up=1
    lim=1
    s=snowvi(round,weight,upper,up,key,lim,dc,matsui,par)
    s.sat_snowvi_DCP()

def main_snowvi_Rkey():
    print("snowvi_Rkey")
    round=6
    weight=57
    upper=121
    up=1
    key=1
    dc=1
    s=snowvi_Rkey(round,weight,upper,up,key,lim,dc,matsui,par)
    s.sat_snowvi_Rkey_DCP()

def main_snowvi_Rkey_lim():
    print("snowvi_Rkey_lim")
    round=5
    weight=34
    upper=121
    up=1
    key=1
    dc=1
    lim=1
    s=snowvi_Rkey(round,weight,upper,up,key,lim,dc,matsui,par)
    s.sat_snowvi_Rkey_DCP()

main_snowv()
# main_snowv_lim()
# main_snowv_Rkey()
# main_snowv_Rkey_lim()
# main_snowvi()
# main_snowvi_lim()
# main_snowvi_Rkey()
# main_snowvi_Rkey_lim()