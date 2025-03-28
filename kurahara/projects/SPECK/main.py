import sys
sys.path.append('Kurahara_project')
from projects.SPECK.SAT_SPECK import SPECK32_DCP, SPECK48_DCP, SPECK64_DCP, SPECK96_DCP, SPECK128_DCP
matsui=0

def main_SPECK32():
    print("SPECK32")
    max_round=2
    weight=0
    upper=31
    up=1
    # matsui=1
    SPECK32_DCP(max_round,weight,upper,up,matsui)

def main_SPECK48():
    print("SPECK48")
    max_round=6
    weight=13
    upper=200
    up=1
    matsui=1
    SPECK48_DCP(max_round,weight,upper,up,matsui)

def main_SPECK64():
    print("SPECK64")
    max_round=7
    weight=18
    upper=30
    up=1
    matsui=1
    SPECK64_DCP(max_round,weight,upper,up,matsui)

def main_SPECK96():
    print("SPECK96")
    max_round=3
    weight=2
    upper=200
    up=1
    SPECK96_DCP(max_round,weight,upper,up,matsui)

def main_SPECK128():
    print("SPECK128")
    max_round=3
    weight=2
    upper=200
    up=1
    SPECK128_DCP(max_round,weight,upper,up,matsui)


# main_SPECK32()
# main_SPECK48()
# main_SPECK64()
main_SPECK96()
main_SPECK128()
