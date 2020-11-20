/// subtracts *SP - *(SP-1)
@R0
A=M  /// go to *SP
D=M /// D=*SP
@R13
M=D  /// RAM[13]=D

/// SP--
@R0
AM=M-1  /// go to --SP
D=M /// D=*SP

@R13
D=D-M  /// subtracts current *SP - R13
@R0
A=M  /// go to *SP
M=D  /// keep the result of sub in *SP

