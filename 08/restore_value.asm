/// restores the value of SEG_NAME to frame - seg_index
/// e.g., *THAT = *(frame - 1)
@frame
D=M
@seg_index   /// A=seg_index
D=D-A
A=D /// goto *(frame - seg_index)
D=M /// keep *(frame - seg_index)
@SEG_NAME
M=D /// M=M-seg_index