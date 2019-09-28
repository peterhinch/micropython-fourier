# dfttest.py Test DFT with synthetic data
# Author: Peter Hinch
# 5th Feb 2018

import math
from dftclass import DFT, FORWARD, REVERSE, POLAR, DB

# *********************** Pretty print **********************

def print_tests():
    st = '''Synthetic data tests for dftclass.
Available tests:
forward() Forward transform. Output in bins 0, 4.
test()  Forward polar transform. Output in bins 0, 4.
dbtest()  dB conversion of above.
dbhann()  Test of hanning (hann) window.
trev()  Test reverse transform. Single cosine cycle.
bench() Benchmark: time a 1K forward transform.
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
    print("Bin       real  imaginary")
    fstr = "{:6d}{:8.2f}{:8.2f}j"
    for x in range(objDFT.length):
        print(fstr.format(x, objDFT.re[x], objDFT.im[x]))

def polarprint(objDFT):
    print("Polar:     mag    phase (degs)")
    fstr = "{:6d}{:8.2f}  {:8.2f}"
    for x in range(objDFT.length//2): # Only the first half is valid
        print(fstr.format(x, objDFT.re[x], int(math.degrees(objDFT.im[x]))))

# ******************** Support functions ********************

# The hann (hanning) window has a -6dB coherent gain. So the function is
# here multiplied by 2 to offset this
def hann(x, length):
    return 1 - math.cos(2*math.pi*x/(length - 1))

# Data acquisition functions.
# For forward transforms only the real array is populated.

# Populate with computed sinewave for forward transform (bin 4)
def acqu_test(objDFT):
    for x in range(objDFT.length):
        objDFT.re[x] = 1 + 2*math.sin(8*math.pi*x/objDFT.length)

# Populate with computed sinewave for forward transform (bin 40)
def acqu_test40(objDFT):
    for x in range(objDFT.length):
        objDFT.re[x] = 1 + 2*math.sin(80*math.pi*x/objDFT.length)

# Populate with frequency domain data for reverse transform
def revtest(objDFT):
    for x in range(objDFT.length):
        objDFT.re[x] = 0
        objDFT.im[x] = 0
    objDFT.re[1] = 10
    objDFT.re[objDFT.length -1] = 10

# ************************** TESTS **************************

# Forward transform
def forward():
    printexp('''Bin 0 real 1.00 imag 0.00j
Bin 4 real 0.00 imag -1.00j.''')
    mydft = DFT(128, acqu_test)
    mydft.run(FORWARD)
    cartesian_print(mydft)

# Forward polar transform
def test():
    printexp('''Bin 0 magnitude 1.00 phase 0.00.
Bin 4 magnitude 1.00 phase -89.00''')
    mydft = DFT(128, acqu_test)
    mydft.run(POLAR)
    polarprint(mydft)

# Forward polar decibel transform
def dbtest():
    printexp('''Bin 0 0dB phase 0.
Bin 4 magnitude 0dB phase -89.''')
    mydft = DFT(128, acqu_test)
    mydft.run(DB)
    polarprint(mydft)

# Forward polar decibel transform (hann window, 0dB coherent power gain)
def dbhann():
    printexp('''Bin 39 -5.99dB phase 88.
Bin 40 magnitude -0.07dB phase -89.
Bin 41 magnitude -5.99dB phase 91''')
    mydft = DFT(128, acqu_test40, hann)
    mydft.run(DB)
    polarprint(mydft)

# Reverse transform
def trev():
    printexp('Single cosine wave amplitude 20.')
    mydft = DFT(128, revtest)
    mydft.run(REVERSE)
    cartesian_print(mydft)

# 1K point benchmark
def bench():
    printexp('''Bin 0 real 1.00 imag 0.00j
Bin 4 real 0.00 imag -1.00j.''')
    mydft = DFT(1024, acqu_test)
    t = mydft.run(FORWARD)
    cartesian_print(mydft)
    print('Time for 1K DFT = {}μs'.format(t))
