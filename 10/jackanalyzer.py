import os
import re
import sys


JACK_SUFFIX = ".jack"
XML_SUFFIX = ".xml"
READ_MODE = "r"
WRITE_MODE = "w"
NEW_LINE = '\n'
SPACE_CHAR = " "
EMPTY_STRING = ''

KEY_WORD_DICT = {"CLASS": "class", "METHOD": "method", "FUNCTION": "function", "CONSTRUCTOR": "constructor",
                 "FIELD": "field", "STATIC": "static", "VAR": "var", "INT": "int", "CHAR": "char",
                 "BOOLEAN": "boolean", "VOID": "void", "TRUE": "true", "FALSE": "false", "NULL": "null",
                 "THIS": "this", "LET": "let", "DO": "do", "IF": "if", "ELSE": "else", "WHILE": "while",
                 "RETURN": "return"}

KEY_WORD_LIST = ["class", "method", "function", "constructor", "field", "static", "var", "int", "char",
                  "boolean", "void", "true", "false", "null", "this",  "let",  "do",  "if", "else", "while",
                  "return"]

KEY_WORD_REGEX =  re.compile(r"")

SYMBOLS_LIST = ['{', '}',
                '(', ')',
                '[', ']'
                '.', ',', ';',
                '+', '-', '*', '/',
                '&', '|',
                '<', '>', '=', '~'
                ]



SYMBOL_TRANSLATION_DICT = {">": "&gt;", "<": "&lt;", "&": "&amp;", "\'": "&quot;"}

TOKEN_TYPE_DICT = {"KEYWORD": "keyword", "SYMBOL": "symbol", "IDENTIFIER": "identifier",
                   "INT_CONST": "integerConstant", "STRING_CONST": "stringConstant"}

NO_CURR_TOKEN_INDEX = -1


class JackTokenizer:
    """
    No other option seems reasonable, so we probably need to use OOP.  :(
    """

    def __init__(self, input_jack_file):
        """
        Yeah, this funky function is for constructing shit, you know.
        """
        self.__input_file = input_jack_file  # the input file, of file type
        self.__next_token = None
        self.__next_token_type = None  # the type (one of TOKEN_TYPE_DICT) of the next token

        self.__token_index = NO_CURR_TOKEN_INDEX  # = -1
        self.__token_list = []

        self.__get_token_list()

    def get_next_token(self):
        """
        Yep. A getter. I'm very disappointed with myself for this OOPy behaviour.
        """
        return self.__next_token

    def __get_token_list(self):
        """
        Initializes a list of all tokens in the input file.
        """
        for line in self.__input_file:
            line = remove_comments_and_stuff(line)





def remove_comments_and_stuff(line):
    """
    Removes inline comments, tabs and newlines. Replaces double (or triple, or ...) spaces with one space.
    (Spaces are not removed, as it is important later)
    """
    comment_pattern = re.compile(r"//.*")
    line = re.sub(comment_pattern, '', line)  # remove comments
    tabs_and_new_lines_pattern = re.compile(r"\t*\n*")
    line = re.sub(tabs_and_new_lines_pattern, '', line)  # remove new lines and tabs
    multiple_spaces_pattern = re.compile(r"  +")
    line = re.sub(multiple_spaces_pattern, SPACE_CHAR, line)  # replaces multiple spaces with only one

    return line.strip(SPACE_CHAR)  # Removes spaces in the beginning or end of line


def jack_analyzer(jack_path_input, xml_file):
    pass


if __name__ == "__main__":
    jack_path_input = sys.argv[1]

    # Check if a file or a directory of vm files.
    if os.path.isfile(jack_path_input):
        xml_path = jack_path_input.replace(JACK_SUFFIX, XML_SUFFIX)
        xml_file = open(xml_path, WRITE_MODE)
        jack_analyzer(jack_path_input, xml_file)
        xml_file.close()

    if os.path.isdir(jack_path_input):
        jack_path_input = jack_path_input.rstrip('/')
        xml_file_name = os.path.basename(jack_path_input)
        xml_path = os.path.join(jack_path_input, xml_file_name + XML_SUFFIX)
        xml_file = open(xml_path, WRITE_MODE)
        for filename in os.listdir(jack_path_input):
            if filename.endswith(JACK_SUFFIX):
                jack_analyzer(os.path.join(jack_path_input, filename), xml_file)
        xml_file.close()
