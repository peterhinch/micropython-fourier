# dftbench.py Demo/test program for DFT.
# Author: Peter Hinch
# 5th October 2019
# Released under the MIT license.

from dftclass import DFTADC, FORWARD

print('''
This acquires data from ADC on pin X7 and performs a 1024 point forward tarnsform.
The time from completion of data acquisition to completion of the transform is
measured and printed. The voltage on the ADC input is immaterial as we discard the
results of the transform.

''')

mydft = DFTADC(1024, 'X7')  # Use default timer 6

dt = mydft.run(FORWARD, 0.1)
print('Time for 1024 point forward transform: {}μs.'.format(dt))

