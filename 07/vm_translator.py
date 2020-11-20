import os
import re
import sys

# I don't know if this is really necessary, but for now
NUMBER_OF_ARGS_DICT = {"add": 2, "sub": 2, "neg": 1, "eq": 2, "gt": 2, "lt": 2, "and": 2, "or": 2, "not:": 1}

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
POINTER_DICT = {SP_CHAR: SP_ADDRESS, CONSTANT: SP_ADDRESS, "local": LCL_ADDRESS, "argument": ARG_ADDRESS,
                "this": THIS_ADDRESS, "that": THAT_ADDRESS}

STARTING_ADDRESS_DICT = {"temp": 5, "static": 16, "stack": 256}


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


def split_line_into_segments(vm_line):
    """
    Divides a line into a list of commands,
    e.g., "push local 0" is translated into ["push", "local", 0].
    Removes spaces between.
    Converts string representing numbers, into integers (e.g., "0" to 0).
    """
    segments_array = vm_line.split(SPACE_CHAR)

    # Remove spaces:
    for i in range(len(segments_array)):
        segments_array[i] = remove_comments_and_spaces(segments_array[i])

        # Convert numbers to int
        if segments_array[i].isnumeric():
            segments_array[i] = int(segments_array[i])

    return segments_array


def parse_to_array(vm_file_name):
    """
    Parses the vm code into an array, ignoring whitespaces. Every line is a new element in the array.
    Every element is divided to commands,
    e.g., "push local 0\n pop that 0" is translated into [["push", "local", 0],["pop", "that", 0]].
    """
    vm_file = open(vm_file_name, READ_MODE)
    vm_code_array = []

    for line in vm_file:

        # if line is only whitespace or empty, then skip it.
        if line.isspace() or line == "":
            continue

        vm_code_array.append(split_line_into_segments(line))

    vm_file.close()

    return vm_code_array


def write_get_pointer_A_command(asm_file, pointer):
    """
    writes the A command that saves in D the value of the RAM cell of the given pointer
    pointer is a string, one of the values in POINTER_DICT. (Or maybe we should receive an int instead?)
    We are assuming that asm_file is already open and in write mode.
    """
    pointer_value = POINTER_DICT[pointer]

    # Get the value of RAM[pointer]: @pointer_value \n


    asm_file.write( + NEW_LINE)


def write_push_const(asm_file, const):
    """
    writes the command push constant const,
     e.g., push constant i
     ->     *SP = i
            SP++
    """


def write_push(asm_file, pointer, arg):
    """
    writes the command push variable const,
     e.g., push local 1
     ->    @
    """
