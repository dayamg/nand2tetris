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

OP_LIST = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
UNARY_OP_LIST = ['~', '-']

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
            self.__compile_class(Element(CLASS))
        self.__xml_tree.write(self.__xml_file, encoding='unicode')

    def __compile_class(self, xml_tree):
        """
        Build xml tree for a class in jack.
        """
        tk = self.__tokenizer

        # 'class' className '{'
        for i in range(3):
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

        # classVarDec*
        while tk.get_token_type() == KEYWORD and tk.get_next_token() in [FIELD, STATIC]:
            self.__compile_class_var_dec(SubElement(xml_tree, "classVarDec"))

        # subroutineDec*
        while tk.get_token_type() == KEYWORD and tk.get_next_token() in [CONSTRUCTOR, FUNCTION, METHOD]:
            self.__compile_subroutine_dec(SubElement(xml_tree, "subroutineDec"))

    def __compile_class_var_dec(self, xml_tree):
        """
        Build xml tree for a class var declaration in jack.
        """
        tk = self.__tokenizer
        # 'static/field'(keyword), type (keyword/identifier), varName (identifier)
        for i in range(3):
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

        # (, varName)*
        while tk.get_token_type() == SYMBOL and tk.get_token_type() == ',':
            # ','
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # varName
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

        # ';'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_subroutine_dec(self, xml_tree):
        """
        build xml tree for a subroutine declaration in jack.
        """
        tk = self.__tokenizer
        # 'constructor/function/method'(keyword), 'void'/type (keyword/identifier), subroutineName (identifier), '('
        for i in range(4):
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

        # 'parameterList'
        self.__compile_parameter_list(SubElement(xml_tree, "parameterList"))

        # ')'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # 'subroutineBody'
        self.__compile_subroutine_body(SubElement(xml_tree, "subroutineBody"))

    def __compile_subroutine_body(self, xml_tree):
        """
        Build xml tree for a subroutine body in jack.
        """
        tk = self.__tokenizer
        # '{'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # varDec*
        while tk.get_token_type() == KEYWORD and tk.get_next_token() == VAR:
            self.__compile_class_var_dec(SubElement(xml_tree, "varDec"))
        # statements
        self.__compile_statements(SubElement(xml_tree, "statements"))

        # '}'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_parameter_list(self, xml_tree):
        """
        Build xml tree for a parameter list in jack.
        """
        tk = self.__tokenizer

        # check is list is empty, meaning next token is )
        if tk.get_token_type() == SYMBOL and tk.get_next_token() == ')':
            # xml_tree = '\n'
            return

        # if (tk.get_token_type() == KEYWORD and tk.get_next_token() in [INT, CHAR, BOOLEAN]) \
        #         or (tk.get_token_type() == IDENTIFIER):

        # type
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # varName
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # (, varName)*
        while tk.get_token_type() == SYMBOL and tk.get_next_token() == ',':
            # ','
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # varName
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

        # ';'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_var_dec(self, xml_tree):
        """
        Build xml tree for a variable declaration in jack.
        """
        tk = self.__tokenizer
        # 'var'(keyword), type (keyword/identifier), varName (identifier)
        for i in range(3):
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

        # (, varName)*
        while tk.get_token_type() == SYMBOL and tk.get_next_token() == ',':
            # ','
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # varName
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

        # ';'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_statements(self, xml_tree):
        """
        Build xml tree for statements in jack.
        """
        tk = self.__tokenizer
        # statement*
        while tk.get_token_type() == KEYWORD and tk.get_next_token() in [LET, IF, WHILE, DO, RETURN]:
            if tk.get_next_token() == LET:
                self.__compile_let(SubElement(xml_tree, "letStatement"))
            if tk.get_next_token() == IF:
                self.__compile_let(SubElement(xml_tree, "ifStatement"))
            if tk.get_next_token() == WHILE:
                self.__compile_let(SubElement(xml_tree, "whileStatement"))
            if tk.get_next_token() == DO:
                self.__compile_let(SubElement(xml_tree, "doStatement"))
            if tk.get_next_token() == RETURN:
                self.__compile_let(SubElement(xml_tree, "returnStatement"))

    def __compile_do(self, xml_tree):
        """
        Build xml tree for do statement in jack.
        """
        tk = self.__tokenizer
        # 'do'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # subroutineName/(className/varName)
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # subroutineCall
        self.__compile_subroutine_call(xml_tree)  # No SubElement!
        # ';'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_subroutine_call(self, xml_tree):
        """
        Build xml tree for subroutine call in jack.
        First token of the identifier subroutineName/(className/varName) should be out already.
        """
        tk = self.__tokenizer

        if tk.get_token_type() == SYMBOL and tk.get_next_token() == '.':
            # '.'
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # subroutineName
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

        # '('
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # expressionList
        self.__compile_expression_list(SubElement(xml_tree, "expressionList"))

        # ')'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_let(self, xml_tree):
        """
        Build xml tree for let statement in jack.
        """
        tk = self.__tokenizer
        # 'let'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # varName
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        if tk.get_token_type() == SYMBOL and tk.get_next_token() == '[':
            # '['
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # expression
            self.__compile_expression(SubElement(xml_tree, "expression"))
            # ']'
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

        # '='
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # expression
        self.__compile_expression(SubElement(xml_tree, "expression"))
        # ';'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_while(self, xml_tree):
        """
        Build xml tree for while statement in jack.
        """
        tk = self.__tokenizer
        # 'while'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # '('
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # expression
        self.__compile_expression(SubElement(xml_tree, "expression"))
        # ')'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # '{'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # statements
        self.__compile_statements(SubElement(xml_tree, "statements"))
        # '}'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_return(self, xml_tree):
        """
        Build xml tree for return statement in jack.
        """
        tk = self.__tokenizer
        # 'return'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        if not(tk.get_next_token() == ';'):
            # expression
            self.__compile_expression(SubElement(xml_tree, "expression"))
        # ';'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_if(self, xml_tree):
        """
        Build xml tree for if statement in jack.
        """
        tk = self.__tokenizer
        # 'if'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # '('
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # expression
        self.__compile_expression(SubElement(xml_tree, "expression"))
        # ')'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # '{'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # statements
        self.__compile_statements(SubElement(xml_tree, "statements"))
        # '}'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # ('else''{'statements'}')?
        if tk.get_token_type() == KEYWORD and tk.get_next_token() == ELSE:
            # 'else'
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # '{'
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # statements
            self.__compile_statements(SubElement(xml_tree, "statements"))
            # '}'
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

    def __compile_expression(self, xml_tree):
        """
        Build xml tree for an expression in jack.
        """
        tk = self.__tokenizer
        # term
        self.__compile_term(SubElement(xml_tree, "term"))
        while tk.get_token_type() == SYMBOL and tk.get_next_token() in OP_LIST:
            # op
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # term
            self.__compile_term(SubElement(xml_tree, "term"))

    def __compile_term(self, xml_tree):
        """
        Build xml tree for a term in jack.
        """
        tk = self.__tokenizer

        # unaryOp term
        if tk.get_next_token() in UNARY_OP_LIST:
            # unaryOp
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # term
            self.__compile_term(SubElement(xml_tree, "term"))
            return

        # integerConstant/stringConstant
        if tk.get_token_type() in [INT_CONST, STRING_CONST]:
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            return

        # keywordConstant
        if tk.get_next_token() in [TRUE, FALSE, NULL, THIS]:
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            return

        # '(' expression ')'
        if tk.get_token_type() == SYMBOL and tk.get_next_token() == '(':
            # '('
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # expression
            self.__compile_expression(SubElement(xml_tree, "expression"))
            # ')'
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            return

        if tk.get_token_type() == IDENTIFIER:
            # varName/ subroutineName
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

            # '[' expression ']'
            if tk.get_token_type() == SYMBOL and tk.get_next_token() == '[':
                # '['
                SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
                tk.advance()
                # expression
                self.__compile_expression(SubElement(xml_tree, "expression"))
                # ']'
                SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
                tk.advance()
                return

            # subroutineCall
            if tk.get_token_type() == SYMBOL and tk.get_next_token() in ['(', '.']:
                # subroutineCall
                self.__compile_subroutine_call(xml_tree)  # No SubElement!
                return

    def __compile_expression_list(self, xml_tree):
        """
        Build xml tree for expression list in jack.
        """
        tk = self.__tokenizer
        # check is list is empty, meaning next token is )
        if tk.get_token_type() == SYMBOL and tk.get_next_token() == ')':
            # xml_tree = '\n'
            return

        # expression
        self.__compile_expression(SubElement(xml_tree, 'expression'))
        # (, expression)*
        while tk.get_token_type() == SYMBOL and tk.get_token_type() == ',':
            # ','
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # expression
            self.__compile_expression(SubElement(xml_tree, 'expression'))


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
