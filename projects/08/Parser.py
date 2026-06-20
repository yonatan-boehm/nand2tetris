"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

from enum import Enum
import typing


class COMMAND_TYPE(Enum):
    C_ARITHMETIC = "C_ARITHMETIC"
    C_POP = "C_POP"
    C_PUSH = "C_PUSH"
    C_LABEL = "C_LABEL"
    C_GOTO = "C_GOTO"
    C_IF = "C_IF"
    C_FUNCTION = "C_FUNCTION"
    C_RETURN = "C_RETURN"
    C_CALL = "C_CALL"


class Parser:
    """
    # Parser

    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient
    access to their components.
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line's end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that,
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        self.input_lines = self._filter_lines(input_file.read().splitlines())
        self.current_command = None
        self.next_cmd_idx = 0
        self.arithmetic_commands = [
            "add",
            "sub",
            "and",
            "or",
            "eq",
            "gt",
            "lt",
            "neg",
            "not",
            "shiftleft",
            "shiftright",
        ]

    def has_more_commands(self) -> bool:
        return self.next_cmd_idx < len(self.input_lines)

    def advance(self) -> None:
        if self.has_more_commands():
            self.current_command = self.input_lines[self.next_cmd_idx]
            self.next_cmd_idx += 1
        return

    def command_type(self) -> str:
        first_word = self.current_command.split(" ")[0]
        if first_word in self.arithmetic_commands:
            return COMMAND_TYPE.C_ARITHMETIC
        elif first_word == "pop":
            return COMMAND_TYPE.C_POP
        elif first_word == "push":
            return COMMAND_TYPE.C_PUSH
        elif first_word == "label":
            return COMMAND_TYPE.C_LABEL
        elif first_word == "goto":
            return COMMAND_TYPE.C_GOTO
        elif first_word == "if-goto":
            return COMMAND_TYPE.C_IF
        elif first_word == "function":
            return COMMAND_TYPE.C_FUNCTION
        elif first_word == "call":
            return COMMAND_TYPE.C_CALL
        elif first_word == "return":
            return COMMAND_TYPE.C_RETURN
        return None

    def arg1(self) -> str:
        if self.command_type() == COMMAND_TYPE.C_RETURN:
            return None
        elif self.command_type() == COMMAND_TYPE.C_ARITHMETIC:
            return self.current_command
        else:
            return self.current_command.split(" ")[1]

    def arg2(self) -> int:
        if self.command_type() in [
            COMMAND_TYPE.C_POP,
            COMMAND_TYPE.C_PUSH,
            COMMAND_TYPE.C_FUNCTION,
            COMMAND_TYPE.C_CALL,
        ]:
            return int(self.current_command.split(" ")[-1])
        return None

    def _filter_lines(self, input_lines: list[str]) -> list[str]:
        filtered_lines = []
        for line in input_lines:
            stripped_line = line.strip()
            if stripped_line.startswith("//") or stripped_line == "":
                continue
            if "//" in stripped_line:
                stripped_line = stripped_line.split("//")[0]
            filtered_lines.append(stripped_line.strip())
        return filtered_lines
