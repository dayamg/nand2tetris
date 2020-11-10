import os
import re
import sys
import copy

# MAGIC NUMBERS - Dictionaries for translations
SYMBOL_DICT = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4, "R0": 0, "R1": 1, "R2": 2, "R3": 3,
               "R4": 4, "R5": 5, "R6": 6, "R7": 7, "R8": 8, "R9": 9, "R10": 10, "R11": 11, "R12": 12,
               "R13": 13, "R14": 14, "R15": 15, "SCREEN": 16384, "KBD": 24576}
DEST_DICT = {"null": "000", "M": "001", "D": "010", "MD": "011", "DM": "011", "A": "100",
             "AM": "101", "MA": "101", "AD": "110", "DA": "110", "AMD": "111", "ADM": "111",
             "MDA": "111", "MAD": "111", "DAM": "111", "DMA": "111"}
JUMP_DICT = {"null": "000", "JGT": "001", "JEQ": "010", "JGE": "011", "JLT": "100",
             "JNE": "101", "JLE": "110", "JMP": "111"}
COMP_DICT = {"0": "110101010", "1": "110111111", "-1": "110111010", "D": "110001100",
             "D&A": "110000000", "D&M": "111000000", "D|A": "110010101", "D|M": "111010101", "D*A": "100000000",
             "M+1": "111110111", "D-1": "110001110", "A-1": "110110010", "M-1": "111110010", "D+A": "110000010",
             "-D": "110001111", "-A": "110110011", "-M": "111110011", "D+1": "110011111", "A+1": "110110111",
             "D*M": "101000000", "D<<": "010110000", "A<<": "010100000", "M<<": "011100000", "D>>": "010010000",
             "A": "110110000", "M": "111110000", "!D": "110001101", "!A": "110110001", "!M": "111110001",
             "D+M": "111000010", "D-A": "110010011", "D-M": "111010011", "A-D": "110000111", "M-D": "111000111",
             "A>>": "010000000", "M>>": "011000000"}
# Constants
VAR_DICT_START_ADDR = 16
BIN_CMD_LEN = 16
READ_MODE = "r"
WRITE_MODE = "w"
NEW_LINE = '\n'
LABEL_PREFIX = '('
LABEL_SUFFIX = ')'

A_CMD_ASM_PREFIX = '@'
A_CMD_BIN_PREFIX = "0"
C_CMD_BIN_PREFIX = "1"

# Global variables
var_dict = {}
var_address_pointer = 0


def remove_comments_and_spaces(line):
    """
    removes inline comments
    """
    pattern = re.compile(r"\s+")  # remove spaces
    line = re.sub(pattern, '', line)
    pattern = re.compile(r"//.*")  # remove comments
    line = re.sub(pattern, '', line)
    return line


def check_for_label(line):
    """
    Receives a line with no spaces or comments and check for label.
    Return the label name, or none.
    """
    label_name = None
    if line[0] == LABEL_PREFIX:
        label_name = line.strip(LABEL_PREFIX + LABEL_SUFFIX)
    return label_name


def remove_labels(file_name):
    """
    Removes the labels and comments from the input .asm file named file_name.
    Returns an array, in which every element is a line of the file without labels.
    """
    global var_dict
    line_count = 0
    asm_file = open(file_name, READ_MODE)
    file_no_labels_array = []

    for line in asm_file:
        # ignore comments and spaces.
        line = remove_comments_and_spaces(line)

        # if line is only whitespace or empty, then skip it.
        if line.isspace() or line == "":
            continue

        # if line contain label, save the label and skip it.
        label = check_for_label(line)
        if label is not None:
            var_dict[label] = line_count
            continue

        file_no_labels_array.append(line)
        line_count += 1

    asm_file.close()
    return file_no_labels_array


def var_dict_handler(var):
    """
    If var in dict, return the address accordingly.
    else, give the var in the next available address (pointer) and return it.
    """
    global var_dict
    global var_address_pointer
    if var not in var_dict.keys():
        var_dict[var] = var_address_pointer
        var_address_pointer += 1
    return var_dict[var]


def translate_a_cmd(line):
    """
    Get a line that contain an A command in asm and translate it to hack.
    """
    line = line.strip(A_CMD_ASM_PREFIX + NEW_LINE)
    # check if address is number or variable
    try:
        address = bin(int(line))[2:]

    except ValueError:
        # Replace variable with an address.
        address = bin(var_dict_handler(line))[2:]

    # pad to 16 bits
    cmd = A_CMD_BIN_PREFIX + address.zfill(BIN_CMD_LEN-1)
    return cmd


def translate_c_cmd(line):
    """
    Get a line that contain an C command in asm and translate it to hack.
    """
    line = line.strip(NEW_LINE)
    # Parse command to dest, comp, jump
    dest = 'null'
    jump = 'null'
    if line.find('=') != -1:
        dest, line = line.split('=')
    if line.find(';') != -1:
        comp, jump = line.split(';')
    else:
        comp = line

    # Build the binary command using the relevant dicts.
    c_cmd = C_CMD_BIN_PREFIX  # the start of a C binary command.
    c_cmd += COMP_DICT[comp]
    c_cmd += DEST_DICT[dest]
    c_cmd += JUMP_DICT[jump]
    return c_cmd


def translate_to_hack(hack_file_path, file_no_labels_array):
    """
    Translate the no labels array into hack commands and write it to the given file address.
    """
    hack_file = open(hack_file_path, WRITE_MODE)

    line_count = 0
    for line in file_no_labels_array:
        if line[0] == A_CMD_ASM_PREFIX:
            binary_cmd = translate_a_cmd(line)
        else:
            binary_cmd = translate_c_cmd(line)

        hack_file.write(binary_cmd + NEW_LINE)
        line_count += 1
    hack_file.close()


def assembler(asm_file_path):
    """
    Get an asm file and translate in into hack file with the same name.
    """
    # Reset var_dict and the address to start storing variables in memory before every file.
    global var_dict
    var_dict = copy.deepcopy(SYMBOL_DICT)
    global var_address_pointer
    var_address_pointer = VAR_DICT_START_ADDR

    file_no_labels_array = remove_labels(asm_file_path)
    hack_file_path = asm_file_path.strip(".asm") + ".hack"
    translate_to_hack(hack_file_path, file_no_labels_array)


if __name__ == "__main__":
    asm_path = sys.argv[1]
    # Check if a file or a directory of asm files.
    if os.path.isfile(asm_path):
        assembler(asm_path)

    if os.path.isdir(asm_path):
        for filename in os.listdir(asm_path):
            if filename.endswith(".asm"):
                assembler(asm_path + filename)

