import os
import re
import sys

from lxml.etree import Element, SubElement, ElementTree
from compiler import SymbolTable
from tokenizer import JackTokenizer


JACK_SUFFIX = ".jack"
XML_SUFFIX = ".xml"
VM_SUFFIX = ".vm"
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
VAR = "var"
INT = "int"
CHAR = "char"
BOOLEAN = "boolean"
VOID = "void"
TRUE = "true"
FALSE = "false"
NULL = "null"
LET = "let"
DO = "do"
IF = "if"
ELSE = "else"
WHILE = "while"
RETURN = "return"

# Segments
CONST = "constant"
ARG = "argument"
LOCAL = "local"
STATIC = "static"  # Also a keyword
THIS = "this"   # Also a keyword
THAT = "that"
POINTER = "pointer"
TEMP = "temp"

# Jack "Macros"
FALSE_VALUE = 0
NULL_VALUE = 0
TRUE_VALUE = -1
THIS_POINTER_VALUE = 0
THAT_POINTER_VALUE = 1

QUOTATION_MARK = "\""

KEYWORD_DICT = {"CLASS": "class", "METHOD": "method", "FUNCTION": "function", "CONSTRUCTOR": "constructor",
                 "FIELD": "field", "STATIC": "static", "VAR": "var", "INT": "int", "CHAR": "char",
                 "BOOLEAN": "boolean", "VOID": "void", "TRUE": "true", "FALSE": "false", "NULL": "null",
                 "THIS": "this", "LET": "let", "DO": "do", "IF": "if", "ELSE": "else", "WHILE": "while",
                 "RETURN": "return"}

KEYWORD_LIST = ["class", "method", "function", "constructor", "field", "static", "var", "int", "char",
                 "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while",
                 "return"]

VAR_KIND_DICT = {"field": THIS, "static": STATIC, "local": LOCAL, "argument": ARG}

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
OP_CMD_DICT = {'+': "add", '-': "sub", '*': "call Math.multiply 2", '/': "call Math.divide 2", '&': "and", '|': "or",
                '<': "lt", '>': "gt", '=': "eq"}
UNARY_OP_LIST = ['~', '-']

SYMBOL_TRANSLATION_DICT = {">": "&gt;", "<": "&lt;", "&": "&amp;", "\'": "&quot;"}

TOKEN_TYPE_DICT = {"KEYWORD": "keyword", "SYMBOL": "symbol", "IDENTIFIER": "identifier",
                   "INT_CONST": "integerConstant", "STRING_CONST": "stringConstant"}

NO_CURR_TOKEN_INDEX = -1

g_in_multiple_line_comments = False



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
        Nothing to the vm file.
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
        Update symbols tables.
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
            self.__symbols_table.add_new_symbol("this", self.__class_name, ARG)

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
        # self.__compile_subroutine_body(SubElement(xml_tree, "subroutineBody"))

        # def __compile_subroutine_body(self, xml_tree):
        """
        Build xml tree for a subroutine body in jack.
        """
        tk = self.__tokenizer
        # '{'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        n_locals = 0
        # varDec*
        while tk.get_token_type() == KEYWORD and tk.get_next_token() == VAR:
            n_locals += self.__compile_var_dec(SubElement(xml_tree, "varDec"))

        full_name = self.__class_name + "." + subroutine_name
        self.__write_function(full_name, str(n_locals))

        if subroutine_type == CONSTRUCTOR:
            # Allocate memory for class instance and init THIS segment.
            self.__write_push(CONST, self.__symbols_table.var_count(FIELD))
            self.__write_call("Memory.alloc", 1)
            self.__write_pop(POINTER, 0)

        if subroutine_type == METHOD:
            # Init THIS segment.
            self.__write_push(ARG, 0)
            self.__write_pop(POINTER, 0)

        # statements
        self.__compile_statements(SubElement(xml_tree, "statements"))

        # '}'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_parameter_list(self, xml_tree):
        """
        Build xml tree for a parameter list in jack.
        Update symbol table.
        """
        tk = self.__tokenizer

        # check is list is empty, meaning next token is )
        if tk.get_token_type() == SYMBOL and tk.get_next_token() == ')':
            xml_tree.text = '\n'
            return

        var_kind = ARG

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
        Update symbol table.
        """
        tk = self.__tokenizer
        num_of_vars = 1

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
            num_of_vars += 1
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
        return num_of_vars

    def __compile_statements(self, xml_tree):
        """
        Build xml tree for statements in jack.
        Nothing to write to vm file.
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
        first_name = tk.get_next_token()
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()
        # subroutineCall
        self.__compile_subroutine_call(xml_tree, first_name)  # No SubElement!
        # remove unnecessary returned value
        self.__write_pop(TEMP, 0)

        # ';'
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

    def __compile_subroutine_call(self, xml_tree, first_token):
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
            subroutine_name = tk.get_next_token()
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()

            if self.__symbols_table.is_in(first_token):
                is_method = 1
                # If first token is a variable, then this subroutine is its method.
                # We need to insert its this address as the first argument to the vm stack.
                var_kind = self.__symbols_table.get_kind(first_token)
                var_index = self.__symbols_table.get_index(first_token)
                self.__write_push(var_kind, var_index)

                # Now we need the class name for the vm call write.
                class_name = self.__symbols_table.get_type(first_token)

            else:
                # The first token is a class name (using function).
                is_method = 0
                class_name = first_token

            full_name = class_name + "." + subroutine_name

        else:
            # first_token is a subroutine of this instance.
            is_method = 1
            # Push this address as first argument.
            self.__write_push(POINTER, 0)
            full_name = self.__class_name + "." + first_token

        # '('
        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # expressionList
        n_args = self.__compile_expression_list(SubElement(xml_tree, "expressionList"))

        self.__write_call(full_name, n_args + is_method)

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
        var_name = tk.get_next_token()
        var_kind = self.__symbols_table.get_kind(var_name)
        var_index = self.__symbols_table.get_index(var_name)

        SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
        tk.advance()

        # Check if it is an array assignment.
        if tk.get_token_type() == SYMBOL and tk.get_next_token() == '[':
            # Calc where to store the result, push start arr address.
            self.__write_push(var_kind, var_index)
            # '['
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # expression
            self.__compile_expression(SubElement(xml_tree, "expression"))
            # ']'
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            self.__vm_file.write("add")
            # '='
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # expression
            self.__compile_expression(SubElement(xml_tree, "expression"))

            # Pop the value to be assign to temp 0
            self.__write_pop(TEMP, 0)
            # Pop the array address to pointer 1, meaning store at That segment.
            self.__write_pop(POINTER, 1)
            # Push the value to be assign back to the stack.
            self.__write_push(TEMP, 0)
            # Pop it to the correct place in the array, which that 0 is pointing to
            self.__write_pop(THAT, 0)

        else:
            # '='
            SubElement(xml_tree, tk.get_token_type()).text = tk.get_next_token()
            tk.advance()
            # expression
            self.__compile_expression(SubElement(xml_tree, "expression"))
            # Pop the value to be assign to the var_name location.
            self.__write_pop(var_kind, var_index)

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

        # If a value is returned, return it.
        if not (tk.get_next_token() == ';'):
            # expression
            self.__compile_expression(SubElement(xml_tree, "expression"))
            self.__vm_file.write(RETURN)

        # If no value is returned, return 0.
        self.__write_push(CONST, 0)
        self.__vm_file.write(RETURN)

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
            first_name = tk.get_next_token()
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
                self.__compile_subroutine_call(xml_tree, first_name)  # No SubElement!
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

        return 0  # TBD!! return number of expressions

    def write_expression_list(self):
        """
        Writes the VM commands of a list of expressions, assuming that the opening bracket, '(', was already parsed.
        Returns the number of expressions in the list.
        """
        self.__write_comment("Parsing expression list. ")
        tk = self.__tokenizer
        number_of_expressions = 0
        # check is list is empty, meaning next token is )
        if tk.get_token_type() == SYMBOL and tk.get_next_token() == ')':
            tk.advance()
            return number_of_expressions

        # else, parse first expression, and then loop until over
        number_of_expressions += 1
        self.__write_comment("Expression No. # " + str(number_of_expressions))
        self.write_expression()

        # as long as there are more ',' symbols, there are more expressions in the list to parse
        while tk.get_token_type() == SYMBOL and tk.get_next_token() == ',':
            number_of_expressions += 1
            self.__write_comment("Expression No. # " + str(number_of_expressions))
            tk.advance()
            self.write_expression()

        return number_of_expressions

    def write_term(self):
        """
        Writes a term in VM instructions.
        """

        tk = self.__tokenizer
        current_token = tk.get_next_token()
        current_token_type = tk.get_token_type()

        # If term is Int Constant, write "push <int value>"
        if current_token_type == INT_CONST:
            self.__write_comment("writing term, int const: " + current_token)
            self.__write_push(CONST, current_token)
            tk.advance()
            return

        # If term is string constant, we should push each char
        elif current_token_type == STRING_CONST:
            self.__write_comment("writing term, string const: " + current_token)
            self.__write_push(CONST, len(current_token))  # Push the argument len(str_const) for String.new()
            self.__write_call("String.new", 1)  # Create new string
            for char in current_token:
                self.__write_push(CONST, ord(char))  # push one by one the string's chars
                self.__write_call("String.appendChar", 2)
            tk.advance()
            return

        # If the term is a variable
        elif current_token_type == IDENTIFIER and self.__symbols_table.var_exists(current_token):
            var_kind = self.__symbols_table.get_kind(current_token)
            self.__write_comment("writing term, variable: " + current_token + " of kind " + var_kind)

            if var_kind == FIELD:
                self.__write_push(THIS, self.__symbols_table.get_index(current_token))
            elif var_kind == STATIC:
                self.__write_push(STATIC, self.__symbols_table.get_index(current_token))
            elif var_kind == LOCAL:
                self.__write_push(LOCAL, self.__symbols_table.get_index(current_token))
            elif var_kind == ARG:
                self.__write_push(ARG, self.__symbols_table.get_index(current_token))

            tk.advance()
            return

        # one of the "macros" true, false, none or this
        elif current_token_type == KEYWORD:
            self.__write_comment("writing term, keyword: " + current_token)
            if current_token == FALSE:
                self.__write_push(CONST, FALSE_VALUE)  # push const 0
            elif current_token == TRUE:
                self.__write_push(CONST, TRUE_VALUE)  # push const -1
            elif current_token == NULL:
                self.__write_push(CONST, NULL_VALUE)  # push const 0
            elif current_token == THIS:
                self.__write_push(POINTER, THIS_POINTER_VALUE) # push pointer 0
            tk.advance()
            return

        # '(' expression ')'
        elif current_token_type == SYMBOL and current_token == '(':
            self.__write_comment("writing (expression): (")
            # '('
            tk.advance()
            # expression
            self.write_expression()  # Calls itself recursively, evaluate the expression inside the parentheses
            # ')'
            self.__write_comment("writing (expression): )")
            tk.advance()
            return

        #  ~expression or -expression
        elif current_token in UNARY_OP_LIST:
            self.__write_comment("writing unary operation: " + current_token)

            if current_token_type == '-':
                tk.advance()
                self.write_term()
                self.__write_arithmetic("neg")
            else:  # current_token_type == '~'
                tk.advance()
                self.write_term()
                self.__write_arithmetic("not")
            tk.advance()
            return

        #  method(exp1, exp2, ..., expn) or Class.func(exp1,...,expn)
        elif current_token_type == IDENTIFIER:
            self.write_subroutine_call()

        elif current_token_type == SYMBOL and current_token == '[':
            # Arrays - TBD
            pass

    def write_subroutine_call(self):
        """
        Compiles a call for a subroutine, func(x1,...,xn) or Class.func(x1,...,xn)
        """
        tk = self.__tokenizer
        func_name_prefix = tk.get_next_token()
        tk.advance()

        # Checks if the function is of type Class.func or obj.func
        if tk.get_next_token() == '.':
            if self.__symbols_table.var_exists(func_name_prefix):
                # In case it is a call through an object, e.g., game.run():
                tk.advance()
                func_name = func_name_prefix + '.' + tk.get_next_token()  # Update func name to be "obj.func"
                var_type, var_kind, var_index = self.__symbols_table.get_all_info(func_name_prefix)

                # First, push the object, while converting var_kind (field, static, local, argument)
                # into the corresponding segment:
                self.__write_push(VAR_KIND_DICT[var_kind], var_index)


        # Now parse the argument list
        num_of_args = self.write_expression_list()
        if num_of_args == 0:
            self.__write_push(CONST, '0')  # In case of void function, push 0


    def write_expression(self):
        """
        Writes an expression, by writing terms until there is no more operators. Assumes the expression is not empty.
        """
        tk = self.__tokenizer
        self.write_term()  # Writes the first term in < term (operator term)* >
        while tk.get_token_type() == SYMBOL and tk.get_next_token() in OP_LIST:
            binary_op = tk.get_next_token()
            tk.advance()
            self.write_term()  # Writes the second term in < term (operator term)* >

            # Write arithmetic cmd - translate ['+', '-', '*', '/', '&', '|', '<', '>', '='] into VM cmd,
            # using the OP_CMD_DICT
            self.__vm_file.write(OP_CMD_DICT[binary_op] + NEW_LINE)

    def __write_comment(self, comment):
        """
        Writes VM comment.
        """
        self.__vm_file.write("/// " + comment + NEW_LINE)

    def __write_push(self, segment, index):
        """
        Writes command "push segment index", e.g., "push constant 3" or "push local 0"
        """
        self.__vm_file.write("push " + segment + " " + str(index) + NEW_LINE)

    def __write_pop(self, segment, index):
        """
        Writes command "pop segment index", e.g., "push constant 3" or "pop local 0"
        """
        self.__vm_file.write("pop " + segment + " " + str(index) + NEW_LINE)

    def __write_function(self, func_name, num_of_vars):
        """
        Writes commands like "function f k"
        """
        self.__vm_file.write("function " + func_name + " " + str(num_of_vars) + NEW_LINE)

    def __write_call(self, func_name, num_of_vars):
        """
        Writes commands like "call f k"
        """
        self.__vm_file.write("call " + func_name + " " + str(num_of_vars) + NEW_LINE)

    def __write_arithmetic(self, arit_op):
        """
        Writes the command arit_op
        """
        self.__vm_file.write(arit_op + NEW_LINE)


