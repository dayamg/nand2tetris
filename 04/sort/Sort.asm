// File name: projects/04/Sort.asm

// Sorts an array in descending order
// Sorts the array starting at the address in R14 with length as specified in R15

	@R15
	D=M
	@lastindex /// lastindex (last index not yet sorted) = R[15]
	M=D

		
	@swap
	M=1	/// initialize a swap variable that checks if a swap happened
	
(LOOP1)
	@i
	M=0 // i=0
	
	@swap
	D=M
	@END
	D;JEQ /// SWAP=0 array sorted, jump to end
	@swap 
	M=0 /// reset swap flag to zero

	@lastindex
	MD=M-1 /// lastindex--
	@END
	D;JLE /// if last index is 0 (or less), jump to end 


(LOOP2)
	@i
	D=M /// D=i
	@R14 /// R[14] = index of first array cell
	D=D+M /// D=i+startarray=adress of curr cell to iterate on
	@leftelement
	M=D /// save adress of left element
	
	@rightelement 
	M=D+1  /// save the adress of right element
	A=M /// go to the adress of the rigth element
	D=M /// save value of rigth element

	@leftelement
	A=M /// go to the left element
	D=D-M /// calculate rightelement-leftelement. should be negative or 0, else swap them
	@ENDLOOP2
	D;JLE /// if arr[i]-arr[i+1]<=0, continue looping in loop2
	
	
	/// else, Swap right and left
	@rightelement
	A=M /// go to rightelement adress
	D=M  /// keep the rightelement value
	@tempelement /// temp = right value
	M=D
	
	@leftelement /// save left element value in D
	A=M
	D=M
	@rightelement
	A=M /// go to adress of rightelement
	M=D /// R[rightelement] = left element value
	
	@tempelement
	D=M
	@leftelement
	A=M /// leftelement = temp
	M=D
	
	@swap /// flag that indicates a swap happened
	M=1
	
(ENDLOOP2)
	@i
	MD=M+1 ///D=++i
	
	@lastindex
	D=M-D /// D=lestindex-i
	@LOOP1
	D;JLE /// if D <= 0, finish loop2, and iterate loop1 again

	@LOOP2
	0;JMP /// else, iterate loop2 again

(END)
	@END
	0;JMP




	
	





