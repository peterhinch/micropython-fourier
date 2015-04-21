# dftadc.py Demo/test program for DFT.
# Author: Peter Hinch
# 21st April 2015
# Acquires samples from the ADC on pin X7.
# Generates a waveform on pin X5: link X5-X7 to test

import array
import math
import pyb
from dftclass import DFTADC, FORWARD, REVERSE, POLAR, DB

import micropython
micropython.alloc_emergency_exception_buf(100)

def hanning(x, length):                 # Example of a window function
    return 0.54 - 0.46*math.cos(2*math.pi*x/(length-1))

def cartesian_print(objDFT):
    for x in range(objDFT.length):
        print("{:6d}{:8.2f}{:8.2f}j".format(x, objDFT.re[x], objDFT.im[x]))

def polarprint(objDFT):
    print("Polar: mag      phase (degs)")
    for x in range(objDFT.length//2):   # Only the first half is valid
        print("{:6d}{:8.2f}   {:8.2f}".format(x, objDFT.re[x], int(math.degrees(objDFT.im[x]))))

# ******************************* Output waveform generator **********************
# This is done using a callback rather than a circular timed write because the current
# MicroPython implementation doesn't support concurrent DAC and ADC timed operation.
# Consequently output frequency is limited.
# Sinewave amplitude 3.25*127/255 = 1.68Vpk
# = 20*log10((3.25*127/255)/sqrt(2)) = 1.17dB relative to 1VRMS

OSLEN = const(100)
outputsamples = array.array('i', [0]*OSLEN)
osindex = 0

for x in range(len(outputsamples)):
    outputsamples[x] = 128+int(127*math.cos(2*math.pi*x/OSLEN))

dac = pyb.DAC(1)                        # Pin X5
#dac.write(127) # bias half way
def cb(t):
    global osindex
    dac.write(outputsamples[osindex])
    osindex = (osindex +1) % OSLEN

tim = pyb.Timer(4, freq=10000)          # 100Hz sinewave
tim.callback(cb)

# ********************************************************************************

mydft = DFTADC(128, "X7")
# mydft = DFTADC(128, "X7", hanning)

# Expected result (without window function)
# bin 10 (sampling 100Hz for 100mS) should contain about +1dB with random phase
def test():
    mydft.run(DB, 0.1)
    polarprint(mydft)
