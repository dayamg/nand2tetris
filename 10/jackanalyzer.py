import os
import re
import sys
from lxml import *
# from xml.etree.ElementTree import Element, SubElement, tostring

# etree
from lxml.etree import Element, SubElement

# ElementTree
# from elementtree.ElementTree import Element

# ElementTree in the Python 2.5 standard library
# from xml.etree.ElementTree import Element

JACK_SUFFIX = ".jack"
XML_SUFFIX = ".xml"
READ_MODE = "r"
WRITE_MODE = "w"
NEW_LINE = '\n'
SPACE_CHAR = " "
EMPTY_STRING = ''

# token types constants
KEYWORD = "keyword"
SYMBOL = "symbol"
IDENTIFIER = "identifier"
INT_CONST = "integerConstant"
STRING_CONST = "stringConstant"

# keyword constants
CLASS = "class"
METHOD = "method"
FUNCTION = "function"
CONSTRUCTOR = "constructor"
FIELD = "field"
STATIC = "static"
VAR = "var"
INT = "int"
CHAR = "char"
BOOLEAN = "boolean"
VOID = "void"
TRUE = "true"
FALSE = "false"
NULL = "null"
THIS = "this"
LET = "let"
DO = "do"
IF = "if"
ELSE = "else"
WHILE = "while"
RETURN = "return"

KEY_WORD_DICT = {"CLASS": "class", "METHOD": "method", "FUNCTION": "function", "CONSTRUCTOR": "constructor",
                 "FIELD": "field", "STATIC": "static", "VAR": "var", "INT": "int", "CHAR": "char",
                 "BOOLEAN": "boolean", "VOID": "void", "TRUE": "true", "FALSE": "false", "NULL": "null",
                 "THIS": "this", "LET": "let", "DO": "do", "IF": "if", "ELSE": "else", "WHILE": "while",
                 "RETURN": "return"}

KEY_WORD_LIST = ["class", "method", "function", "constructor", "field", "static", "var", "int", "char",
                 "boolean", "void", "true", "false", "null", "this",  "let",  "do",  "if", "else", "while",
                 "return"]

KEY_WORD_REGEX_PATTERN = re.compile(r"class|method|function|constructor|field|static|var|int|char|boolean|void|true"
                                    r"|false|null|this|let|do|if|else|while|return")
KEY_WORD_NO_SPACE_PATTERN = re.compile(r"true|false|null|this|if|else|while|return")

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
        self.__next_token = None  # a tuple, (token, token_type). token_type is one of TOKEN_TYPE_DICT keys.
        self.__next_token_type = None

        self.__token_index = NO_CURR_TOKEN_INDEX  # = -1
        self.__token_list = []  # A list of tuples, (token, token_type).

        self.__get_token_list()

    def get_next_token(self):
        """
        Yep. A getter. I'm very disappointed with myself for this OOPy behaviour.
        """
        if not self.__next_token:
            return self.__next_token[0]
        return None

    def get_token_type(self):
        """
        Another getter. Type is in one of the elements of TOKEN_TYPE_DICT.
        """
        if not self.__next_token:
            return self.__next_token[1]
        return None

    def __get_token_list(self):
        """
        Initializes a list of all tokens in the input file.
        """
        for line in self.__input_file:
            line = remove_comments_and_stuff(line)
            line_separated_array = line.split(SPACE_CHAR)
            for element in line_separated_array:
                for symbol in SYMBOLS_LIST:
                    for i in range(len(element)):  # This horrible "beginner's loop" is due to my laziness
                        if element[i] == symbol:
                            self.__parse_one_element(element[0:i])
                            self.__token_list.append((symbol, "SYMBOL"))
                            self.__parse_one_element(element[i + 1:])

    def __parse_one_element(self, element):
        """
        Parses one element of a line (after separating by spaces). Recalls itself recursively after separating by
        symbols, i.e., by '.' or '{'.
        :param element: one segment of a line to parse
        """
        if element.isspace() or not element:  # Not supposed to happen, but anyway
            return

        if element in KEY_WORD_LIST:
            self.__token_list.append((element, "KEYWORD"))
            return

        elif element in SYMBOLS_LIST:
            self.__token_list.append((element, "SYMBOL"))
            return

        else:
            pass

    def advance(self):
        pass


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


class SyntaxAnalyzer:

    def __init__(self, jack_path_input, xml_file):
        """
        Yeah, this funky function is for constructing shit, you know.
        """
        self.__tokenizer = JackTokenizer(jack_path_input)
        self.__xml_file = xml_file
        self.__xml_tree = None
        next_token = self.__tokenizer.get_next_token()
        if next_token is not None:
            self.__xml_tree = Element(CLASS)
            self.__compile_class()
        self.__xml_tree.write(self.__xml_file, encoding='unicode')

    def __compile_class(self):
        """
        build xml tree for a class in jack.
        """
        tk = self.__tokenizer

        # 'class' (keyword), className (identifier), '{' (symbol)
        for i in range(3):
            SubElement(self.__xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

        # classVarDec*
        while tk.get_token_type() == KEYWORD and tk.get_token_type() in [FIELD, STATIC]:
            self.__compile_class_var_dec()

        # subroutineDec*
        while tk.get_token_type() == KEYWORD and tk.get_token_type() in [CONSTRUCTOR, FUNCTION, METHOD]:
            self.__compile_subroutine_dec()

    def __compile_class_var_dec(self):
        """
        build xml tree for a class var declaration in jack.
        """
        tk = self.__tokenizer
        # !!TBD CONTINUE

    def __compile_subroutine_dec(self):
        tk = self.__tokenizer
        # !!TBD CONTINUE

    def __compile_parameter_list(self):
        tk = self.__tokenizer
        # !!TBD CONTINUE

    def __compile_var_dec(self):
        tk = self.__tokenizer
        # !!TBD CONTINUE

    def __compile_statements(self):
        tk = self.__tokenizer
        # !!TBD CONTINUE

    def __compile_do(self):
        tk = self.__tokenizer
        # !!TBD CONTINUE

    def __compile_let(self):
        tk = self.__tokenizer
        # !!TBD CONTINUE

    def __compile_while(self):
        tk = self.__tokenizer
        # !!TBD CONTINUE

    def __compile_return(self):
        tk = self.__tokenizer
        # !!TBD CONTINUE

    def __compile_if(self):
        tk = self.__tokenizer
        # !!TBD CONTINUE

    def __compile_expression(self):
        tk = self.__tokenizer
        # !!TBD CONTINUE

    def __compile_term(self):
        tk = self.__tokenizer
        # !!TBD CONTINUE

    def __compile_expression_list(self):
        tk = self.__tokenizer
        # !!TBD CONTINUE


if __name__ == "__main__":
    jack_path_input = sys.argv[1]

    # Check if a file or a directory of vm files.
    if os.path.isfile(jack_path_input):
        xml_path = jack_path_input.replace(JACK_SUFFIX, XML_SUFFIX)
        xml_file = open(xml_path, WRITE_MODE)
        SyntaxAnalyzer(jack_path_input, xml_file)
        xml_file.close()

    if os.path.isdir(jack_path_input):
        jack_path_input = jack_path_input.rstrip('/')
        xml_file_name = os.path.basename(jack_path_input)
        xml_path = os.path.join(jack_path_input, xml_file_name + XML_SUFFIX)
        xml_file = open(xml_path, WRITE_MODE)
        for filename in os.listdir(jack_path_input):
            if filename.endswith(JACK_SUFFIX):
                SyntaxAnalyzer(os.path.join(jack_path_input, filename), xml_file)
        xml_file.close()
