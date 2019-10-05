# dftclass.py Python interface for FFT assembler code
# Author: Peter Hinch

# 5th Feb 2018
# PYBOARD_DBOFFSET calculation.
# dB default scaling is relative to 1.0VRMS on Pyboard. Assume a 1VRMS sinewave.
# Appropriate DC bias is assumed and does not affect calculation below.
# 1.0VRMS = 1.414VP. ADC full scale = 4095 @ 3.25V. Hence ADC will output
# a peak value 0f 4095*1.414/3.25 = 1782.
# DB conversions ignore the conjugates. So the peak value in the frequency bins
# in the 1st half of the array will be 1782/2 = 891. Hence
# dB offset = round(20*math.log10(891)) = 59

PYBOARD_DBOFFSET = const(59)
import array
import math
import pyb
from dft import fft
from uctypes import addressof
from window import winapply, setarray, icopy
from polar import topolar
import utime

# Control: on entry r1 should hold one of these values to determine the direction and scaling
# of the transform. Only bit 0 now used by fft()
REVERSE = const(0)      # Inverse transform (frequency to time domain)
FORWARD = const(1)      # Forward transform
POLAR   = const(3)      # bit 2: Polar conversion
DB      = const(7)      # bit 3: Polar with dB conversion

# Instantiating the class creates the real, imaginary and control arrays, populates real and imaginary
# with zero. Populates the control array with these values:
# ctrl[0] = length of data array
# ctrl[1] = no. of bits to represent the length
# ctrl[2] = Address of real data array
# ctrl[3] = Address of imaginary data array
# ctrl[4] = Byte Offset into entry 0 of complex roots of unity
# ctrl[5] = Address of scratchpad for use by fft code
# After this is an array of seven complex nos followed by one for the roots of unity.
# The first complex no. is initialised to the initial u value. The rest make up a scratchpad used by fft()
# see ctrlmap.ods for more detail.

class DFT(object):
    def __init__(self, length, popfunc=None, winfunc=None):
        bits = round(math.log(length)/math.log(2))
        assert 2**bits == length, "Length must be an integer power of two"
        self.dboffset = 0               # Offset for dB calculation
        self._length = length
        self.popfunc = popfunc          # Function to acquire data
        self.re = array.array('f', (0 for x in range(self._length)))
        self.im = array.array('f', (0 for x in range(self._length)))
        if winfunc is not None:  # If a window function is provided, create and populate the array
            self.windata = array.array('f', (0 for x in range(self._length))) # of window coefficients
            for x in range(0, length):
                self.windata[x] = winfunc(x, length)
        else:
            self.windata = None
        COMPLEX_NOS = 7                 # Size of complex buffer area before roots of unity
        ROOTSOFFSET = COMPLEX_NOS*2     # Word offset into complex array of roots of unity
        bits = round(math.log(self._length)/math.log(2))
        self.ctrl = array.array('i', [0]*6)
        self.cmplx = array.array('f', [0.0]*((bits +1 +COMPLEX_NOS)*2))
        self.ctrl[0] = self._length
        self.ctrl[1] = bits
        self.ctrl[2] = addressof(self.re)
        self.ctrl[3] = addressof(self.im)
        self.ctrl[4] = COMPLEX_NOS*8    # Byte offset into complex array of roots of unity
        self.ctrl[5] = addressof(self.cmplx) # Base address

        self.cmplx[0] = 1.0             # Initial value of u = [1 +j0]
        self.cmplx[1] = 0.0             # Intermediate values are used by fft() and not initialised
        self.cmplx[12] = 1.0/self._length # Default scaling multiply by 1/length
        self.cmplx[13] = 0.0            # ignored
        i = ROOTSOFFSET
        creal = -1
        cimag =  0
        self.cmplx[i] = creal           # Complex roots of unity
        self.cmplx[i +1] = cimag
        i += 2
        for x in range(bits):
            cimag = math.sqrt((1.0 - creal) / 2.0)  # Imaginary part
            self.cmplx[i +1] = cimag
            creal = math.sqrt((1.0 + creal) / 2.0)  # Real part
            self.cmplx[i] = creal
            i += 2

    @property
    def scale(self):
        return self.cmplx[12]

    @scale.setter
    def scale(self, value):             # Allow user to override default
        self.cmplx[12] = value

    @property
    def length(self):
        return self._length  # Read only

    def run(self, conversion):          # Uses assembler for speed
        if self.popfunc is not None:
            self.popfunc(self)          # Populate the data (for fwd transfers, just the real data)
        if conversion != REVERSE:       # Forward transform: real data assumed
            setarray(self.im, 0, self._length)# Fast zero imaginary data
            if self.windata is not None:  # Fast apply the window function
                winapply(self.re, self.windata, self._length)
        start = utime.ticks_us()
        fft(self.ctrl, conversion)
        delta = utime.ticks_diff(utime.ticks_us(), start)
        if (conversion & POLAR) == POLAR: # Ignore complex conjugates, convert 1st half of arrays
            topolar(self.re, self.im, self._length//2) # Fast
            if conversion == DB:        # Ignore conjugates: convert 1st half only
                for idx, val in enumerate(self.re[0:self._length//2]):
                    self.re[idx] = -80.0 if val <= 0.0 else 20*math.log10(val) - self.dboffset
        return delta
# Subclass for acquiring data from Pyboard ADC using read_timed() method.

class DFTADC(DFT):
    def __init__(self, length, adcpin, winfunc=None, timer=6):
        super().__init__(length, winfunc = winfunc)
        self.buff = array.array('i', (0 for x in range(self._length)))
        if isinstance(adcpin, pyb.ADC):
            self.adc = adcpin
        else:
            self.adc = pyb.ADC(adcpin)
        if isinstance(timer, pyb.Timer):
            self.timer = timer
        else:
            self.timer = pyb.Timer(timer)
        self.dboffset = PYBOARD_DBOFFSET # Value for Pyboard ADC

    def run(self, conversion, duration):
        tim = self.timer
        tim.deinit()
        tim.init(freq = int(self._length/duration))
        self.adc.read_timed(self.buff, tim) # Note: blocks for duration
        start = utime.ticks_us()
        icopy(self.buff, self.re, self._length) # Fast copy integer array into real
        super().run(conversion)
        return utime.ticks_diff(utime.ticks_us(), start)
