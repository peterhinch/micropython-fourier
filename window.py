# window.py Window function
# Author: Peter Hinch
# 20th April 2015
# Now uses FPU mnemonics. Tests complete.
# Floating point version
# Applies a window function to an array of real samples before performing a DFT.
# removes the DC (zero frequency) component by averaging the sample set and
# subtracting from each sample, before multiplying the sample by the corrsponding
# coefficient and storing the result in the sample array.
# The coefficient array is unchanged.

import array, math

# Multiply each element in array 0 by the corresponding one in array 1, returning the
# result in array 0.
# r0: array 0 real data
# r1: array 1 window coefficients
# r2: length of arrays

@micropython.asm_thumb
def winapply(r0, r1, r2):
    push({r0, r2})
    mov(r3, 0)
    vmov(s14, r3)
    vcvt_f32_s32(s15, s14)  # s15 holds value to set
    label(LOOP1)
    vldr(s14, [r0, 0])
    vadd(s15, s14, s15)
    add(r0, 4)
    sub(r2, 1)
    bgt(LOOP1)
    pop({r0, r2})
    vmov(s14, r2)
    vcvt_f32_s32(s14, s14)  # convert array length to float
    vdiv(s13, s15, s14)     # avg. in s13
    label(LOOP)
    vldr(s14, [r0, 0])
    vsub(s15, s14, s13)
    vldr(s14, [r1, 0])
    vmul(s15, s14, s15)
    vstr(s15, [r0, 0])
    add(r0, 4)
    add(r1, 4)
    sub(r2, 1)
    bgt(LOOP)

# Set all elements of a float array to an integer value
# r0: the array
# r1: value
# r2: length of array
@micropython.asm_thumb
def setarray(r0, r1, r2):
    vmov(s14, r1)
    vcvt_f32_s32(s15, s14)  # Value in s15
    label(LOOP)
    vstr(s15, [r0, 0])
    add(r0, 4)
    sub(r2, 1)
    bgt(LOOP)


# Copy elements of an integer array to a float array, converting
# r0: integer array
# r1: float array
# r2: length
@micropython.asm_thumb
def icopy(r0, r1, r2):
    label(LOOP)
    vldr(s14, [r0, 0])
    vcvt_f32_s32(s15, s14)
    vstr (s15, [r1, 0])
    add(r0, 4)
    add(r1, 4)
    sub(r2, 1)
    bgt(LOOP)
