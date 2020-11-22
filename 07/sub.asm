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