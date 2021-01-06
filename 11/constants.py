import re

VM_COMMENTS = 0

CLASS_LEVEL_IDENTIFIERS = ["static", "field"]
SUBROUTINE_LEVEL_IDENTIFIERS = ["argument", "local"]

TYPE_INDEX = 0
KIND_INDEX = 1
COUNTER_INDEX = 2

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