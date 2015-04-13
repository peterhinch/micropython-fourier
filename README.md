Single precision FFT written in ARM assembler
=============================================

V0.3 13th April 2015  
Author: Peter Hinch  

Overview
--------

The `DFT` class is intended to perform a fast discrete fourier transform on an array of data typically received from a sensor. Apart from initialisation most of the code is written in ARM assembler for speed. It uses the floating point coprocessor and does not allocate heap storage: it can therefore be called from a MicroPython interrupt handler. It performs a 256 sample conversion in 2.5mS. This compares with 115mS for a floating point conversion in pure Python and 90mS using the native code emitter. A 1024 point conversion takes 12mS (vs 9mS on a Cray 1!). The DFT is performed using the Cooley-Tukey algorithm for arrays of length 2**N with the "twiddle factors" precomputed in Python. The algorithm performs the conversion in place to minimise RAM usage. Inverse transforms and fast Cartesian to polar conversion are supported.

The use of window functions is supported along with an option to convert polar magnitudes to dB.

Limitations
-----------

This code effectively replaces my integer based converter: the ARM FPU is sufficiently fast that integer code offers no discernable speed advantage. The use of floating point avoids the problems with scaling and loss of precision which become apparent when integers are used for transforms with more than 256 bins.  
If `adc.read_timed()` is to be used for data acquisition, you should use a firmware build dated 24th March 2015 or later. Note that read_timed() blocks until completion but is designed to work up to about a 750KHz sample rate.  
Conversion from Cartesian to polar is performed in assembler using an approximation to the `math.atan2()` function. Its accuracy is of the order of +-0.085 degrees.

Getting Started
---------------

The first step is to determine how to populate the real data array. If you are using the Pyboard and intend to use an onboard ADC, one option is to use the ADC's read_timed() method. This can acquire data at high speed but has the drawack of blocking for the duration of the read. Its use is supported by the DFTADC class:

```python
from dftclass import DFTADC, POLAR
mydft = DFTADC(128, "X7")
mydft.run(POLAR, 0.1) # Acquire data for 0.1 secs and convert: values are in mydft.re and mydft.im
```

Where the data is to be acquired by other means you will need to instantiate a `DFT` object and provide a function to populate its `re` array. For synthetic data this is straightforward. Data from sensors is usually in the form of integers which will need to be converted to floats. While this is trivial in Python, if speed is critical the `icopy` function can copy and convert an integer array to one of floats (see the `DFTADC` class). The test programs `dftadc.py` and `dfttest.py` provide examples, the latter showing the use of synthetic data.

File | Purpose |
-----|-------- |
dftadc.py   | Demo program using the DAC to generate analog data passed to the ADC |
dfttest.py  | Demo with synthetic data |
dft.py      | The fft implementation. |
dftclass.py | Python interface. |
window.py   | Assembler code to initialise an array and to multiply two 1D arrays. |
polar.py    | Cartesian to polar conversion. Includes fast atan2 approximation. |
ctrlmap.ods | Structure of the control array |
algorithms.py | Pure Python DFT used as basis for asm code. |

dftadc.py also illustrates the use of a window function.

Output Scaling for Forward Transforms
-------------------------------------

Forward transforms assume real data: you only need to populate the real array, the imaginary array being zeroed before a conversion is performed. By default values are scaled by the transform length to produce mathematically correct values. The scaling may be altered from the default of 1/length by means of the `DFT` class `scale()` method.  

Option | Result |
-------|------- |
FORWARD | Normal forward transform. |
POLAR | Results are converted to polar coordinates with the magnitude in the DFT object's re array and the phase in im. Phase is in radians in a form compatible with `math.atan2()`. |

Reverse Transforms
------------------

These accept complex data so your `populate()` function must initialise the DFT object's `re` and `im` arrays. The `revtest()` function in `dfttest.py` provides an example of this. The result is a set of complex vales.

Implementation
--------------

The DFT constructor creates and initialises three member float arrays, `re`, `im`, and `cmplx` and an integer array `ctrl`. The first two store the real and imaginary parts of the input and output data: for a 256 bin transform each will use 1KB of RAM. The `ctrl` and `cmplx` arrays are small (total size of the order of 120 bytes, size of the latter varies slightly with transform length) and contains data used by the transform itself, including a one-off calculation of the roots of unity (twiddle factors). There is no need to access this data. The constructor is pure Python as it is assumed that the speed of initialisation is not critical. The `run()` member function which performs the transform uses assembler for iterative routines apart from dB conversion in an attempt to optimise performance.

Note for beginners
------------------

This README does assume some familiarity with sampling theory and the DFT. It is worth noting that, in any sampled data system, precautions need to be taken to prevent a phenomenon known as aliasing. If you read the ADC at 1mS intervals, the maximum frequency which can be extracted from the set of samples is 500Hz. If signals above this frequency are present in the input analog signal, these will incorrectly appear as signals below this frequency. This is a fundamental property of all sampled data systems and you need to ensure that such signals are removed. Typically this is performed by a combination of analog and digital filtering.

