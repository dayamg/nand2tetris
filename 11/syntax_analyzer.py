import os
import re
import sys

from lxml.etree import Element, SubElement, ElementTree
from compiler import SymbolTable

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

QUOTATION_MARK = "\""

KEY_WORD_DICT = {"CLASS": "class", "METHOD": "method", "FUNCTION": "function", "CONSTRUCTOR": "constructor",
                 "FIELD": "field", "STATIC": "static", "VAR": "var", "INT": "int", "CHAR": "char",
                 "BOOLEAN": "boolean", "VOID": "void", "TRUE": "true", "FALSE": "false", "NULL": "null",
                 "THIS": "this", "LET": "let", "DO": "do", "IF": "if", "ELSE": "else", "WHILE": "while",
                 "RETURN": "return"}

KEY_WORD_LIST = ["class", "method", "function", "constructor", "field", "static", "var", "int", "char",
                 "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while",
                 "return"]

KEY_WORD_REGEX_PATTERN = re.compile(r"class|method|function|constructor|field|static|var|int|char|boolean|void|true"
                                    r"|false|null|this|let|do|if|else|while|return")
KEY_WORD_NO_SPACE_PATTERN = re.compile(r"true|false|null|this|if|else|while|return")

STRING_CONST_REGEX = re.compile(r"\"(.*?\n*)*\"")

COMMENT_PATTERN = re.compile(r"\/\/.*|\/\*\*?.*?(\n.*?)*\*\/")

SYMBOLS_LIST = ['{', '}',
                '(', ')',
                '[', ']',
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

g_in_multiple_line_comments = False


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

        self.__string_counter = 0
        self.__string_list = []

        self.__token_index = NO_CURR_TOKEN_INDEX  # = -1
        self.__token_list = []  # A list of tuples, (token, token_type).

        self.__get_token_list()

        if self.__token_list:
            self.__token_index = 0
            self.get_next_token()
            self.get_token_type()

    def get_next_token(self):
        """
        Yep. A getter. I'm very disappointed with myself for this OOPy behaviour.
        """
        if self.has_more_tokens():
            self.__next_token = self.__token_list[self.__token_index]
            return self.__next_token[0]
        return None

    def get_token_type(self):
        """
        Another getter. Type is in one of the elements of TOKEN_TYPE_DICT.
        """
        if self.has_more_tokens():
            self.__next_token = self.__token_list[self.__token_index]
            return self.__next_token[1]
        return None

    def __replace_spaces_in_string(self, line):
        """
        There is a problem when splitting a line by spaces, in case of strings that include space, e.g., "hi there".
        This function replaces the spaces with \n and eventually the string is reconstructed (replaced back).
        """
        for match in re.finditer(STRING_CONST_REGEX, line):
            if match:
                start_ind, end_ind = match.span()
                mid_line = line[start_ind:end_ind]
                line = line[0:start_ind] + mid_line.replace(SPACE_CHAR, NEW_LINE) + line[end_ind:]
        return line

    def __get_token_list(self):
        """
        Initializes a list of all tokens in the input file.
        """

        for line in self.__input_file:
            line = self.__parse_strings(line)
            line = remove_comments_and_stuff(line)
            line = remove_multiple_line_comments(line)
            if not line:
                continue

            line_separated_array = line.split(SPACE_CHAR)
            for element in line_separated_array:
                if element in SYMBOLS_LIST:  # Get rid of elements which are symbols
                    self.__token_list.append((element, SYMBOL))
                    continue

                symbols_index_list = []  # List of all indices in which the string contains a symbol

                for i in range(len(element)):
                    if element[i] in SYMBOLS_LIST:
                        symbols_index_list.append(i)

                if not symbols_index_list:
                    self.__parse_one_element(element)
                    continue

                i = 0
                prev_part_last_index = 0
                for i in symbols_index_list:
                    self.__parse_one_element(element[prev_part_last_index:i])
                    self.__token_list.append((element[i], SYMBOL))
                    prev_part_last_index = i + 1

                self.__parse_one_element(
                    element[i + 1:])  # Parse last part, or the whole string if there are no symbols

    def __parse_strings(self, line):
        for match in re.finditer(STRING_CONST_REGEX, line):
            start_ind, end_ind = match.span()
            curr_string = line[start_ind:end_ind]
            line = line.replace(curr_string, QUOTATION_MARK + str(self.__string_counter) + QUOTATION_MARK)
            self.__string_list.append(curr_string)
            self.__string_counter += 1
            return line
        return line

    def __parse_one_element(self, element):
        """
        Parses one segment of a line (with no symbols in it!)
        """
        if element.isspace() or not element:
            return

        if element in KEY_WORD_LIST:
            self.__token_list.append((element, KEYWORD))
            return

        elif element in SYMBOLS_LIST:  # Again, not supposed to happen
            self.__token_list.append((element, SYMBOL))
            return

        elif element.isdigit():
            self.__token_list.append((int(element), INT_CONST))
            return

        is_string_const_match = re.match(STRING_CONST_REGEX, element)
        if is_string_const_match:
            if is_string_const_match.end() >= len(element) - 1:
                element = element.strip(QUOTATION_MARK)
                # We now replace back the new lines with space chars.
                element = self.__string_list[int(element)]
                element = element.strip(QUOTATION_MARK)
                self.__token_list.append((element, STRING_CONST))
                return

        else:  # Only other option is variable name
            self.__token_list.append((element, IDENTIFIER))

    def has_more_tokens(self):
        """
        :return: true of current index is not the last.
        """
        return self.__token_index <= len(self.__token_list) - 1

    def advance(self):
        self.__token_index += 1
        self.get_next_token()


def remove_multiple_line_comments(line):
    """
    Assume no constant srings with a comment in it is inside.
    check for // and /* commands on multiple lines and remove the comment parts.
    """
    global g_in_multiple_line_comments
    start_comment_index = None
    end_comment_index = None

    for i in range(len(line) - 1):
        if not g_in_multiple_line_comments:
            if line[i] == '/':
                # check for inline command '//'
                if line[i + 1] == '/':
                    line = line[:i]
                    return line
                # check for multi-line command '/*'
                if line[i + 1] == '*':
                    g_in_multiple_line_comments = True
                    start_comment_index = i

        # look for end '*/' of multi line comment
        else:
            if line[i:i + 2] == "*/":
                g_in_multiple_line_comments = False
                end_comment_index = i + 2

    # all line is in or out multi-line commend.
    if start_comment_index is None and end_comment_index is None:
        if g_in_multiple_line_comments:
            return ""
        else:
            return line

    # if "bla */ important stuff /* bla"
    if start_comment_index is not None and end_comment_index is not None \
            and start_comment_index > end_comment_index:
        return line[end_comment_index:start_comment_index]

    if start_comment_index is None:
        start_comment_index = 0

    if end_comment_index is None:
        end_comment_index = len(line)

    return line[0:start_comment_index] + line[end_comment_index:len(line)]


def remove_comments_and_stuff(line):
    """
    Removes inline comments, tabs and newlines. Replaces double (or triple, or ...) spaces with one space.
    (Spaces are not removed, as it is important later)
    """
    line = re.sub(COMMENT_PATTERN, '', line)  # remove comments
    tabs_pattern = re.compile(r"\t+")
    new_line_pattern = re.compile(r"\n*")
    line = re.sub(tabs_pattern, SPACE_CHAR, line)  # removes tabs
    line = re.sub(new_line_pattern, '', line)  # removes new lines

    multiple_spaces_pattern = re.compile(r"  +")
    line = re.sub(multiple_spaces_pattern, SPACE_CHAR, line)  # replaces multiple spaces with only one

    return line.strip(SPACE_CHAR)  # Removes spaces in the beginning or end of line


class SyntaxAnalyzer:

    def __init__(self, jack_path_input, xml_path, vm_file_path):
        """
        Yeah, this funky function is for constructing shit, you know.
        """
        jack_file = open(jack_path_input, READ_MODE)
        self.__tokenizer = JackTokenizer(jack_file)
        self.__symbols_table = SymbolTable()
        self.__xml_file = xml_path
        self.__vm_file = open(vm_file_path, READ_MODE)
        self.__xml_tree = None
        self.__class_name = None
        next_token = self.__tokenizer.get_next_token()
        if next_token is not None:
            self.__xml_tree = Element(CLASS)
            self.__compile_class(self.__xml_tree)
        tree = ElementTree(self.__xml_tree)
        jack_file.close()
        tree.write(xml_path, pretty_print=True, encoding="utf-8")

    def __compile_class(self, xml_tree):
        """
        Build xml tree for a class in jack.
        """
        tk = self.__tokenizer

        # 'class'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # className
        self.__class_name = tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # '{'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # classVarDec*
        while tk.get_token_type() == KEYWORD and tk.get_next_token() in [FIELD, STATIC]:
            self.__compile_class_var_dec(SubElement(xml_tree, "classVarDec"))

        # print(self.__symbols_table.get_class_symbol_dict())
        # print()
        # subroutineDec*
        while tk.get_token_type() == KEYWORD and tk.get_next_token() in [CONSTRUCTOR, FUNCTION, METHOD]:
            self.__compile_subroutine_dec(SubElement(xml_tree, "subroutineDec"))
            # print(self.__symbols_table.get_subroutine_symbol_dict())
            # print()

        # '}'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_class_var_dec(self, xml_tree):
        """
        Build xml tree for a class var declaration in jack.
        """
        tk = self.__tokenizer
        # 'static/field'(keyword)
        var_kind = tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # type (keyword/identifier)
        var_type = tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # varName (identifier)
        var_name = tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        self.__symbols_table.add_new_symbol(var_name, var_type, var_kind)

        # (, varName)*
        while tk.get_token_type() == SYMBOL and tk.get_next_token() == ',':
            # ','
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # varName
            var_name = tk.get_next_token()
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            self.__symbols_table.add_new_symbol(var_name, var_type, var_kind)

        # ';'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_subroutine_dec(self, xml_tree):
        """
        build xml tree for a subroutine declaration in jack.
        """
        tk = self.__tokenizer
        self.__symbols_table.start_subroutine()

        # 'constructor/function/method'(keyword)
        subroutine_type = tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        if subroutine_type == "method":
            self.__symbols_table.add_new_symbol("this", self.__class_name, "arg")

        # 'void'/type (keyword/identifier)
        tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # subroutineName (identifier)
        subroutine_name = tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # '('
        tk.get_next_token()
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
            self.__compile_var_dec(SubElement(xml_tree, "varDec"))
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
            xml_tree.text = '\n'
            return

        var_kind = "arg"

        # type
        var_type = tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # varName
        var_name = tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        self.__symbols_table.add_new_symbol(var_name, var_type, var_kind)

        # (, type varName)*
        while tk.get_token_type() == SYMBOL and tk.get_next_token() == ',':
            # ','
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # type
            var_type = tk.get_next_token()
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # varName
            var_name = tk.get_next_token()
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            self.__symbols_table.add_new_symbol(var_name, var_type, var_kind)

    def __compile_var_dec(self, xml_tree):
        """
        Build xml tree for a variable declaration in jack.
        """
        tk = self.__tokenizer

        # 'var'(keyword)
        var_kind = tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # type (keyword/identifier)
        var_type = tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # varName (identifier)
        var_name = tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        self.__symbols_table.add_new_symbol(var_name, var_type, var_kind)

        # (, varName)*
        while tk.get_token_type() == SYMBOL and tk.get_next_token() == ',':
            # ','
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # varName
            var_name = tk.get_next_token()
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            self.__symbols_table.add_new_symbol(var_name, var_type, var_kind)

        # ';'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_statements(self, xml_tree):
        """
        Build xml tree for statements in jack.
        """
        tk = self.__tokenizer
        # check is list is empty, meaning next token is }
        if tk.get_token_type() == SYMBOL and tk.get_next_token() == '}':
            xml_tree.text = '\n'
            return

        # statement*
        while tk.get_token_type() == KEYWORD and tk.get_next_token() in [LET, IF, WHILE, DO, RETURN]:
            if tk.get_next_token() == LET:
                self.__compile_let(SubElement(xml_tree, "letStatement"))
            if tk.get_next_token() == IF:
                self.__compile_if(SubElement(xml_tree, "ifStatement"))
            if tk.get_next_token() == WHILE:
                self.__compile_while(SubElement(xml_tree, "whileStatement"))
            if tk.get_next_token() == DO:
                self.__compile_do(SubElement(xml_tree, "doStatement"))
            if tk.get_next_token() == RETURN:
                self.__compile_return(SubElement(xml_tree, "returnStatement"))

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
        if not (tk.get_next_token() == ';'):
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
            SubElement(xml_tree, tk.get_token_type()).text = str(tk.get_next_token())
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
            xml_tree.text = '\n'
            return

        # expression
        self.__compile_expression(SubElement(xml_tree, 'expression'))
        # (, expression)*
        while tk.get_token_type() == SYMBOL and tk.get_next_token() == ',':
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
        SyntaxAnalyzer(jack_path_input, xml_path)

    if os.path.isdir(jack_path_input):
        jack_path_input = jack_path_input.rstrip('/')
        for filename in os.listdir(jack_path_input):
            if filename.endswith(JACK_SUFFIX):
                filename_jack_path = os.path.join(jack_path_input, filename)
                xml_path = filename_jack_path.replace(JACK_SUFFIX, XML_SUFFIX)
                SyntaxAnalyzer(filename_jack_path, xml_path)

