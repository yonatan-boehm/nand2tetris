// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

@R14
D=M
@max
M=D // max points to arr[0]
@min
M=D // min points to arr[0]
@R15
D=M
@i
M=D-1 // i stores arr length

(LOOP)
    @i
    D=M
    @SWAP
    D;JEQ // jump to end if i=0

    // store current array value in variable
    @R14
    D=M // D points to arr[0]
    @i 
    D=D+M // D points to arr[i]
    @cur
    M=D // cur points to arr[i]

    // check if bigger than max
    @max
    A=M
    D=M
    @cur
    A=M
    D=D-M
    @UMAX // A stores UMAX (update max)
    D;JLT // jump to UMAX if cur > max

    // check if smaller than min
    @min
    A=M
    D=M
    @cur
    A=M
    D=D-M
    @UMIN // A stores UMIN (update min)
    D;JGT // jump to UMIN if cur < min

(UMAX)
    @cur
    D=M // store cur pointer in D
    @max
    M=D
    @CONT
    0;JMP

(UMIN)
    @cur
    D=M // store cur pointer in D
    @min
    M=D
    @CONT
    0;JMP

(CONT)
    @i
    M=M-1
    @LOOP
    0;JMP

(SWAP)
    @min
    A=M // A points to arr[min]
    D=M // D stores min value
    @temp
    M=D // temp stores min value
    @max
    A=M // A points to arr[max]
    D=M // D stores max value
    @min 
    A=M // A points to arr[min]
    M=D // arr[min] stores max value
    @temp
    D=M // D stores min value
    @max
    A=M // A points to arr[max]
    M=D // arr[max] stores min value

    @END
    0;JMP

(END)
    @END
    0;JMP