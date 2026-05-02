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

def first_pass(parser: Parser, symbol_table: SymbolTable) -> None:
    """
    Goes through the entire assembly program, only paying attention to (XXX) pseudo-commands.
    Adds them to the symbol table with their corresponding ROM address.
    """
    rom_address = 0
    while parser.has_more_commands():
        parser.advance()
        cmd_type = parser.command_type()
        if cmd_type == COMMAND_TYPE.L_COMMAND:
            symbol = parser.symbol()
            symbol_table.add_entry(symbol, rom_address)
        elif cmd_type in (COMMAND_TYPE.A_COMMAND, COMMAND_TYPE.C_COMMAND):
            rom_address += 1

def second_pass(parser: Parser, symbol_table: SymbolTable, output_file: typing.TextIO) -> None:
    """
    Translates commands to binary and handles variables.
    """
    code = Code()
    parser.reset()
    while parser.has_more_commands():
        parser.advance()
        cmd_type = parser.command_type()
        
        if cmd_type == COMMAND_TYPE.A_COMMAND:
            symbol = parser.symbol()
            if symbol.isdigit():
                address = int(symbol)
            else:
                if not symbol_table.contains(symbol):
                    symbol_table.add_entry(symbol, symbol_table.new_symbol_address)
                    symbol_table.increment_new_symbol_address()
                address = symbol_table.get_address(symbol)
            
            binary_string = bin(address)[2:].zfill(16)
            output_file.write(binary_string + '\n')
            
        elif cmd_type == COMMAND_TYPE.C_COMMAND:
            comp = code.comp(parser.comp())
            dest = code.dest(parser.dest())
            jump = code.jump(parser.jump())
            binary_string = "111" + comp + dest + jump
            output_file.write(binary_string + '\n')

def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    parser = Parser(input_file)
    symbol_table = SymbolTable()
    
    first_pass(parser, symbol_table)
    second_pass(parser, symbol_table, output_file)


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
