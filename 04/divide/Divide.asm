// This program divides R13 (stores in num1) by R14 (stores in num2) and put the result in R15.

// Store R13 to num1 and R14 to num2.
@R13
D=M
@num1
M=D

@R14
D=M
@num2
M=D

// Check edge cases.

// if num1=num2 -> result=1
@num1
D=M
@num2
D=D-M // D=num1-num2
@RESULT1
D; JEQ
// if num2>num1 -> result=0
@RESULT0
D; JLT
// if num2=1 -> result=num1
@num2
D=M-1
@RESULTR13
D; JEQ

// start to calc division.

@result	// result=0
M=1

(LOOP1) // While (num1)>(num2*2) -> result*=2 :
@num2
D=M
D=D<<
@num1
D=D-M	//D = num2*2-num1 -> if D > 0 jump to FINISHMULTBY2  
@FINISHMULTBY2
D; JGT

@num2	// multiple num2 by 2
M=M<<
@result	// multiple result by 2
M=M<<
@LOOP1
0; JMP

(FINISHMULTBY2)
@num2 // partnum2 = num2/2
D=M
D=D>>
@partnum2
M=D

@result // partresult = result/2
D=M
D=D>>
@partresult
M=D

(LOOP2)
@partnum2
D=M
@num2
D=D+M
@num1
D=D-M // D=(num2+partnum2)-num1
@LOOPCHECK
D; JGT // if D>0 dont update result, check next if interation.

// Update result
@partnum2 // num2 += partnum2
D=M
@num2
M=D+M

@partresult	// result += partresult
D=M
@result
M=D+M

(LOOPCHECK)
// check if partresult>> and partnum2>> are zero.
@partnum2
M=M>>
D=M
@END
D; JEQ // If D=0, end program.

@partresult 
M=M>>
D=M
@END
D; JEQ // If D=0, end program.

@LOOP2
0; JMP

(RESULT1)
@result
M=1
@END
0; JMP

(RESULT0)
@result
M=0
@END
0; JMP

(RESULTR13)
@R13
D=M
@result
M=D
@END
0; JMP

(END) // R15=result
@result
D=M
@R15
M=D

//(STOP)
//@STOP
//0; JMP



