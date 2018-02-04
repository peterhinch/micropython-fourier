# dfttest.py Test DFT with synthetic data
# Author: Peter Hinch
# 11th April 2015

import math
from dftclass import DFT, FORWARD, REVERSE, POLAR, DB

def print_tests():
    st = '''Synthetic data tests for dftclass.
Available tests:
forward() Forward transform. Output in bins 0, 4.
test()  Forward polar transform. Output in bins 0, 4.
dbtest()  dB conversion of above.
trev()  Test reverse transform. Single cosine wave.
'''
    print('\x1b[32m')
    print(st)
    print('\x1b[39m')

print_tests()

def printexp(exp):
    print('Expected output:')
    print('\x1b[32m')
    print(exp)
    print('\x1b[39m')

def cartesian_print(objDFT):
    for x in range(objDFT.length):
        print("{:6d}{:8.2f}{:8.2f}j".format(x, objDFT.re[x], objDFT.im[x]))

def polarprint(objDFT):
    print("Polar: mag      phase (degs)")
    for x in range(objDFT.length//2): # Only the first half is valid
        print("{:6d}{:8.2f}  {:8.2f}".format(x, objDFT.re[x], int(math.degrees(objDFT.im[x]))))

# Data acquisition functions. For forward transforms only the real array is populated.

def acqu_test(objDFT):  # Populate with computed sinewave for forward transform
    for x in range(objDFT.length):
        objDFT.re[x] = 10 + 10*math.sin(8*math.pi*x/objDFT.length)

def revtest(objDFT):  # Populate with frequency domain data for reverse transform
    for x in range(objDFT.length):
        objDFT.re[x] = 0
        objDFT.im[x] = 0
    objDFT.re[1] = 10
    objDFT.re[objDFT.length -1] = 10

# Forward transform
def forward():
    printexp('''Bin 0 real 10.00 imag 0.00j
Bin 4 real 0.00 imag -5.00j.''')
    mydft = DFT(128, acqu_test)
    mydft.run(FORWARD)
    cartesian_print(mydft)

# Forward polar transform
def test():
    printexp('''Bin 0 magnitude 10 phase 0.
Bin 4 magnitude 5 phase -89.''')
    mydft = DFT(128, acqu_test)
    mydft.run(POLAR)
    polarprint(mydft)

# Forward polar decibel transform
def dbtest():
    printexp('''Bin 0 20dB phase 0.
Bin 4 magnitude 13.98dB phase -89.''')
    mydft = DFT(128, acqu_test)
    mydft.run(DB)
    polarprint(mydft)

# Reverse transform
def trev():
    printexp('Single cosine wave amplitude 20.')
    mydft = DFT(128, revtest)
    mydft.run(REVERSE)
    cartesian_print(mydft)
