"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from Parser import COMMAND_TYPE
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code

def replace_symbols(parser: Parser, symbol_table: SymbolTable):
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == COMMAND_TYPE.L_COMMAND:

            symbol_table.add_entry(parser.symbol(), parser.next_cmd_idx-1)
            parser.delete_current_line()

            
    parser.reset()
    parser.advance()
    while parser.has_more_commands():
        if parser.command_type() == COMMAND_TYPE.C_COMMAND:
            parser.advance()
            continue
        symbol = parser.symbol()
        try:
            int(symbol)
        except ValueError:
            if not symbol_table.contains(symbol):
                symbol_table.add_entry(symbol, symbol_table.new_symbol_address)
                symbol_table.increment_new_symbol_address()
        parser.advance()
    parser.reset()

def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    parser = Parser(input_file)
    symbol_table = SymbolTable()
    replace_symbols(parser, symbol_table)
    code = Code()
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == COMMAND_TYPE.A_COMMAND:
            symbol = symbol_table.get_address(parser.symbol(),parser.symbol())
            binary_command = bin(int(symbol))[2:]
            binary_string = "0" * (16 - len(binary_command)) + binary_command
            output_file.write(binary_string+'\n')
        elif parser.command_type() == COMMAND_TYPE.C_COMMAND:
            comp = code.comp(parser.comp())
            dest = code.dest(parser.dest())
            jump = code.jump(parser.jump())
            binary_string = "111"+comp+dest+jump
            output_file.write(binary_string+'\n')


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
