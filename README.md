Single precision FFT written in ARM assembler
=============================================

V0.51 4th Feb 2018  
Author: Peter Hinch  
Requires: ARM platform with FPU (e.g. Pyboard). Any firmware version dated
after end of 2015.  

# 1. Overview

The `DFT` class is intended to perform a fast discrete fourier transform on an
array of data typically received from a sensor. Apart from initialisation most
of the code is written in ARM assembler for speed. It uses the floating point
coprocessor and does not allocate heap storage: it can therefore be called from
a MicroPython interrupt handler. It performs a 256 sample conversion in 2.5mS.
This compares with 115mS for a floating point conversion in pure Python and
90mS using the native code emitter. A 1024 point conversion takes 12mS.

The DFT is performed using the Cooley-Tukey algorithm. This requires arrays of
length 2**N where N is an integer. The "twiddle factors" are precomputed in
Python. The algorithm performs the conversion in place to minimise RAM usage
(i.e. the results appear in the same arrays as the source data).

Inverse transforms and fast Cartesian to polar conversion are supported, as is
the use of window functions. There is an option to convert polar magnitudes to
dB.

# 2. Limitations

This code effectively replaces my integer based converter: the ARM FPU is so
fast that integer code offers no speed advantage. The use of floating point
avoids problems with scaling and loss of precision which become apparent when
integers are used for transforms with more than 256 bins.

`adc.read_timed()` may be used for data acquisition. It blocks until completion
but is designed to work up to about a 750KHz sample rate.

Conversion from Cartesian to polar is performed in assembler using an
approximation to the `math.atan2()` function. Its accuracy is of the order of
+-0.085 degrees.

# 3. Getting Started

The first step is to determine how to populate the real data array. If you are
using the Pyboard and intend to use an onboard ADC, one option is to use the
ADC's `read_timed()` method. This can acquire data at high speed but has the
drawack of blocking for the duration of the read. Its use is supported by the
`DFTADC` class:

```python
from dftclass import DFTADC, POLAR
mydft = DFTADC(128, "X7")
 # Acquire data for 0.1 secs and convert
mydft.run(POLAR, 0.1)  # values are in mydft.re and mydft.im
```

Where the data is to be acquired by other means you will need to instantiate a
`DFT` object and provide a function to populate its `re` array. For synthetic
data this is straightforward. Data from sensors is usually in the form of
integers which will need to be converted to floats. While this is trivial in
Python, if speed is critical the `window.icopy` function can copy and convert
an integer array to one of floats (see the `DFTADC` class). The test programs
`dftadc.py` and `dfttest.py` provide examples, the latter showing the use of
synthetic data.

File | Purpose |
-----|-------- |
dftadc.py   | Demo program using the DAC to generate analog data passed to the ADC |
dftadc_tests.py | Further ADC demos showing window function etc. |
dfttest.py  | Demo with synthetic data |
dft.py      | The fft implementation. |
dftclass.py | Python interface. Requires `polar.py`, `window.py`, `dft.py`. |
window.py   | Assembler code to initialise an array and to multiply two 1D arrays. |
polar.py    | Cartesian to polar conversion. Includes fast atan2 approximation. |
ctrlmap.ods | Describes structure of the control array. |
algorithms.py | Pure Python DFT used as basis for asm code. |

Test programs `dftadc.py` and `dfttest.py` provide means of demonstrating the
code with ADC and synthetic data respectively. `dftadc.py` also illustrates the
use of a window function.

Test programs require `dft.py`, `dftclass.py`, `polar.py`, and `window.py`.
Note that `dft.py` cannot be frozen as bytecode because of it use of assembler.

# 4. The DFT class

This is the interface to the conversion. The constructor takes the following
arguments:  
 1. `length` Mandatory. Integer. The conversion length. Must be an integer
 power of 2.
 2. `popfunc=None` An optional function to populate the real array.
 3. `winfunc=None` An optional window function.

Method:  
 * `run` Mandatory arg: `conversion`. Specifies the conversion type. See below.

Property:  
 * `scale` Integer. The consructor provides a default scaling factor `1/length`
 which may be modified prior to executing `run`.

User-accessible bound variables:  
 * `re` Real data array. Elements are of type `float`.
 * `im` Iaginary data array. Elements are of type `float`.
 * `length` Integer. The transform length.
 * `dboffset` Float. Offset for dB conversion. See section 4.7.

# 4.1 Conversion types

These constants in `dftclass.py` are passed to `DFT.run()` and define the
conversion to be performed. The following are the options, described in detail
below:

Option | Result |
-------|------- |
FORWARD | Normal forward transform. See 4.4 below. |
REVERSE | Perform a reverse transform. See 4.5 below. |
POLAR | Forward transform with results as polar coordinates. See 4.6. |
DB | As per POLAR but magnitude is converted to dB. See 4.7. |

# 4.2 The populate function

This optional function is called each time `run` is executed. Its purpose is to
populate the `re` data array, possibly by accessing hardware. It receives the
`DFT` instance as its arg. Any return value is ignored. Any windowing is
applied after it returns.

# 4.3 The window function

This optional function takes two arguments:
 * `x` Point number (0 <= number < length).
 * `length` Transform length.

It should return the window function value for the specified point. Normally
in range 0-1.0.

# 4.4 FORWARD transform

Forward transforms assume real data: you only need to populate the real array.
The imaginary array is zeroed by `DFT.run()` before a conversion is performed.
By default values are scaled by the transform length to produce mathematically
correct values. The scaling may be altered from the default of `1/length` by
means of the `DFT` class `scale` property.

The result is complex data in the DFT object's `re` and `im` arrays.

# 4.5 REVERSE transform

These accept complex data in the DFT object's `re` and `im` arrays. If you use
a `populate()` function it must initialise both arrays. The `revtest()`
function in `dfttest.py` provides an example of this.

The conversion result comprises complex data in the DFT object's `re` and `im`
arrays.

# 4.6 POLAR transform

This is a forward transform with results converted to polar coordinates.

On completion the magnitude is in the DFT object's `re` array and the phase is
in `im`. Phase is in radians in a form compatible with `math.atan2()`.

For performance only the first half of `re` and `im` arrays are converted. The
complex conjugates are ignored.

# 4.7 DB transform

This is a forward transform with results converted to polar coordinates. The
magnitude is converted to dB. Magnitudes are scaled by adding the `dboffset`
bound variable. Mgnitudes <= 0.0 are returned as -80dB. 

On completion the magnitude is in the DFT object's `re` array and the phase is
in `im`. Phase is in radians in a form compatible with `math.atan2()`.

For performance only the first half of `re` and `im` arrays are converted. The
complex conjugates are ignored.

# 5 Class DFTADC

This supports input from a Pyboard ADC using `pyb.Timer.read_timed`. Its base
class is `DFT`.

Costructor. This takes the following args:
 1. `length` Mandatory. Integer defining transform length.
 2. `adcpin` Mandatory. This may take an ADC instance or an object capable of
 defining one e.g. `'X7'` or `pyb.Pin.board.X19`.
 3. `winfunc=None` Window function. See section 4.3.
 4. `timer=6` Can take a `pyb.Timer` instance or a timer no. Defines the timer
 used for data acquisition.

The constructor sets the `dboffset` bound variable so that the scaling is such
that 0dB corresponds to a 1V RMS sinewave applied to the Pyboard ADC (with
suitable DC bias). This only affects `DB` conversions.

Method.  
 * `run` Mandatory args: `conversion`, `duration`.

`conversion` must be one of the forward conversion types defined in section
4.1.  
`duration` Integer or float. Acquisition duration in seconds.

`run` will block for the duration.

In the case of `DB` conversions scaling may be modified by altering the
`dboffset` bound variable.

# 6. Implementation

The DFT constructor creates and initialises three member float arrays, `re`,
`im`, and `cmplx` and an integer array `ctrl`. The first two store the real
and imaginary parts of the input and output data: for a 256 bin transform
each will use 1KB of RAM. The `ctrl` and `cmplx` arrays are small (total size
of the order of 120 bytes, size of the latter varies slightly with transform
length) and contains data used by the transform itself, including a one-off
calculation of the roots of unity (twiddle factors). There is no need to
access this data. The constructor is pure Python as it is assumed that the
speed of initialisation is not critical. The `run()` member function which
performs the transform uses assembler for iterative routines in an attempt to
optimise performance. The one exception is dB conversion of the result which
is in Python.

# 7. Note for beginners

This README does assume some familiarity with sampling theory and the DFT. It
is worth noting that, in any sampled data system, precautions need to be taken
to prevent a phenomenon known as aliasing. If you read the ADC at 1mS
intervals, the maximum frequency which can be extracted from the set of samples
is 500Hz. If signals above this frequency are present in the input analog
signal, these will incorrectly appear as signals below this frequency. This is
a fundamental property of all sampled data systems and you need to ensure that
such signals are removed. Typically this is performed by a combination of
analog and digital filtering.

# 8. A whimsical observation

At one time a 1024 point DFT was widely used as a computer benchmark. As such
they were implemented in highly optimised assembler. I can't make this claim:
my code could be significantly imporoved. But it does it in 12mS on a Pyboard
costing £28.

One of the first supercomputers, a Cray 1, took 9mS. It cost a king's ransom.
