/// return - first part (without reseting THIS, THAT, etc...)
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







