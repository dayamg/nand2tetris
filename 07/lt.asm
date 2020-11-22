/// returns 1 iff *SP < *(SP-1), and 0 otherwise, , i.e., true iff y < x
@R0
AM=M-1  /// go to *SP
D=M /// D=y

@R13
M=D /// R[13]=y

@YNEGLTi
D;JLT /// if D<0, jump to y negative (YNEG)

@R15 /// else, keep sign of D as +
M=1

(PARSEXLTi)
/// SP--
@R0
AM=M-1  /// go to --SP
D=M /// D=*SP=x
@R14
M=D /// R[14]=x

@XNEGLTi
D;JLT /// if x<0, jump to y negative (XNEGLTi)

@R15
MD=M-1  /// sign of x: 1, so calculate R15 = sign(y)-sign(x), D = sign(y)-sign(x)

(CHECKSIGNLTi)
@RETURNTRUELTi
D;JGT /// if D = sign(y)-sign(x) > 0, then y > x, so return FALSE

@RETURNFALSELTi
D;JLT /// if D = sign(y)-sign(x) < 0, then y < x, so return TRUE

/// Else, we need to compare x and y, and as they are the same sign, there are no overflow problems
@R14
D=M  /// D = x
@R13 /// M = y
D=M-D /// D = y - x

@RETURNTRUELTi
D;JGT /// if D = y - x > 0, then y > x, so return FALSE

@RETURNFALSELTi
D;JEQ /// if D = y - x = 0, then y = x, so return FALSE

@RETURNFALSELTi
D;JLT /// if D = y - x < 0, then y < x, so return TRUE
@ENDLTi
0;JMP

(YNEGLTi)
@R15 /// keep R15 = sign of y = -1
M=-1
@PARSEXLTi
0;JMP /// continue parsing the value of x

(XNEGLTi)
@R15
MD=M+1  /// sign of x: -1, so calculate R15 = sign(y)-sign(x)
@CHECKSIGNLTi
0;JMP /// next: check if both are with the same sign

(RETURNFALSELTi)
@R0
A=M
M=0
@ENDLTi
0;JMP

(RETURNTRUELTi)
@R0
A=M
M=-1

(ENDLTi)
@R0
M=M+1  /// SP++