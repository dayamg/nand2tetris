from constants import *
import os
import re
import sys

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


class JackTokenizer:
    """
    No other option seems reasonable, so we probably need to use OOP.  :(
    """

    def __init__(self, input_jack_file):
        """
        Yeah, this funky function is for constructing shit, you know.
        """
        self.__input_file = input_jack_file  # the input file, of file type
        self.__next_token = None  # a tuple, (token, token_type).
        self.__next_token_type = None  # token_type is one of TOKEN_TYPE_DICT keys.

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

    def peek(self, how_far):
        self.__token_index += how_far
        if self.has_more_tokens():
            self.__next_token = self.__token_list[self.__token_index]
            self.__token_index -= how_far
            return self.__next_token[0]

        self.__token_index -= how_far
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

        if element in KEYWORD_LIST:
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
