/// File name: projects/04/Mult.asm

/// Multiplies R0 and R1 and stores the result in R2.
/// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
/// program assumes that R0>=0, R1>=0, and R0*R1<32768

	@i
	M=1 // i=1

	@R2
	M=0 // R[2] = 0 (sum)

(LOOP)
	///Adding a to itseld b times
	@i
	D=M /// D=i
	
	@R1 /// b
	D=D-M /// D = i-b, D > 0 iff i > b
	@END
	D;JGT /// if i > b, go to stop
	
	@R0
	D=M /// D=a
	@R2 
	M=D+M  /// sum += a
	@i
	M=M+1  /// i++
	@LOOP
	0;JMP
	
(END)
	@END
	0;JMP