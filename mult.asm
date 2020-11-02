// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

	@R0
	D=M
	@a
	M=D /// a = R0

	@R1
	D=M
	@b
	M=D /// b = R1

	@i
	M=1 // i=1

	@sum
	M=0 // sum = 0

(LOOP)
	///Adding a to itseld b times
	@i
	D=M
	@b
	D=D-M /// D = i-b; D > 0 iff i > b
	@STOP
	D; JGT /// if i > b, go to stop
	
	
	@sum
	D=M
	@a
	D=D+M  /// sum += a
	@i
	M=M+1  /// i++
	@LOOP
	0; JMP
	
(STOP)
	@sum
	D=M
	@R2
	M=D /// RAM[2] = sum



(END)
	@END
	0;JMP