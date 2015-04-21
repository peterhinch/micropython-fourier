# dfttest.py Test DFT with synthetic data
# Author: Peter Hinch
# 11th April 2015

import math
from dftclass import DFT, FORWARD, REVERSE, POLAR, DB

def cartesian_print(objDFT):
    for x in range(objDFT.length):
        print("{:6d}{:8.2f}{:8.2f}j".format(x, objDFT.re[x], objDFT.im[x]))

def polarprint(objDFT):
    print("Polar: mag      phase (degs)")
    for x in range(objDFT.length//2): # Only the first half is valid
        print("{:6d}{:8.2f}  {:8.2f}".format(x, objDFT.re[x], int(math.degrees(objDFT.im[x]))))

# Data acquisition functions. For forward transforms only the real array is populated.

def acqu_test(objDFT):                  # Example: populate with computed data
    for x in range(objDFT.length):
        objDFT.re[x] = 10+ 10*math.sin(8*math.pi*x/objDFT.length)

def revtest(objDFT):                    # Populate with frequency domain data for reverse transform
    for x in range(objDFT.length):
        objDFT.re[x] = 0
        objDFT.im[x] = 0
    objDFT.re[1] = 10
    objDFT.re[objDFT.length -1] = 10

# Forward polar transform
def test():
    mydft = DFT(128, acqu_test)
    mydft.run(POLAR)
    polarprint(mydft)

# Forward polar decibel transform
def dbtest():
    mydft = DFT(128, acqu_test)
    mydft.run(DB)
    polarprint(mydft)

# Reverse transform
def trev():
    mydft = DFT(128, revtest)
    mydft.run(REVERSE)
    cartesian_print(mydft)
