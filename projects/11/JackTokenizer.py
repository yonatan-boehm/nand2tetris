"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import typing
from enum import Enum


class TokenType(str, Enum):
    KEYWORD = "KEYWORD"
    SYMBOL = "SYMBOL"
    IDENTIFIER = "IDENTIFIER"
    INT_CONST = "INT_CONST"
    STRING_CONST = "STRING_CONST"


KEYWORDS = [
    "class",
    "constructor",
    "function",
    "method",
    "field",
    "static",
    "var",
    "int",
    "char",
    "boolean",
    "void",
    "true",
    "false",
    "null",
    "this",
    "let",
    "do",
    "if",
    "else",
    "while",
    "return",
]

SYMBOLS = [
    "{",
    "}",
    "(",
    ")",
    "[",
    "]",
    ".",
    ",",
    ";",
    "+",
    "-",
    "*",
    "/",
    "&",
    "|",
    "<",
    ">",
    "=",
    "~",
    "^",
    "#",
]


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.

    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters,
    and comments, which are ignored. There are three possible comment formats:
    /* comment until closing */ , /** API comment until closing */ , and
    // comment until the line's end.

    - 'xxx': quotes are used for tokens that appear verbatim ('terminals').
    - xxx: regular typeface is used for names of language constructs
           ('non-terminals').
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' |
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' |
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate
    file. A compilation unit is a single class. A class is a sequence of tokens
    structured according to the following context free syntax:

    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement |
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions

    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName |
            varName '['expression']' | subroutineCall | '(' expression ')' |
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className |
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'

    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_stream.read().splitlines()

        self.input_lines = input_stream.read().splitlines()
        self.current_line = self.input_lines[0]
        self.current_line_index = 0
        self.next_token_index = 0
        self.token_type_var = None
        self.current_token = None
        # needs to handle comments and whitespace

    def has_more_tokens(self) -> bool:
        return self.current_line is not None

    def _advance_line(self):
        """Move to the next input line, or set current_line to None if done."""
        self.current_line_index += 1
        self.next_token_index = 0
        if self.current_line_index >= len(self.input_lines):
            self.current_line = None
        else:
            self.current_line = self.input_lines[self.current_line_index]

    def skip_comments(self):
        """Skip whitespace, line comments (//), and block comments (/* */)."""
        while self.current_line is not None:
            # Skip whitespace from current position
            while self.next_token_index < len(self.current_line) and self.current_line[
                self.next_token_index
            ] in (" ", "\t", "\r"):
                self.next_token_index += 1

            # Line exhausted - move to next
            if self.next_token_index >= len(self.current_line):
                self._advance_line()

            # Line comment - skip entire rest of line
            elif (
                self.current_line[self.next_token_index : self.next_token_index + 2]
                == "//"
            ):
                self._advance_line()

            # Block comment - find closing */
            elif (
                self.current_line[self.next_token_index : self.next_token_index + 2]
                == "/*"
            ):
                close_idx = self.current_line.find("*/", self.next_token_index + 2)
                while close_idx == -1:
                    self._advance_line()
                    close_idx = self.current_line.find("*/")
                self.next_token_index = close_idx + 2

            # Found a real token - done
            else:
                break

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        self.skip_comments()

        if self.current_line is None:
            return

        if self.current_line[self.next_token_index] == '"':  # string constant
            token_end_index = self.current_line.find('"', self.next_token_index + 1)
            self.current_token = self.current_line[
                self.next_token_index : token_end_index + 1
            ]
            self.next_token_index = token_end_index + 1

        elif self.current_line[self.next_token_index] in SYMBOLS:  # symbol
            self.current_token = self.current_line[self.next_token_index]
            self.next_token_index += 1

        else:  # keyword, identifier, or integer constant
            token_end_index = self.next_token_index
            while (
                token_end_index < len(self.current_line)
                and self.current_line[token_end_index] not in SYMBOLS
                and self.current_line[token_end_index] not in (" ", "\t")
            ):
                token_end_index += 1

            self.current_token = self.current_line[
                self.next_token_index : token_end_index
            ]
            self.next_token_index = token_end_index

        if self.next_token_index >= len(self.current_line):
            self._advance_line()
        return

    def token_type(self) -> TokenType:
        """
        Returns:
            TokenType: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.current_token in SYMBOLS:
            return TokenType.SYMBOL
        elif self.current_token in KEYWORDS:
            return TokenType.KEYWORD
        elif self.current_token[0].isdigit():
            return TokenType.INT_CONST
        elif self.current_token[0] == '"':
            return TokenType.STRING_CONST
        else:
            return TokenType.IDENTIFIER

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.current_token if self.token_type() == TokenType.KEYWORD else None

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return self.current_token if self.token_type() == TokenType.SYMBOL else None

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.current_token if self.token_type() == TokenType.IDENTIFIER else None

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return self.current_token if self.token_type() == TokenType.INT_CONST else None

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
        """
        return (
            self.current_token if self.token_type() == TokenType.STRING_CONST else None
        )
