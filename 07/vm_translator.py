import os
import re
import sys



# I don't know if this is really necessary, but for now
NUMBER_OF_ARGS_DICT = {"add": 2, "sub": 2, "neg": 1, "eq": 2, "gt": 2, "lt": 2, "and": 2, "or": 2, "not:": 1}

VM_SUFFIX = ".vm"
ASM_SUFFIX = ".asm"
READ_MODE = "r"
WRITE_MODE = "w"
NEW_LINE = '\n'
SPACE_CHAR = " "

CONSTANT = "constant"

A_COMMAND_PREFIX = '@'

SP_ADDRESS = 0
LCL_ADDRESS = 1
ARG_ADDRESS = 2
THIS_ADDRESS = 3
THAT_ADDRESS = 4

SP_CHAR = "SP"

# A dictionary for translating variables types. Notice: the string "SP" is not used in the vm file
# (as there is no special name for it), and "constant" is not a real RAM section
SEGMENT_DICT = {SP_CHAR: SP_ADDRESS, CONSTANT: SP_ADDRESS, "local": LCL_ADDRESS, "argument": ARG_ADDRESS,
                "this": THIS_ADDRESS, "that": THAT_ADDRESS}
POINTER_DICT = {0: THIS_ADDRESS, 1: THAT_ADDRESS}
STARTING_ADDRESS_DICT = {"temp": 5, "static": 16, "stack": 256}


def generate_push_cmd(vm_cmd, vm_file):
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
    return cmd_string


def generate_pop_cmd(vm_cmd, vm_file):
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
    return cmd_string


def generate_arithmetic_cmd(vm_cmd):
    """
    !!!TBD!!!
    writes vm arithmetic commands in asm and returns it.
    """
    cmd_string = ""
    return cmd_string


def write_vm_cmd_to_asm(vm_cmd, asm_file, vm_file):
    """
    find the vm command type, generate it in asm, and write to asm file.
    """
    # Write the translated command in a comment in the asm file.
    cmd_string = "///// "
    for i in vm_cmd:
        cmd_string += " " + str(i)
    asm_file.write(cmd_string + NEW_LINE)

    # Extract the file name for push/pop static commands.
    file_name = os.path.splitext(os.path.basename(vm_file.name))[0]

    cmd_type = vm_cmd[0]
    asm_cmd = ""
    if cmd_type == "push":
        asm_cmd = generate_push_cmd(vm_cmd, file_name)
    if cmd_type == "pop":
        asm_cmd = generate_pop_cmd(vm_cmd, file_name)
    if cmd_type in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
        asm_cmd = generate_arithmetic_cmd(vm_cmd)

    # Write cmd_string to asm file.
    asm_file.write(asm_cmd + NEW_LINE)


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
        if segments_array[i].isnumeric():
            segments_array[i] = int(segments_array[i])

    return segments_array


def vm_translator(vm_path, asm_path):
    """
    Get vm and asm files path, and translate vm into asm file.
    """
    vm_file = open(vm_path, READ_MODE)
    asm_file = open(asm_path, WRITE_MODE)

    for line in vm_file:

        line = remove_comments(line)
        # if line is only whitespace or empty, then skip it.
        if line.isspace() or line == "":
            continue

        vm_cmd = split_line_into_segments(line)
        write_vm_cmd_to_asm(vm_cmd, asm_file, vm_file)

    vm_file.close()
    asm_file.close()


if __name__ == "__main__":
    vm_path = sys.argv[1]
    # Check if a file or a directory of vm files.
    if os.path.isfile(vm_path):
        asm_path = vm_path.replace(VM_SUFFIX, ASM_SUFFIX)
        vm_translator(vm_path, asm_path)

    if os.path.isdir(vm_path):
        asm_path = os.path.join(vm_path, VM_SUFFIX)
        for filename in os.listdir(vm_path):
            if filename.endswith(VM_SUFFIX):
                vm_translator(os.path.join(vm_path, filename), asm_path)
