"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

from JackTokenizer import TokenType
from JackTokenizer import JackTokenizer
import typing

XML_ESCAPE = {"<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;"}


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(
        self, input_stream: JackTokenizer, output_stream: typing.TextIO
    ) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.input_stream = input_stream
        self.output_stream = output_stream

    def write_current_token(self) -> None:
        """Writes the current token with its XML tag and advances."""
        token_type = self.input_stream.token_type()

        # Determine the tag name based on the Enum/Type
        # (Assuming you use the lowercase tag name)
        tag = token_type.lower()
        if tag == "int_const":
            tag = "integerConstant"
        elif tag == "string_const":
            tag = "stringConstant"

        val = self.input_stream.current_token
        # Strip outer quotes for string constants as required by the spec
        if token_type == TokenType.STRING_CONST:
            val = val.strip('"')

        # Escape special XML characters (e.g., <, >, &, ")
        escaped_val = XML_ESCAPE.get(val, val)

        self.output_stream.write(
            f"<{tag}> {escaped_val} </{tag}>\n"
        )  # or corresponding tag
        self.input_stream.advance()
        return

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output_stream.write("<class>\n")
        self.write_current_token()  # class
        self.write_current_token()  # className
        self.write_current_token()  # '{'
        while True:
            if self.input_stream.keyword() not in ["static", "field"]:
                break
            else:
                self.compile_class_var_dec()
        while True:
            if self.input_stream.keyword() not in ["constructor", "function", "method"]:
                break
            else:
                self.compile_subroutine()
        self.write_current_token()  # '}'
        self.output_stream.write("</class>\n")
        return

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        self.output_stream.write("<classVarDec>\n")
        # first write keyword static/field
        self.write_current_token()
        self.write_current_token()
        self.write_current_token()
        # additional varNames
        while self.input_stream.symbol() != ";":
            self.write_current_token()
            self.write_current_token()

        self.write_current_token()
        self.output_stream.write("</classVarDec>\n")

        return

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.output_stream.write("<subroutineDec>" + "\n")
        self.write_current_token()  # ('constructor' | 'function' | 'method')
        self.write_current_token()  # ('void' | type)
        self.write_current_token()  # subroutineName
        self.write_current_token()  # '('
        self.compile_parameter_list()
        self.write_current_token()  # ')'
        self.output_stream.write("<subroutineBody>" + "\n")
        self.write_current_token()  # '{'
        while self.input_stream.keyword() == "var":
            self.output_stream.write("<varDec>\n")
            self.compile_var_dec()
            self.output_stream.write("</varDec>\n")
        self.compile_statements()
        self.write_current_token()  # '}'
        self.output_stream.write("</subroutineBody>" + "\n")
        self.output_stream.write("</subroutineDec>" + "\n")

        return

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        # Your code goes here!
        self.output_stream.write("<parameterList>\n")
        if self.input_stream.token_type() != TokenType.SYMBOL:
            self.write_current_token()  # 'type'
            self.write_current_token()  # 'varName'
        while self.input_stream.symbol() != ")":
            self.write_current_token()  # ','
            self.write_current_token()  # 'type'
            self.write_current_token()  # 'varName'

        self.output_stream.write("</parameterList>\n")

        return

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.write_current_token()  # 'var'
        self.write_current_token()  # type
        self.write_current_token()  # varName
        if self.input_stream.symbol() == ";":
            self.write_current_token()  # ';'
            return
        elif self.input_stream.symbol() == ",":
            while self.input_stream.symbol() != ";":
                self.write_current_token()  # ','
                self.write_current_token()  # varName
        self.write_current_token()  # ';'
        return

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        self.output_stream.write("<statements>\n")
        while (
            self.input_stream.token_type() == TokenType.KEYWORD
            and self.input_stream.keyword() in ["let", "if", "while", "do", "return"]
        ):
            if self.input_stream.keyword() == "let":
                self.compile_let()
            elif self.input_stream.keyword() == "if":
                self.compile_if()
            elif self.input_stream.keyword() == "while":
                self.compile_while()
            elif self.input_stream.keyword() == "do":
                self.compile_do()
            elif self.input_stream.keyword() == "return":
                self.compile_return()
        self.output_stream.write("</statements>\n")
        return

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output_stream.write("<doStatement>" + "\n")
        self.write_current_token()  # do
        self.write_current_token()  # stringConstant, identifier, intConstant, keyword

        if self.input_stream.symbol() == "(":  # subroutineCall
            self.write_current_token()  # '('
            self.compile_expression_list()
            self.write_current_token()  # ')'
        elif self.input_stream.symbol() == ".":
            self.write_current_token()  #'.'
            self.write_current_token()  # subroutine name
            self.write_current_token()  #'('
            self.compile_expression_list()
            self.write_current_token()  #')'
        self.write_current_token()  #';'
        self.output_stream.write("</doStatement>" + "\n")
        return

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output_stream.write("<letStatement>" + "\n")
        self.write_current_token()  # let
        self.write_current_token()  # varName
        if self.input_stream.symbol() == "[":
            self.write_current_token()  # '['
            self.compile_expression()
            self.write_current_token()  # ']'
        self.write_current_token()  # '='
        self.compile_expression()
        self.write_current_token()  # ';'
        self.output_stream.write("</letStatement>" + "\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output_stream.write("<whileStatement>" + "\n")
        self.write_current_token()  # while
        self.write_current_token()  # '('
        self.compile_expression()
        self.write_current_token()  # ')'
        self.write_current_token()  # '{'
        self.compile_statements()
        self.write_current_token()  # '}'
        self.output_stream.write("</whileStatement>" + "\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        self.output_stream.write("<returnStatement>" + "\n")
        self.write_current_token()  # return
        if not (
            self.input_stream.token_type() == TokenType.SYMBOL
            and self.input_stream.symbol() == ";"
        ):
            self.compile_expression()
        self.write_current_token()  # ';'
        self.output_stream.write("</returnStatement>" + "\n")
        return

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output_stream.write("<ifStatement>" + "\n")
        self.write_current_token()  # if
        self.write_current_token()  # '('
        self.compile_expression()
        self.write_current_token()  # ')'
        self.write_current_token()  # '{'
        self.compile_statements()
        self.write_current_token()  # '}'
        if self.input_stream.keyword() == "else":
            self.write_current_token()  # else
            self.write_current_token()  # '{'
            self.compile_statements()
            self.write_current_token()  # '}'
        self.output_stream.write("</ifStatement>" + "\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output_stream.write("<expression>" + "\n")
        self.compile_term()
        while self.input_stream.symbol() in [
            "+",
            "-",
            "*",
            "/",
            "&",
            "|",
            "<",
            ">",
            "=",
        ]:
            self.write_current_token()  # op
            self.compile_term()

        self.output_stream.write("</expression>" + "\n")

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.output_stream.write("<term>\n")
        if self.input_stream.symbol() in ["-", "~", "^", "#"]:
            self.write_current_token()  # unary op
            self.compile_term()

        elif self.input_stream.symbol() == "(":  # expression
            self.write_current_token()  # '('
            self.compile_expression()  # expression
            self.write_current_token()  # ')'

        else:
            self.write_current_token()  # stringConstant, identifier, intConstant, keyword
            if self.input_stream.symbol() == "[":  # varName
                self.write_current_token()  # '['
                self.compile_expression()
                self.write_current_token()  # ']'
            elif self.input_stream.symbol() == "(":  # subroutineCall
                self.write_current_token()  # '('
                self.compile_expression_list()
                self.write_current_token()  # ')'
            elif self.input_stream.symbol() == ".":
                self.write_current_token()  # '.'
                self.write_current_token()  # subroutineName
                self.write_current_token()  # '('
                self.compile_expression_list()
                self.write_current_token()  # ')'
        self.output_stream.write("</term>\n")
        return

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output_stream.write("<expressionList>\n")
        if self.input_stream.symbol() != ")":
            self.compile_expression()
            while self.input_stream.symbol() != ")":
                self.write_current_token()
                self.compile_expression()

        self.output_stream.write("</expressionList>\n")

        return
