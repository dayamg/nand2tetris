/// checks *SP == *(SP-1), i.e., y==x
@R0
A=M  /// go to *SP
D=M /// D=y

/// SP--
@R0
AM=M-1  /// go to --SP
D=D-M /// D = y-x


@EQ
D;JEQ /// if D == 0, jump to return equal (true)
@R0
A=M
M=0 /// return false
@END
0;JMP


(EQ)
@R0
A=M
M=1 /// return true

(END)