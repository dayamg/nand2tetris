
ADD_ASM = """
/// adds *SP + *(SP-1)
@R0
AM=M-1  /// go to *SP
D=M /// D = y

/// SP--
@R0
AM=M-1  /// go to --SP
D=M+D /// D = x + y

@R0
A=M  /// go to *SP
M=D  /// keep the result of add in *SP

@R0
M=M+1  /// SP++
"""

SUB_ASM = """
/// subtracts *SP - *(SP-1), x - y
@R0
AM=M-1  /// go to *SP
D=M /// D = y

/// SP--
@R0
AM=M-1  /// go to --SP, M = x
D=M-D /// D = x - y

@R0
A=M  /// go to *SP
M=D  /// keep the result of add in *SP

@R0
M=M+1  /// SP++
"""

GT_ASM = """
/// returns 1 iff *SP < *(SP-1), and 0 otherwise, , i.e., true iff y < x
@R0
AM=M-1  /// go to *SP
D=M /// D=y

@R13
M=D /// R[13]=y

@YNEGGTi
D;JLT /// if D<0, jump to y negative (YNEGGT)

@R15 /// else, keep sign of D as +
M=1

(PARSEXGTi)
/// SP--
@R0
AM=M-1  /// go to --SP
D=M /// D=*SP=x
@R14
M=D /// R[14]=x

@XNEGGTi
D;JLT /// if x<0, jump to y negative (XNEGGT)

@R15
MD=M-1  /// sign of x: 1, so calculate R15 = sign(y)-sign(x), D = sign(y)-sign(x)

(CHECKSIGNGTi)
@RETURNFALSEGTi
D;JGT /// if D = sign(y)-sign(x) > 0, then y > x, so return FALSE

@RETURNTRUEGTi
D;JLT /// if D = sign(y)-sign(x) < 0, then y < x, so return TRUE

/// Else, we need to compare x and y, and as they are the same sign, there are no overflow problems
@R14
D=M  /// D = x
@R13 /// M = y
D=M-D /// D = y - x

@RETURNFALSEGTi
D;JGT /// if D = y - x > 0, then y > x, so return FALSE

@RETURNFALSEGTi
D;JEQ /// if D = y - x = 0, then y = x, so return FALSE

@RETURNTRUEGTi
D;JLT /// if D = y - x < 0, then y < x, so return TRUE
@ENDGTi
0;JMP

(YNEGGTi)
@R15 /// keep R15 = sign of y = -1
M=-1
@PARSEXGTi
0;JMP /// continue parsing the value of x

(XNEGGTi)
@R15
MD=M+1  /// sign of x: -1, so calculate R15 = sign(y)-sign(x)
@CHECKSIGNGTi
0;JMP /// next: check if both are with the same sign

(RETURNFALSEGTi)
@R0
A=M
M=0
@ENDGTi
0;JMP

(RETURNTRUEGTi)
@R0
A=M
M=-1

(ENDGTi)
@R0
M=M+1  /// SP++
"""

LT_ASM = """
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
"""

NOT_ASM = """
/// returns not y
@R0
A=M-1 /// go to *SP
M=!M /// *SP = not *SP
"""

OR_ASM = """
/// returns y or x (bitwise)
@R0
AM=M-1  /// go to *--SP
D=M /// D = y

/// SP--
@R0
AM=M-1  /// go to SP-1
D=D|M /// D = x or y

@R0
A=M
M=D /// *SP = x|y

@R0
M=M+1  /// go to SP++
"""

AND_ASM = """
/// returns y and x (bitwise)
@R0
AM=M-1  /// go to *--SP
D=M /// D = y

/// SP--
@R0
AM=M-1  /// go to SP-1
D=D&M /// D = x or y

@R0
A=M
M=D /// *SP = x|y

@R0
M=M+1  /// go to SP++
"""

NEG_ASM = """
/// neg *SP
@R0
A=M-1 /// go to *--SP
M=-M /// D=*SP
"""

EQ_ASM = """
/// checks *(SP-1) == *(SP-2), i.e., y==x
@R0
AM=M-1  /// go to --SP
D=M /// D = y

/// SP--
@R0
AM=M-1  /// go to --SP
D=D-M /// D = y-x

@TRUEEQi
D;JEQ /// if D == 0, jump to return TRUE
@R0
A=M
M=0 /// else, return FALSE
@ENDEQi
0;JMP

(TRUEEQi)
@R0
A=M
M=-1 /// return true

(ENDEQi)
@R0
M=M+1  /// SP++
"""

IF_GOTO_ASM = """
@R0
AM=M-1
D=M
@label_name
D;JNE
"""

# used for function command
PUSH_0_INIT = """
@0
D=A
@R0
A=M
M=D // *SP=0
@R0
MA=M+1
"""

PUSH_0_REPEAT = """
M=D // D=0
@R0
MA=M+1
"""

CALL_CMD = """
// push returnAddress
@fileName.functionName$return.index
D=A
@R0
A=M
M=D // *SP=returnAddress
@R0
M=M+1

// push LCL
@LCL
D=A
@R0
A=M
M=D // *SP=LCL
@R0
M=M+1

// push ARG
@ARG
D=A
@R0
A=M
M=D // *SP=ARG
@R0
M=M+1

// push THIS
@THIS
D=A
@R0
A=M
M=D // *SP=THIS
@R0
M=M+1

// push THAT
@THAT
D=A
@R0
A=M
M=D // *SP=THAT
@R0
M=M+1

// ARG = SP-nArgs-5
@SP
D=A
@nArgs
D=D-A
@R13
M=D    // R13=SP-nArgs
@5
D=A
@R13
D=M-D  // D=SP-nArgs-5
@ARG
M=D

// LCL = SP
@SP
D=M
@LCL
M=D

// goto g
@fileName.functionName
0; JMP

// returnAddress:
(fileName.functionName$return.index)
"""

RESTORE_VAL_CMD = """
/// restores the value of SEG_NAME to framej - seg_index
/// e.g., *THAT = *(frame - 1)
@framej
D=M
@seg_index   /// A=seg_index
D=D-A
A=D /// goto *(framej - seg_index)
D=M /// keep *(framej - seg_index)
@SEG_NAME
M=D /// M=M-seg_index
"""

RETURN_ASM_1 = """
/// return - first part (without reset of THIS, THAT, etc...)
@LCL
D=M
@R13 /// @frame = @R13
M=D /// frame = LCL

@5
D=D-A  /// D = D - 5
A=D /// go to *(frame-5)
D=M
@R14 /// @R14 = @retAddr
M=D  /// keep the return address val, *(frame-5)

@SP /// *ARG = pop
A=M-1
D=M
@ARG
M=D

@ARG  /// SP=ARG+1  (restore SP to point at first argument)
D=M
@SP
M=D+1
"""

RETURN_ASM_2 = """
/// return - second part (after setting THIS, THAT,...) 
@R14 /// @R14 = @retAddr
A=M /// go to *retAddr
0;JMP
"""

SYS_INIT_1 = """
@256
D=A
@SP
M=D
"""
