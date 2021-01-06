from constants import *
import os
import re
import sys
from tokenizer import JackTokenizer
from compiler import SymbolTable


class SyntaxAnalyzer:
    def __init__(self, jack_path_input, vm_file_path):
        """
        Create a syntax analyzer and compile the given jack_path_input
        file to vm_file_path file.
        """
        jack_file = open(jack_path_input, READ_MODE)
        self.__tokenizer = JackTokenizer(jack_file)
        self.__symbols_table = SymbolTable()
        self.__vm_file = open(vm_file_path, WRITE_MODE)
        self.__class_name = None
        self.__while_statement_cnt = -1
        self.__if_statement_cnt = -1
        next_token = self.__tokenizer.get_next_token()
        if next_token is not None:
            self.__compile_class()
        jack_file.close()
        self.__vm_file.close()

    def __compile_class(self):
        """
        Build xml tree for a class in jack.
        Nothing to the vm file.
        """
        if VM_COMMENTS:
            self.__write_comment("Compiling class.")

        tk = self.__tokenizer

        # 'class'
        tk.advance()
        # className
        self.__class_name = tk.get_next_token()
        tk.advance()
        # '{'
        tk.advance()

        # classVarDec*
        while tk.get_token_type() == KEYWORD and tk.get_next_token() in [FIELD, STATIC]:
            self.__compile_class_var_dec()

        # subroutineDec*
        while tk.get_token_type() == KEYWORD and tk.get_next_token() in [CONSTRUCTOR, FUNCTION, METHOD]:
            self.__compile_subroutine_dec()

        # '}'
        tk.advance()

    def __compile_class_var_dec(self):
        """
        Build xml tree for a class var declaration in jack.
        Update symbols tables.
        """
        if VM_COMMENTS:
            self.__write_comment("Compiling class var dec.")

        tk = self.__tokenizer
        # 'static/field'(keyword)
        var_kind = tk.get_next_token()
        tk.advance()
        # type (keyword/identifier)
        var_type = tk.get_next_token()
        tk.advance()
        # varName (identifier)
        var_name = tk.get_next_token()
        tk.advance()
        self.__symbols_table.add_new_symbol(var_name, var_type, var_kind)

        # (, varName)*
        while tk.get_token_type() == SYMBOL and tk.get_next_token() == ',':
            # ','
            tk.advance()
            # varName
            var_name = tk.get_next_token()
            tk.advance()
            self.__symbols_table.add_new_symbol(var_name, var_type, var_kind)

        # ';'
        tk.advance()

    def __compile_subroutine_dec(self):
        """
        build xml tree for a subroutine declaration in jack.
        """
        if VM_COMMENTS:
            self.__write_comment("Compiling subroutine_dec.")

        tk = self.__tokenizer
        self.__symbols_table.start_subroutine()

        # 'constructor/function/method'(keyword)
        subroutine_type = tk.get_next_token()
        tk.advance()

        if subroutine_type == "method":
            self.__symbols_table.add_new_symbol("this", self.__class_name, ARG)

        # 'void'/type (keyword/identifier)
        tk.get_next_token()
        tk.advance()
        # subroutineName (identifier)
        subroutine_name = tk.get_next_token()
        tk.advance()
        # '('
        tk.get_next_token()
        tk.advance()

        # 'parameterList'
        self.__compile_parameter_list()

        # ')'
        tk.advance()
        # '{'
        tk.advance()

        n_locals = 0
        # varDec*
        while tk.get_token_type() == KEYWORD and tk.get_next_token() == VAR:
            n_locals += self.__compile_var_dec()

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
        self.__compile_statements()
        # '}'
        tk.advance()

    def __compile_parameter_list(self):
        """
        Build xml tree for a parameter list in jack.
        Update symbol table.
        """
        if VM_COMMENTS:
            self.__write_comment("Compiling parameter list.")

        tk = self.__tokenizer

        # check is list is empty, meaning next token is )
        if tk.get_token_type() == SYMBOL and tk.get_next_token() == ')':
            return

        var_kind = ARG

        # type
        var_type = tk.get_next_token()
        tk.advance()
        # varName
        var_name = tk.get_next_token()
        tk.advance()
        self.__symbols_table.add_new_symbol(var_name, var_type, var_kind)

        # (, type varName)*
        while tk.get_token_type() == SYMBOL and tk.get_next_token() == ',':
            # ','
            tk.advance()
            # type
            var_type = tk.get_next_token()
            tk.advance()
            # varName
            var_name = tk.get_next_token()
            tk.advance()
            self.__symbols_table.add_new_symbol(var_name, var_type, var_kind)

    def __compile_var_dec(self):
        """
        Build xml tree for a variable declaration in jack.
        Update symbol table.
        """
        if VM_COMMENTS:
            self.__write_comment("Compiling var dec.")

        tk = self.__tokenizer
        num_of_vars = 1

        # 'var'(keyword)
        var_kind = LOCAL
        tk.advance()

        # type (keyword/identifier)
        var_type = tk.get_next_token()
        tk.advance()

        # varName (identifier)
        var_name = tk.get_next_token()
        tk.advance()
        self.__symbols_table.add_new_symbol(var_name, var_type, var_kind)

        # (, varName)*
        while tk.get_token_type() == SYMBOL and tk.get_next_token() == ',':
            num_of_vars += 1
            # ','
            tk.advance()
            # varName
            var_name = tk.get_next_token()
            tk.advance()
            self.__symbols_table.add_new_symbol(var_name, var_type, var_kind)

        # ';'
        tk.advance()
        return num_of_vars

    def __compile_statements(self):
        """
        Build xml tree for statements in jack.
        Nothing to write to vm file.
        """
        if VM_COMMENTS:
            self.__write_comment("Compiling statements.")

        tk = self.__tokenizer
        # check is list is empty, meaning next token is }
        if tk.get_token_type() == SYMBOL and tk.get_next_token() == '}':
            return

        # statement*
        while tk.get_token_type() == KEYWORD and tk.get_next_token() in [LET, IF, WHILE, DO, RETURN]:
            if tk.get_next_token() == LET:
                self.__compile_let()
            if tk.get_next_token() == IF:
                self.__compile_if()
            if tk.get_next_token() == WHILE:
                self.__compile_while()
            if tk.get_next_token() == DO:
                self.__compile_do()
            if tk.get_next_token() == RETURN:
                self.__compile_return()

    def __compile_do(self):
        """
        Build xml tree for do statement in jack.
        """
        if VM_COMMENTS:
            self.__write_comment("Compiling do statement.")

        tk = self.__tokenizer
        # 'do'
        tk.advance()
        # subroutineName/(className/varName)
        first_name = tk.get_next_token()
        tk.advance()
        # subroutineCall
        self.__compile_subroutine_call(first_name)  # No SubElement!
        # remove unnecessary returned value
        self.__write_pop(TEMP, 0)
        # ';'
        tk.advance()

    def __compile_subroutine_call(self, first_token):
        """
        Build xml tree for subroutine call in jack.
        First token of the identifier subroutineName/(className/varName) should be out already.
        """
        self.__write_comment("Compiling subroutine call. ")

        tk = self.__tokenizer

        if tk.get_token_type() == SYMBOL and tk.get_next_token() == '.':
            # '.'
            tk.advance()
            # subroutineName
            subroutine_name = tk.get_next_token()
            tk.advance()
            if VM_COMMENTS:
                self.__write_comment("Compiling subroutine call to " + subroutine_name)

            if self.__symbols_table.var_exists(first_token):
                is_method = 1
                # If first token is a variable, then this subroutine is its method.
                # We need to insert its this address as the first argument to the vm stack.
                var_kind = self.__symbols_table.get_kind(first_token)
                var_index = self.__symbols_table.get_index(first_token)
                self.__write_push(VAR_KIND_DICT[var_kind], var_index)

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
        tk.advance()

        # expressionList
        n_args = self.write_expression_list()
        self.__write_call(full_name, n_args + is_method)

        # ')'
        tk.advance()

    def __is_next_token_array(self):
        """
        Returns true if the next token is in form of var[], where var is in the symbols table.
        """
        return self.__symbols_table.var_exists(self.__tokenizer.get_next_token()) and self.__tokenizer.peek(1) == '['

    def __compile_array_evaluation(self):
        """
        Compiles the evaluation part of an array expression.
        """
        if VM_COMMENTS:
            self.__write_comment("Compiling array evaluation.")

        tk = self.__tokenizer

        # varName
        var_name = tk.get_next_token()
        var_type, var_kind, var_index = self.__symbols_table.get_all_info(var_name)
        tk.advance()  # current token is the var name, now the current token is '['

        # '['
        tk.advance()
        # expression
        self.write_expression()
        # ']'
        tk.advance()
        # Calculate where to store the result, push start arr address.
        self.__write_push(VAR_KIND_DICT[var_kind], var_index)
        self.__write_arithmetic("add")

    def __compile_let(self):
        """
        Compile let statement.
        """
        tk = self.__tokenizer
        # 'let'
        tk.advance()
        # varName
        var_name = tk.get_next_token()
        var_type, var_kind, var_index = self.__symbols_table.get_all_info(var_name)

        if VM_COMMENTS:
            comment = "Compiling let statement: "
            i = 0
            while tk.peek(i) and not tk.peek(i) == ';':
                comment = comment + str(tk.peek(i))
                i += 1
            self.__write_comment(comment)

        # Check if it is an array assignment.
        if self.__is_next_token_array():
            self.__compile_array_evaluation()
            # '='
            tk.advance()
            # expression
            self.write_expression()

            # Pop the value to be assign to temp 0
            self.__write_pop(TEMP, 0)
            # Pop the array address to pointer 1, meaning store at That segment.
            self.__write_pop(POINTER, 1)
            # Push the value to be assign back to the stack.
            self.__write_push(TEMP, 0)
            # Pop it to the correct place in the array, which that 0 is pointing to
            self.__write_pop(THAT, 0)

        else:
            tk.advance()
            # '='
            tk.advance()
            # expression
            self.write_expression()
            # Pop the value to be assign to the var_name location.
            self.__write_pop(VAR_KIND_DICT[var_kind], var_index)

        # ';'
        tk.advance()

    def __compile_while(self):
        """
        Build xml tree for while statement in jack.
        """
        if VM_COMMENTS:
            self.__write_comment("Compiling while statement.")

        tk = self.__tokenizer
        self.__while_statement_cnt += 1
        self.__write_label("WHILE_EXP" + str(self.__while_statement_cnt))
        # 'while'
        tk.advance()
        # '('
        tk.advance()
        # expression
        self.write_expression()
        # ')'
        tk.advance()

        self.__write_arithmetic("not")
        self.__write_if_goto("WHILE_END" + str(self.__while_statement_cnt))
        # '{'
        tk.advance()
        # statements
        self.__compile_statements()
        self.__write_go_to("WHILE_EXP" + str(self.__while_statement_cnt))
        self.__write_label("WHILE_END" + str(self.__while_statement_cnt))
        # '}'
        tk.advance()

    def __compile_return(self):
        """
        Build xml tree for return statement in jack.
        """
        if VM_COMMENTS:
            self.__write_comment("Compiling return statement. ")

        tk = self.__tokenizer
        # 'return'
        tk.advance()

        # If a value is returned, return it.
        if not (tk.get_next_token() == ';'):
            # expression
            self.write_expression_list()
            self.__write_return()
            tk.advance()
            return

        # If no value is returned, return 0.
        if VM_COMMENTS:
            self.__write_comment("No value is returned, so return 0 ")
        self.__write_push(CONST, 0)
        self.__write_return()

        # ';'
        tk.advance()

    def __compile_if(self):
        """
        Build xml tree for if statement in jack.
        """
        if VM_COMMENTS:
            self.__write_comment("Compiling if statement.")

        tk = self.__tokenizer
        self.__if_statement_cnt += 1
        # 'if'
        tk.advance()
        # '('
        tk.advance()
        # expression
        self.write_expression_list()
        if VM_COMMENTS:
            self.__write_comment("start if algorithm.")
        # self.__write_arithmetic("not")
        self.__write_if_goto("IF_TRUE" + str(self.__if_statement_cnt))
        self.__write_go_to("IF_FALSE" + str(self.__if_statement_cnt))
        self.__write_label("IF_TRUE" + str(self.__if_statement_cnt))
        # ')'
        tk.advance()
        # '{'
        tk.advance()
        # statements
        self.__compile_statements()
        self.__write_go_to("IF_END" + str(self.__if_statement_cnt))
        self.__write_label("IF_FALSE" + str(self.__if_statement_cnt))
        # '}'
        tk.advance()
        # ('else''{'statements'}')?
        if tk.get_token_type() == KEYWORD and tk.get_next_token() == ELSE:
            # 'else'
            tk.advance()
            # '{'
            tk.advance()
            # statements
            self.__compile_statements()
            # '}'
            tk.advance()
        self.__write_label("IF_END" + str(self.__if_statement_cnt))

    def write_expression_list(self):
        """
        Writes the VM commands of a list of expressions, assuming that the opening bracket, '(', was already parsed.
        Returns the number of expressions in the list.
        """
        if VM_COMMENTS:
            self.__write_comment("Parsing expression list. ")

        tk = self.__tokenizer
        number_of_expressions = 0
        # check is list is empty, meaning next token is )
        if tk.get_token_type() == SYMBOL and tk.get_next_token() == ')':
            # tk.advance()
            return number_of_expressions

        # else, parse first expression, and then loop until over
        number_of_expressions += 1
        if VM_COMMENTS:
            self.__write_comment("Expression No. # " + str(number_of_expressions))
        self.write_expression()

        # as long as there are more ',' symbols, there are more expressions in the list to parse
        while tk.get_token_type() == SYMBOL and tk.get_next_token() == ',':
            number_of_expressions += 1
            if VM_COMMENTS:
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
            if VM_COMMENTS:
                self.__write_comment("writing term, int const: " + str(current_token))
            self.__write_push(CONST, current_token)
            tk.advance()
            return

        # If term is string constant, we should push each char
        elif current_token_type == STRING_CONST:
            if VM_COMMENTS:
                self.__write_comment("writing term, string const: " + current_token)
            self.__write_push(CONST, len(current_token))  # Push the argument len(str_const) for String.new()
            self.__write_call("String.new", 1)  # Create new string
            for char in current_token:
                self.__write_push(CONST, ord(char))  # push one by one the string's chars
                self.__write_call("String.appendChar", 2)
            tk.advance()
            return

        # Array expression
        elif self.__is_next_token_array():
            self.__compile_array_evaluation()
            self.__write_pop(POINTER, 1)
            self.__write_push(THAT, 0)

        # If the term is a variable, and NOT an array and Not a function:
        elif current_token_type == IDENTIFIER and self.__symbols_table.var_exists(current_token)\
                and not tk.peek(1) == '.':
            var_kind = self.__symbols_table.get_kind(current_token)
            if VM_COMMENTS:
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
            if VM_COMMENTS:
                self.__write_comment("writing term, keyword: " + current_token)
            if current_token == FALSE:
                self.__write_push(CONST, FALSE_VALUE)  # push const 0
            elif current_token == TRUE:
                self.__write_push(CONST, FALSE_VALUE)  # push const 0
                self.__write_arithmetic("not")  # neg
            elif current_token == NULL:
                self.__write_push(CONST, NULL_VALUE)  # push const 0
            elif current_token == THIS:
                self.__write_push(POINTER, THIS_POINTER_VALUE)  # push pointer 0
            tk.advance()
            return

        # '(' expression ')'
        elif current_token_type == SYMBOL and current_token == '(':
            if VM_COMMENTS:
                self.__write_comment("writing (expression): (")
            # '('
            tk.advance()
            # expression
            self.write_expression()  # Calls itself recursively, evaluate the expression inside the parentheses
            if VM_COMMENTS:
                self.__write_comment("writing (expression): )")
            # ')'
            tk.advance()
            return

        #  ~expression or -expression
        elif current_token in UNARY_OP_LIST:
            if VM_COMMENTS:
                self.__write_comment("writing unary operation: " + current_token)

            if current_token == '-':
                tk.advance()
                self.write_term()
                self.__write_arithmetic("neg")
            else:  # current_token == '~'
                tk.advance()
                self.write_term()
                self.__write_arithmetic("not")
            # tk.advance()
            return

        #  method(exp1, exp2, ..., expn) or Class.func(exp1,...,expn)
        elif current_token_type == IDENTIFIER:
            if VM_COMMENTS:
                self.__write_comment("Writing function, " + str(tk.get_next_token()))
            tk.advance()
            self.__compile_subroutine_call(current_token)

    def write_expression(self):
        """
        Writes an expression, by writing terms until there is no more operators. Assumes the expression is not empty.
        """
        tk = self.__tokenizer
        if VM_COMMENTS:
            self.__write_comment("Writing expression, " + str(tk.get_next_token()))
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

    def __write_label(self, label_name):
        """
        Write a label to the vm file
        """
        self.__vm_file.write("label " + label_name + NEW_LINE)

    def __write_return(self):
        """
        Write return to the vm file
        """
        self.__vm_file.write("return" + NEW_LINE)

    def __write_go_to(self, label_name):
        """
        Write go_to command to the vm file
        """
        self.__vm_file.write("goto " + label_name + NEW_LINE)

    def __write_if_goto(self, label_name):
        """
        Write if-goto command to the vm file
        """
        self.__vm_file.write("if-goto " + label_name + NEW_LINE)
