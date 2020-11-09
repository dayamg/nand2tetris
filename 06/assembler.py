import os
import re

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

READ_MODE = "r"


def remove_comments_and_spaces(line):
    """
    removes inline comments
    """
    pattern = re.compile(r"\s+")  # remove spaces
    line = re.sub(pattern, '', line)
    pattern = re.compile(r"//.*")  # remove comments
    line = re.sub(pattern, '', line)
    return line


def line_is_label(line):
    """
    receives a line with no spaces or comments
    :return (is_the_line_a_label, label_name)
    """
    label_name = ''


    return False, label_name


def remove_labels(file_name):
    """
    Removes the labels from the input .asm file named file_name.
    Writes the result in a new file named  file_nameNoLabels.txt
    """
    label_dict = dict()  # dictionary in form of {LABEL: line_number}
    line_count = 0

    asm_file = open(file_name, READ_MODE)
    for line in asm_file:
        if not line.isspace():  # check if the line is not a whitespace
            line = remove_comments_and_spaces(line)

            if line_is_label(line):




            line_count += 1




