import os
import re
import sys
from asm_helper import *

# test git commit

VM_SUFFIX = ".vm"
ASM_SUFFIX = ".asm"
READ_MODE = "r"
WRITE_MODE = "w"
NEW_LINE = '\n'
SPACE_CHAR = " "

SEG_NAME_TOKEN = "SEG_NAME"  # The name used in the asm file as a , to be replaced
SEG_INDEX_TOKEN = "seg_index"  # The name used in the asm file as a , to be replaced

CONSTANT = "constant"

A_COMMAND_PREFIX = '@'

SP_ADDRESS = 0
LCL_ADDRESS = 1
ARG_ADDRESS = 2
THIS_ADDRESS = 3
THAT_ADDRESS = 4

SP_CHAR = "SP"

g_arith_i_index = 0  # Global index i for labeling arithmetic commands
g_call_j_index = 0  # Global index j for labeling call commands

g_curr_func = None

# A dictionary for translating variables types. Notice: the string "SP" is not used in the vm file
# (as there is no special name for it), and "constant" is not a real RAM section
SEGMENT_DICT = {SP_CHAR: SP_ADDRESS, CONSTANT: SP_ADDRESS, "local": LCL_ADDRESS, "argument": ARG_ADDRESS,
                "this": THIS_ADDRESS, "that": THAT_ADDRESS}
POINTER_DICT = {0: THIS_ADDRESS, 1: THAT_ADDRESS}
STARTING_ADDRESS_DICT = {"temp": 5, "static": 16, "stack": 256}

ARITHMETIC_DICT = {"add": ADD_ASM, "neg": NEG_ASM, "sub": SUB_ASM, "eq": EQ_ASM, "lt": LT_ASM,
                   "gt": GT_ASM, "not": NOT_ASM, "or": OR_ASM, "and": AND_ASM}


def generate_label_cmd(vm_cmd, asm_file):
    global g_curr_func
    label_name = vm_cmd[1]
    cmd_string = "(" + label_name + ")"
    if g_curr_func:
        cmd_string = "(" + str(g_curr_func) + "$" + label_name + ")"
    # Write cmd_string to asm file.
    asm_file.write(cmd_string + NEW_LINE)


def generate_goto_cmd(vm_cmd, asm_file):
    global g_curr_func
    label_name = vm_cmd[1]
    cmd_string = "@" + label_name + "\n" + "0;JMP"
    if g_curr_func:
        cmd_string = "@" + str(g_curr_func) + "$" + label_name + "\n" + "0;JMP"
    # Write cmd_string to asm file.
    asm_file.write(cmd_string + NEW_LINE)


def generate_if_goto_cmd(vm_cmd, asm_file):
    global g_curr_func
    label_name = vm_cmd[1]
    label_cmd = label_name
    if g_curr_func:
        label_cmd = str(g_curr_func) + "$" + label_name

    cmd_string = IF_GOTO_ASM
    cmd_string = cmd_string.replace("label_name", label_cmd)
    # Write cmd_string to asm file.
    asm_file.write(cmd_string + NEW_LINE)


def generate_function_cmd(vm_cmd, asm_file):
    global g_curr_func
    # function g nVars
    function_name = vm_cmd[1]
    g_curr_func = function_name
    nVars = vm_cmd[2]
    cmd_string = "(" + function_name + ")" + "\n"
    for i in range(nVars):
        if i == 0:
            cmd_string += PUSH_0_INIT + "\n"
            continue
        cmd_string += PUSH_0_REPEAT + "\n"

    # Write cmd_string to asm file.
    asm_file.write(cmd_string + NEW_LINE)


def generate_call_cmd(vm_cmd, asm_file):
    # call g nArgs
    global g_call_j_index
    global g_curr_func

    function_name = vm_cmd[1]
    nArgs = vm_cmd[2]
    cmd_string = CALL_CMD + "\n"
    cmd_string = cmd_string.replace("index", str(g_call_j_index))
    cmd_string = cmd_string.replace("functionName", function_name)
    cmd_string = cmd_string.replace("nArgs", str(nArgs))
    g_call_j_index += 1

    # Write cmd_string to asm file.
    asm_file.write(cmd_string + NEW_LINE)


def generate_push_cmd(vm_cmd, vm_file, asm_file):
    """
    writes the command "push segment i" in asm and return it.
    """
    segment = vm_cmd[1]
    cmd_string = ""

    if segment in ["local", "argument", "this", "that"]:
        # address = segmentPointer+i, *SP = *address, SP++
        cmd_string = "@R?\nD=M\n@i\nA=D+A\nD=M // D = segment i\n@R0\nA=M\nM=D // *SP=D\n@R0\nM=M+1"
        seg_addr = str(SEGMENT_DICT[segment])
        cmd_string = cmd_string.replace("?", seg_addr)

    if segment == "static":
        cmd_string = "@name.i\nD=M\n@R0\nA=M\nM=D\n@R0\nM=M+1"

    if segment == "constant":
        # *sp=i, sp++
        cmd_string = "@i\nD=A\n@R0\nA=M\nM=D\n@R0\nM=M+1"

    if segment == "temp":
        # address = 5+i, *sp=*address, sp++
        cmd_string = "@5\nD=A\n@i\nA=D+A \nD=M // D = segment i\n@R0\nA=M\nM=D // *SP=D\n@R0\nM=M+1"

    index = vm_cmd[2]
    cmd_string = cmd_string.replace("i", str(index))
    cmd_string = cmd_string.replace("name", vm_file)  # For static commands

    if segment == "pointer":
        # *sp=THIS/THAT, sp++
        cmd_string = "@R?\nD=M\n@R0\nA=M\nM=D	// *sp= R3/4\n@R0\nM=M+1"
        # if index is 0 then: THIS-3 else if 1 then: THAT-4
        cmd_string = cmd_string.replace("?", str(POINTER_DICT[index]))

    # Write cmd_string to asm file.
    asm_file.write(cmd_string + NEW_LINE)


def generate_pop_cmd(vm_cmd, vm_file, asm_file):
    """
    writes the command "pop segment i" in asm and return it.
    """
    segment = vm_cmd[1]
    cmd_string = ""

    if segment in ["local", "argument", "this", "that"]:
        # addr = segmentPointer + i, SP - -, *addr = *SP
        cmd_string = "@R?\nD=M\n@i\nD=D+A\n@R13 // R13 = segment i addr\nM=D\n@R0\nAM=M-1\nD=M\n@R13\nA=M\nM=D"
        seg_addr = str(SEGMENT_DICT[segment])
        cmd_string = cmd_string.replace("?", seg_addr)

    if segment == "static":
        cmd_string = "@R0\nAM=M-1\nD=M // D = stack.pop\n@name.i\nM=D"

    if segment == "temp":
        # address=5+i, sp--, *address=*sp
        cmd_string = "@5\nD=A\n@i\nD=D+A\n@R13 // R13 = addr of segment i\nM=D\n@R0\nAM=M-1\nD=M\n@R13\nA=M\nM=D"

    index = vm_cmd[2]
    cmd_string = cmd_string.replace("i", str(index))
    cmd_string = cmd_string.replace("name", vm_file)  # For static commands

    if segment == "pointer":
        # sp--, THIS/THAT=*sp
        cmd_string = "@R0\nAM=M-1\nD=M\n@R?\nM=D"
        # if index is 0 then: THIS-3 else if 1 then: THAT-4
        cmd_string = cmd_string.replace("?", str(POINTER_DICT[index]))

    # Write cmd_string to asm file.
    asm_file.write(cmd_string + NEW_LINE)


def write_vm_cmd_to_asm(vm_cmd, asm_file, vm_file):
    """
    find the vm command type, generate it in asm, and write to asm file.
    """
    global g_arith_i_index

    # Write the translated command in a comment in the asm file.
    cmd_string = "//#//#// "
    for i in vm_cmd:
        cmd_string += " " + str(i)
    asm_file.write(cmd_string + NEW_LINE)

    # Extract the file name for push/pop static commands.
    file_name = os.path.splitext(os.path.basename(vm_file.name))[0]

    cmd_type = vm_cmd[0]
    if cmd_type == "push":
        generate_push_cmd(vm_cmd, file_name, asm_file)

    if cmd_type == "pop":
        generate_pop_cmd(vm_cmd, file_name, asm_file)

    if cmd_type in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
        arithmetic_asm_str = ARITHMETIC_DICT[cmd_type].replace("i", str(g_arith_i_index))
        asm_file.write(arithmetic_asm_str + NEW_LINE)
        g_arith_i_index += 1

    if cmd_type == "label":
        generate_label_cmd(vm_cmd, asm_file)

    if cmd_type == "goto":
        generate_goto_cmd(vm_cmd, asm_file)

    if cmd_type == "if-goto":
        generate_if_goto_cmd(vm_cmd, asm_file)

    if cmd_type == "function":
        generate_function_cmd(vm_cmd, asm_file)

    if cmd_type == "call":
        generate_call_cmd(vm_cmd, asm_file)

    if cmd_type == "return":
        generate_return_cmd(asm_file)


def generate_restore_command(asm_file, seg_name, seg_index):
    """
    writes the command that restores the pointer seg_name to value before function call.
    E.g., generate_restore_command(asm_file, "THIS", 1) will write the command THIS = *(frame - 1).
    """

    asm_cmd = RESTORE_VAL_CMD.replace(SEG_NAME_TOKEN, seg_name).replace(SEG_INDEX_TOKEN, str(seg_index))
    asm_file.write(asm_cmd + NEW_LINE)


def generate_return_cmd(asm_file):
    asm_file.write(RETURN_ASM_1 + NEW_LINE)
    generate_restore_command(asm_file, "THAT", 1)
    generate_restore_command(asm_file, "THIS", 2)
    generate_restore_command(asm_file, "ARG", 3)
    generate_restore_command(asm_file, "LCL", 4)
    asm_file.write(RETURN_ASM_2 + NEW_LINE)  # goto retAddr = *R14


def remove_comments_and_spaces(segment):
    """
    Removes inline comments and spaces
    (Are there even comments in vm?)
    """
    pattern = re.compile(r"\s+")  # remove spaces
    segment = re.sub(pattern, '', segment)
    pattern = re.compile(r"//.*")  # remove comments
    segment = re.sub(pattern, '', segment)
    return segment


def remove_comments(segment):
    """
    Removes inline comments and spaces
    (Are there even comments in vm?)
    """
    pattern = re.compile(r"//.*")  # remove comments
    segment = re.sub(pattern, '', segment)
    return segment


def split_line_into_segments(vm_line):
    """
    Divides a line into a list of commands,
    e.g., "push local 0" is translated into ["push", "local", 0].
    Removes spaces between.
    Converts string representing numbers, into integers (e.g., "0" to 0).
    """
    segments_array = vm_line.split(SPACE_CHAR)
    segments_array = list(filter(None, segments_array))

    # Remove spaces:
    for i in range(len(segments_array)):
        segments_array[i] = remove_comments_and_spaces(segments_array[i])

        # Convert numbers to int
        if str(segments_array[i]).isdigit():
            segments_array[i] = int(segments_array[i])

    return segments_array


def vm_translator(vm_path, asm_file):
    """
    Get vm and asm files path, and translate vm into asm file.
    """
    vm_file = open(vm_path, READ_MODE)

    for line in vm_file:

        line = remove_comments(line)
        # if line is only whitespace or empty, then skip it.
        if line.isspace() or line == "":
            continue

        vm_cmd = split_line_into_segments(line)
        write_vm_cmd_to_asm(vm_cmd, asm_file, vm_file)

    vm_file.close()


def generate_sys_init(asm_file):
    asm_file.write("//#//#// SYS.INIT" + NEW_LINE)
    asm_file.write(SYS_INIT_1 + NEW_LINE)
    vm_cmd = ["call", "Sys.init", 0]
    asm_file.write("//#// CALL SYS.INIT" + NEW_LINE)
    generate_call_cmd(vm_cmd, asm_file)


if __name__ == "__main__":
    vm_path_input = sys.argv[1]
    # Check if a file or a directory of vm files.
    if os.path.isfile(vm_path_input):
        asm_path = vm_path_input.replace(VM_SUFFIX, ASM_SUFFIX)
        asm_file = open(asm_path, WRITE_MODE)
        generate_sys_init(asm_file)
        vm_translator(vm_path_input, asm_file)
        asm_file.close()

    if os.path.isdir(vm_path_input):
        vm_path_input = vm_path_input.rstrip('/')
        asm_file_name = os.path.basename(vm_path_input)
        asm_path = os.path.join(vm_path_input, asm_file_name+ASM_SUFFIX)
        asm_file = open(asm_path, WRITE_MODE)
        generate_sys_init(asm_file)
        for filename in os.listdir(vm_path_input):
            if filename.endswith(VM_SUFFIX):
                # Write a comment with file name
                asm_file.write("////////*****//////// " + filename + NEW_LINE)
                vm_translator(os.path.join(vm_path_input, filename), asm_file)
        asm_file.close()
