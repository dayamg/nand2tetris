/// returns y and x (bitwise)
@R0
A=M  /// go to *SP
D=M /// D = y

/// SP--
@R0
AM=M-1  /// go to --SP
D=D&M /// D = x and y

@R0
A=M
M=D /// *SP = D
