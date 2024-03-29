from syntax_analyzer import *
import os


class SymbolTable:
    def __init__(self):
        self.__subroutine_symbol_dict = dict()
        # Subroutine symbol table; a dictionary in form {var_name: (var_type, var_kind, var_index)}
        # E.g., {"x": ("int", "local", 2)}.
        # Type is one of int, char, boolean or other class name
        # Kind is one of field, static, local, argument
        # Index is an inner counter for every kind

        # Class symbol table, in the same structure
        self.__class_symbol_dict = dict()

    def get_subroutine_symbol_dict(self):
        """
        a getter for subroutine_symbol_dict
        """
        return self.__subroutine_symbol_dict

    def get_class_symbol_dict(self):
        """
        a getter for class_symbol_dict
        """
        return self.__class_symbol_dict

    def start_subroutine(self):
        """
        Reset the inner dict that handles the subroutine scope.
        """
        self.__subroutine_symbol_dict = dict()

    def add_new_symbol(self, var_name, var_type, var_kind):
        """
        Adds a new variable to the symbol table. It understands by itself to which table to add.
        """
        # STATIC and FIELD identifiers have a class scope, while ARG and VAR identifiers have a subroutine scope
        if var_kind in CLASS_LEVEL_IDENTIFIERS:
            self.__class_symbol_dict[var_name] = (var_type, var_kind, self.var_count(var_kind))

        elif var_kind in SUBROUTINE_LEVEL_IDENTIFIERS:
            self.__subroutine_symbol_dict[var_name] = (var_type, var_kind, self.var_count(var_kind))

    def var_count(self, var_kind):
        """
        Returns the number of variables of the given kind already defined in the current scope.
        """
        # STATIC and FIELD identifiers have a class scope, while ARG and VAR identifiers have a subroutine scope
        if var_kind in CLASS_LEVEL_IDENTIFIERS:
            #  A nice one-liner that counts all appearances of var_kind in the dictionary
            return sum(map(lambda val: val[KIND_INDEX] == var_kind, self.__class_symbol_dict.values()))

        else:  # in case var_kind is in SUBROUTINE_LEVEL_IDENTIFIERS
            return sum(map(lambda val: val[KIND_INDEX] == var_kind, self.__subroutine_symbol_dict.values()))

    def __get_property(self, var_name, property_number):
        """
        Helper function to avoid code repetition. Returns the property of number property_number of the variable.
        In case there is no such variable, it returns None.
        """
        # First, search in the inner scope:
        if var_name in self.__subroutine_symbol_dict:
            return self.__subroutine_symbol_dict[var_name]

        # Second, search in the outer scope:
        elif var_name in self.__class_symbol_dict:
            return self.__class_symbol_dict[var_name]

        else:
            return None

    def get_kind(self, var_name):
        """
        Returns the kind (static, field, arg, var) of the given variable.
        In case there is no such variable, it returns None.
        """
        return self.__get_property(var_name, KIND_INDEX)

    def get_type(self, var_name):
        """
        Returns the type (int, char, boolean or other class name) of the given variable.
        In case there is no such variable, it returns None.
        """
        return self.__get_property(var_name, TYPE_INDEX)

    def get_index(self, var_name):
        """
        Returns the index counter of the given variable.
        In case there is no such variable, it returns None.
        """
        return self.__get_property(var_name, COUNTER_INDEX)

    def get_all_info(self, var_name):
        """
        Returns a triplet (var_type, var_kind, var_index).
        """
        if var_name in self.__subroutine_symbol_dict:
            return self.__subroutine_symbol_dict[var_name]

        # Second, search in the outer scope:
        elif var_name in self.__class_symbol_dict:
            return self.__class_symbol_dict[var_name]

        else:
            return None

    def var_exists(self, var_name):
        """
        Returns True if the variable exists in class or subroutine level tables.
        """
        return var_name in self.__subroutine_symbol_dict or var_name in self.__class_symbol_dict


if __name__ == "__main__":
    jack_path_input = sys.argv[1]

    # Check if a file or a directory of vm files.
    if os.path.isfile(jack_path_input):
        vm_file_path = jack_path_input.replace(JACK_SUFFIX, VM_SUFFIX)
        SyntaxAnalyzer(jack_path_input, vm_file_path)

    if os.path.isdir(jack_path_input):
        jack_path_input = jack_path_input.rstrip('/')
        for filename in os.listdir(jack_path_input):
            if filename.endswith(JACK_SUFFIX):
                filename_jack_path = os.path.join(jack_path_input, filename)

                vm_file_path = filename_jack_path.replace(JACK_SUFFIX, VM_SUFFIX)
                SyntaxAnalyzer(filename_jack_path, vm_file_path)
