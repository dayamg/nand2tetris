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
