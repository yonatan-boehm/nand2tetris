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
    A_COMMAND = "A_COMMAND"
    C_COMMAND = "C_COMMAND"
    L_COMMAND = "L_COMMAND"

class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_lines = self._filter_lines(input_file.read().splitlines())
        self.current_command = None
        self.next_cmd_idx = 0

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.next_cmd_idx < len(self.input_lines)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.current_command = self.input_lines[self.next_cmd_idx]
            self.next_cmd_idx += 1
        return

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        cmd = self.current_command
        if cmd.startswith('(') and cmd.endswith(')'):
            return COMMAND_TYPE.L_COMMAND
        if cmd.startswith('@'):
            return COMMAND_TYPE.A_COMMAND
        return COMMAND_TYPE.C_COMMAND

        

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.command_type() == COMMAND_TYPE.A_COMMAND:
            return self.current_command[1:]
        elif self.command_type() == COMMAND_TYPE.L_COMMAND:
            return self.current_command[1:-1]
        else:
            raise Exception('invalid command type')

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when command_type() is "C_COMMAND".
        """
        if self.command_type() != COMMAND_TYPE.C_COMMAND:
            raise Exception('invalid command type')
        dest_part = self.current_command
        if '=' in dest_part:
            return dest_part.split('=')[0]
        return ""
        

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when command_type() is "C_COMMAND".
        """
        if self.command_type() != COMMAND_TYPE.C_COMMAND:
            raise Exception('invalid command type')
        comp_part = self.current_command
        if "=" in comp_part:
            comp_part = comp_part.split('=')[1]
        if ";" in comp_part:
            comp_part = comp_part.split(';')[0]
        return comp_part

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when command_type() is "C_COMMAND".
        """
        if self.command_type() != COMMAND_TYPE.C_COMMAND:
            raise Exception('invalid command type')
        jump_index = self.current_command.find(';')
        if jump_index == -1:
            return "null"
        return self.current_command[jump_index + 1:]
    
    def _filter_lines(self, input_lines: list[str]) -> list[str]:
        filtered_lines = []
        for line in input_lines:
            stripped_line = line.replace(" ", "")
            if stripped_line.startswith("//") or stripped_line == "":
                continue
            if "//" in stripped_line:
                stripped_line = stripped_line.split("//")[0]
            filtered_lines.append(stripped_line)
        return filtered_lines
    
    def reset(self) -> None:
        self.current_command = None
        self.next_cmd_idx = 0