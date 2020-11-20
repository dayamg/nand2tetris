/// adds *SP + *(SP-1)
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
D=M+D  /// add R13 + current *SP
@R0
A=M  /// go to *SP
M=D  /// keep the result of add in *SP

