//////////////// local, argument, this, that

// push segment i
// addr = segmentPointer+i, *SP = *addr, SP++
// need to get: segment -> R?, i

@R? // TBD change according to given segment
D=M
@i
A=D+A 
D=M // D = segment i
@R0
A=M
M=D // *SP=D 
@R0
M=M+1

// pop segment i
// addr = segmentPointer+i, SP--, *addr = *SP
@R? // TBD change according to given segment
D=M
@i
D=D+A 
@R13 // R13 contains the addr of segment i
M=D
@R0
AM=M-1
D=M
@R13
A=M
M=D

////////////////// static

// replace name with current translated file name 

// push static i 
@name.i
D=M
@R0
A=M
M=D
@R0
M=M+1

// pop static i
@R0
AM=M-1
D=M // D = stack.pop
@name.i
M=D

//////////////////// constant

// push constant i 
// *sp=i, sp++
@i
D=A
@R0
A=M
M=D
@R0
M=M+1


///////////////////// temp

// push temp i
// addr = 5+i, *sp=*addr, sp++
@5
D=A
@i
A=D+A 
D=M // D = segment i
@R0
A=M
M=D // *SP=D 
@R0
M=M+1

// pop temp i
// addr=5+i, sp--, *addr=*sp
@5
D=A
@i
D=D+A 
@R13 // R13 = addr of segment i
M=D
@R0
AM=M-1
D=M
@R13
A=M
M=D

///////////////////// pointer

// push pointer 0/1
// *sp=THIS/THAT, sp++
@R3/4 // if 0 then: THIS-3 else if 1 then: THAT-4 
D=M
@R0
A=M
M=D	  // *sp= R3/4
@R0
M=M+1

// pop pointer 0/1
// sp--, THIS/THAT=*sp
@R0
AM=M-1
D=M
@R3/4 // if 0 then: THIS-3 else if 1 then: THAT-4 
M=D
