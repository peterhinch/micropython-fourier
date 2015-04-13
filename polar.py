# polar.py Fast floating point cartesian to polar coordinate conversion
# Author: Peter Hinch
# 10th April 2015

# Arctan is based on the following approximation applicable to octant zero where q = x/y :
# arctan(q) = q*pi/4- q*(q - 1)*(0.2447 + 0.0663*q)
# Arctan approximation: max error about 0.085 deg in my tests.

from math import pi
from array import array
consts = array('f', [0.0, 0.0, 1.0, pi, pi/2, -pi/2, pi/4, 0.2447, 0.0663])

# Entry:
# r0: array of real (x) values
# r1: array of imaginary (y) values
# r2: array element 0 = length of arrays following are constants
# ARM CPU register usage
# r3: Array length (integer)
# r4: Negate flag
# Returns:
# The real array holds magnitude values, the imaginary ones phase.
# Phase is in radians compatible with cPython's math.atan2()

@micropython.asm_thumb
def polar(r0, r1, r2):    # Array length in r3: convert to integer
    data(2, 0xEDD2, 0x7A00) # vldr	s15, [r2, 0]
    data(2, 0xEEFD, 0x7AE7) # ftosizs s15, s15
    data(2, 0xEE17, 0x3A90) # vmov	r3, s15
# Load constants
    data(2, 0xED92, 0x0A01) # vldr s0, [r2, 1] 0
    data(2, 0xEDD2, 0x0A02) # vldr s1, [r2, 2] 1
    data(2, 0xED92, 0x1A03) # vldr s2, [r2, 3] Pi
    data(2, 0xEDD2, 0x1A04) # vldr s3, [r2, 4] Pi/2
    data(2, 0xED92, 0x2A05) # vldr s4, [r2, 5] -Pi/2
    data(2, 0xEDD2, 0x2A06) # vldr s5, [r2, 6] Pi/4
    data(2, 0xED92, 0x3A07) # vldr s6, [r2, 7] 0.2447
    data(2, 0xEDD2, 0x3A08) # vldr s7, [r2, 8] 0.0663
    b(START)

    label(DOCALC)
    data(2, 0xED92, 0x4A01) # vldr s8, [r2, 1] c = 0.0
    data(2, 0xED90, 0x7A00) # vldr s14, [r0, 0] x
    data(2, 0xEDD1, 0x7A00) # vldr s15, [r1, 0] y
# Calculate magnitude
    data(2, 0xEE27, 0x5A07) # vmul s10, s14, s14
    data(2, 0xEE67, 0x4AA7) # vmul s9, s15, s15
    data(2, 0xEE35, 0x5A24) # vadd s10, s10, s9
    data(2, 0xEEB1, 0x5AC5) # vsqrt s10, s10
    data(2, 0xED80, 0x5A00) # vstr s10, [r0, 0] real = hypot

# Start of arctan calculation
    mov(r4, 0)              # Negate flag
    data(2, 0xEEB4, 0x7AC0) # vcmpe s14, s0
    data(2, 0xEEF1, 0xFA10) # vmrs transfer status to ARM status registers
    bne(QUADCHECK)          # Skip if not x == 0

    data(2, 0xEEF4, 0x7AC0) # vcmpe s15, s0
    data(2, 0xEEF1, 0xFA10) # vmrs transfer status to ARM status registers
    bne(P01)
    data(2, 0xED81, 0x0A00) # vstr	s0, [r1,0] result = 0
    b(Q0DONE)

    label(P01)
    data(2, 0xEEF4, 0x7AC0) # vcmpe s15, s0
    data(2, 0xEEF1, 0xFA10) # vmrs transfer status to ARM status registers
    ite(ge)
    data(2, 0xEDC1, 0x1A00) # vstr	s3, [r1,0] result = pi/2
    data(2, 0xED81, 0x2A00) # vstr	s4, [r1,0] result = -pi/2
    b(Q0DONE)
    
    label(QUADCHECK)
    data(2, 0xEEF4, 0x7AC0) # vcmpe s15, s0 compare y with 0
    data(2, 0xEEF1, 0xFA10) # vmrs transfer status to ARM status registers
    bge(P02)
    data(2, 0xEEF1, 0x7A67) # vneg s15, s15 y = -y
    mov(r4, 1)              # set negate flag
    label(P02)              # y now > 0
    data(2, 0xEEB4, 0x7AC0) # vcmpe s14, s0 comp x with 0
    data(2, 0xEEF1, 0xFA10) # vmrs transfer status to ARM status registers
    bge(P04)
                            # x < 0
    data(2, 0xEEB1, 0x7A47) # vneg r14, r14 x = -x
    data(2, 0xEEB4, 0x7AE7) # vcmpe s14, s15 comp x with y
    data(2, 0xEEF1, 0xFA10) # vmrs transfer status to ARM status registers
    bgt(P03)
    data(2, 0xEEB0, 0x6A47) # vmov s12, s14 swap x and y
    data(2, 0xEEB0, 0x7A67) # vmov s14, s15
    data(2, 0xEEF0, 0x7A46) # vmov s15, s12
    data(2, 0xEEB0, 0x4A61) # vmov s8, s3  c = pi/2
    b(OCTZERO)

    label(P03)              # y < x
    cmp(r4, 0)
    ite(eq)
    mov(r4, 1)
    mov(r4, 0)              # neg = not neg
    data(2, 0xEEB0, 0x4A41) # vmov s8, s2  c = pi
    data(2, 0xEEB1, 0x4A44) # vneg s8, s8  c = -pi
    b(OCTZERO)
    
    label(P04)              # x > 0
    data(2, 0xEEB4, 0x7AE7) # vcmpe s14, s15 comp x with y
    data(2, 0xEEF1, 0xFA10) # vmrs transfer status to ARM status registers
    bge(OCTZERO)
    data(2, 0xEEB0, 0x6A47) # vmov s12, s14 swap x and y
    data(2, 0xEEB0, 0x7A67) # vmov s14, s15
    data(2, 0xEEF0, 0x7A46) # vmov s15, s12
    data(2, 0xEEB0, 0x4A42) # vmov s8, s4  c = -pi/2
    cmp(r4, 0)
    ite(eq)
    mov(r4, 1)
    mov(r4, 0)              # neg = not neg
# Octant zero        
    label(OCTZERO)          # calculate r = x*pi/4 - x*(x - 1)*(0.2447 + 0.0663*x)
    data(2, 0xEE87, 0x7A87) # vdiv s14, s15, s14  x = y/x
    data(2, 0xEE63, 0x7A87) # vmul s15, s7, s14  s15 = 0.0663x
    data(2, 0xEE73, 0x7A27) # vadd s15, s6, s15 s15 = 0.2447 + 0.0663*x
    data(2, 0xEE77, 0x6A60) # vsub s13, s14, s1 s1 = x -1
    data(2, 0xEE67, 0x7AA6) # vmul s15, s15, s13 s15 = (x - 1)*(0.2447 + 0.0663*x)
    data(2, 0xEE67, 0x7A27) # vmul s15, s14, s15 s15 = x*(x - 1)*(0.2447 + 0.0663*x)
    data(2, 0xEE67, 0x6A22) # vmul s13, s14, s5 s5 = x*pi/4
    data(2, 0xEE76, 0x7AE7) # vsub s15, s13, s15

    data(2, 0xEE77, 0x7A84) # vadd s15, s15, s8 s15 += c
    cmp(r4, 0)
    it(ne)
    data(2, 0xEEF1, 0x7A67) # vneg r15, r15
    data(2, 0xEDC1, 0x7A00) # vstr s15, [r1, 0] imag = angle
    label(Q0DONE)
    bx(lr)                  # ! DOCALC

    label(START)            # r0-> real r1-> imag r3 = length
    bl(DOCALC) 
    add(r0, 4)
    add(r1, 4)
    sub(r3, 1)
    bne(START)

def topolar(re, im, length):
    consts[0] = length
    polar(re, im, consts)

