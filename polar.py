# polar.py Fast floating point cartesian to polar coordinate conversion
# Author: Peter Hinch
# 31st Oct 2015 Updated to match latest firmware
# 21st April 2015
# Now uses recently implemented FPU mnemonics
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
# r5, r6: Temporary storage
# Returns:
# The real array holds magnitude values, the imaginary ones phase.
# Phase is in radians compatible with cPython's math.atan2()

@micropython.asm_thumb
def polar(r0, r1, r2):    # Array length in r3: convert to integer
    vldr(s15, [r2, 0])
    vcvt_s32_f32(s15, s15)
    vmov(r3, s15)
# Load constants
    vldr(s0, [r2, 4])       # 0
    vldr(s1, [r2, 8])       # 1
    vldr(s2, [r2, 12])       # Pi
    vldr(s3, [r2, 16])       # Pi/2
    vldr(s4, [r2, 20])       # -Pi/2
    vldr(s5, [r2, 24])       # Pi/4
    vldr(s6, [r2, 28])       # 0.2447
    vldr(s7, [r2, 32])       # 0.0663
    b(START)

    label(DOCALC)
    vldr(s8, [r2, 4])       # c = 0.0
    vldr(s14, [r0, 0])      # x
    vldr(s15, [r1, 0])      # y
# Calculate magnitude
    vmul(s10, s14, s14)
    vmul(s9, s15, s15)
    vadd(s10, s10, s9)
    vsqrt(s10, s10)
    vstr(s10, [r0, 0])      # real = hypot

# Start of arctan calculation
    mov(r4, 0)              # Negate flag
    vcmp(s14, s0)
    vmrs(APSR_nzcv, FPSCR)  # transfer status to ARM status registers
    bne(QUADCHECK)          # Skip if not x == 0

    vcmp(s15, s0)
    vmrs(APSR_nzcv, FPSCR)  # transfer status to ARM status registers
    bne(P01)
    vstr(s0, [r1,0])        # result = 0
    b(Q0DONE)

    label(P01)
    vcmp(s15, s0)
    vmrs(APSR_nzcv, FPSCR)  # transfer status to ARM status registers
    ite(ge)
    vstr(s3, [r1,0])        # result = pi/2
    vstr(s4, [r1,0])        # result = -pi/2
    b(Q0DONE)

    label(QUADCHECK)
    vcmp(s15, s0)           # compare y with 0
    vmrs(APSR_nzcv, FPSCR)
    bge(P02)
    vneg(s15, s15)          # y = -y
    mov(r4, 1)              # set negate flag
    label(P02)              # y now > 0
    vcmp(s14, s0)           # comp x with 0
    vmrs(APSR_nzcv, FPSCR)
    bge(P04)
                            # x < 0
    vneg(s14, s14)          # x = -x
    vcmp(s14, s15)          # comp x with y
    vmrs(APSR_nzcv, FPSCR)
    bgt(P03)
    vmov(r5, s14)          # swap x and y CONVOLUTED: need to implement vmov(Sd, Sm)
    vmov(r6, s15)
    vmov(s15, r5)
    vmov(s14, r6)
    vmov(r5, s3)
    vmov(s8, r5)            # c = pi/2
    b(OCTZERO)

    label(P03)              # y < x
    cmp(r4, 0)
    ite(eq)
    mov(r4, 1)
    mov(r4, 0)              # neg = not neg
    vmov(r5, s2)            # c = pi
    vmov(s8, r5)
    vneg(s8, s8)            # c = -pi
    b(OCTZERO)

    label(P04)              # x > 0
    vcmp(s14, s15)          # comp x with y
    vmrs(APSR_nzcv, FPSCR)
    bge(OCTZERO)
    vmov(r5, s14)          # swap x and y
    vmov(r6, s15)
    vmov(s15, r5)
    vmov(s14, r6)
    vmov(r5, s4)            # c = -pi/2
    vmov(s8, r5)
    cmp(r4, 0)
    ite(eq)
    mov(r4, 1)
    mov(r4, 0)              # neg = not neg
# Octant zero
    label(OCTZERO)          # calculate r = x*pi/4 - x*(x - 1)*(0.2447 + 0.0663*x)
    vdiv(s14, s15, s14)     #  x = y/x
    vmul(s15, s7, s14)      #  s15 = 0.0663x
    vadd(s15, s6, s15)      # s15 = 0.2447 + 0.0663*x
    vsub(s13, s14, s1)      # s1 = x -1
    vmul(s15, s15, s13)     # s15 = (x - 1)*(0.2447 + 0.0663*x)
    vmul(s15, s14, s15)     # s15 = x*(x - 1)*(0.2447 + 0.0663*x)
    vmul(s13, s14, s5)      # s5 = x*pi/4
    vsub(s15, s13, s15)

    vadd(s15, s15, s8)      # s15 += c
    cmp(r4, 0)
    it(ne)
    vneg(s15, s15)
    vstr(s15, [r1, 0])      # imag = angle
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
