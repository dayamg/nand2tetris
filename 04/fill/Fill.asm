// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(MAINLOOP)
	@SCREEN
	D=A
	@addr
	M=D /// addr = screen's base adress
 
	@KBD
	D=M
	@BLACK
	D;JNE /// if KBD != 0, color the screen black

 (WHITE)
	@24575
	D=A  /// last index of screen
	@addr
	D=D-M /// last index - curr index
	@MAINLOOP
	D;JLT /// if D<0, goto mainloop
	
	@addr
	A=M
	M=0 ///color white
	
	@addr
	M=M+1 /// curr addr++
	@WHITE
	0;JMP
 
 (BLACK)
	@24575
	D=A  /// last index of screen
	@addr
	D=D-M /// last index - curr index
	@MAINLOOP
	D;JLT /// if D<0, goto mainloop
	
	@addr
	A=M
	M=-1 ///color black
	
	@addr
	M=M+1 /// curr addr++
	@BLACK
	0;JMP