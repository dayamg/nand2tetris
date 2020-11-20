/// returns 1 iff *SP < *(SP-1), and 0 otherwise, , i.e., true iff y < x
@R0
A=M  /// go to *SP
D=M /// D=y

@R13
M=D /// R[13]=y

@YNEG
D;JLT /// if D<0, jump to y negative (YNEG)

@R15 /// else, keep sign of D as +
M=1

(PARSEX)
/// SP--
@R0
AM=M-1  /// go to --SP
D=M /// D=*SP=x
@R14
M=D /// R[14]=x

@XNEG
D;JLT /// if x<0, jump to y negative (XNEG)

@R15
M=M-1  /// sign of x: 1, so calculate R15 = sign(y)-sign(x)
(CHECKSIGN)
D=M /// D = sign(y)-sign(x)

@RETURNFALSE
D;JGT /// if D = sign(y)-sign(x) > 0, then y > x, so return FALSE

@RETURNTRUE
D;JLT /// if D = sign(y)-sign(x) < 0, then y < x, so return TRUE

/// Else, we need to compare x and y, and they are the same sign, so no overflow problems
@R14
D=M  /// D = x
@R13 /// M = y
D=M-D /// D = y - x

@RETURNFALSE
D;JGT /// if D = y - x > 0, then y > x, so return FALSE

@RETURNTRUE
D;JLT /// if D = y - x < 0, then y < x, so return TRUE

@END
0;JMP

(YNEG)
@R15 /// keep R15 = sign of y = -1
M=-1
@PARSEX
0;JMP /// continue parsing the value of x

(XNEG)
@R15
M=M+1  /// sign of x: -1, so calculate R15 = sign(y)-sign(x)
@CHECKSIGN
0;JMP /// check if both are with the same sign

(RETURNFALSE)
@R0
M=0
@END
0;JMP

(RETURNTRUE)
@R0
M=1

(END)
