# dftadc.py Demo/test program for DFT.
# Author: Peter Hinch
# 4th Feb 2018
# Acquires samples from the ADC on pin X7.
# Generates a waveform on pin X5: link X5-X7 to test

import array
import math
import pyb
from dftclass import DFTADC, DB

def polarprint(objDFT):
    print("Polar: mag (dB) phase (degs)")
    fstr = "{:6d}{:8.2f}   {:8.2f}"
    for x in range(objDFT.length//2):  # Only the first half is valid
        print(fstr.format(x, objDFT.re[x], int(math.degrees(objDFT.im[x]))))

# ************************** Output waveform generator *********************
# Sinewave amplitude 3.25*127/255 = 1.68Vpk
# = 20*log10((3.25*127/255)/sqrt(2)) = 1.17dB relative to 1VRMS

OSLEN = const(100)
outputsamples = bytearray(128+int(127*math.cos(2*math.pi*x/OSLEN)) for x in range(OSLEN))

dac = pyb.DAC(1)  # Pin X5
tim = pyb.Timer(4)
tim.init(freq=10000)  # 100Hz sinewave

dac.write_timed(outputsamples, tim, mode=pyb.DAC.CIRCULAR)

# ******************************* Input test *******************************

print('''Issue dftadc.test()

Expected result:
bin 0 contains the DC offset.
bin 10 (sampling 100Hz for 100mS) should contain about +1dB with random phase.
''')

mydft = DFTADC(128, 'X7')  # Use default timer 6

def test():
    mydft.run(DB, 0.1)
    polarprint(mydft)
