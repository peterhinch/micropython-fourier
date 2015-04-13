# window.py Window function
# Author: Peter Hinch
# 7th April 2015
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
    data(2, 0xEE07, 0x3A10) # vmov	s14, r3
    data(2, 0xEEF8, 0x7AC7) # fsitos s15, s14 zero f15
    label(LOOP1)
    data(2, 0xED90, 0x7A00) # vldr	s14, [r0]
    data(2, 0xEE77, 0x7A27) # vadds s15, s14, s15
    add(r0, 4)
    sub(r2, 1)
    bgt(LOOP1)
    pop({r0, r2})
    data(2, 0xEE07, 0x2A10) # vmov	s14, r2
    data(2, 0xEEB8, 0x7AC7) # fsitos s14, s14 convert to float
    data(2, 0xEEC7, 0x6A87) # vdiv  s13, s15, s14 avg. in s13
    label(LOOP)
    data(2, 0xED90, 0x7A00) # vldr	s14, [r0]
    data(2, 0xEE77, 0x7A66) # vsub  s15, s14, s13
    data(2, 0xED91, 0x7A00) # vldr	s14, [r1]
    data(2, 0xEE67, 0x7A27) # vmul  s15, s14, s15
    data(2, 0xEDC0, 0x7A00) # vstr	s15, [r0]
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
    label(LOOP)
    data(2, 0xEE07, 0x1A10) # vmov	s14, r1
    data(2, 0xEEF8, 0x7AC7) # fsitos s15, s14
    data(2, 0xEDC0, 0x7A00) # vstr	s15, [r0]
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
    data(2, 0xED90, 0x7A00) # vldr  s14, [r0]
    data(2, 0xEEF8, 0x7AC7) # fsitos s15, s14
    data(2, 0xEDC1, 0x7A00) # vstr  s15, [r1]
    add(r0, 4)
    add(r1, 4)
    sub(r2, 1)
    bgt(LOOP)
