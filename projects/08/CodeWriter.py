"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import os
import typing

from Parser import COMMAND_TYPE


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.output_file = output_stream
        self.conditional_counter = 0
        self.current_function = None
        self.current_function_ret_counter = 0
        self.filename = os.path.basename(self.output_file.name)
        self.segment_dict = {
            "this": "THIS",
            "that": "THAT",
            "local": "LCL",
            "argument": "ARG",
            "temp": "5",
        }
        return

    def write_init(self) -> None:
        """Writes the bootstrap code that initializes the VM.
        This code must be placed at the beginning of the output file.
        Sets SP=256 and calls Sys.init.
        """
        self.output_file.write("// bootstrap code" + "\n")
        # SP = 256
        self.output_file.write("@256" + "\n")
        self.output_file.write("D=A" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("M=D" + "\n")
        # call Sys.init
        self.current_function = "bootstrap"
        self.write_call("Sys.init", 0)

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.filename = os.path.splitext(filename)[0]
        return

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        # Your code goes here!
        self.output_file.write(f"//{command}" + "\n")
        if command == "add" or command == "sub":
            self.output_file.write("@SP" + "\n")
            self.output_file.write("A=M-1" + "\n")
            self.output_file.write("D=M" + "\n")
            self.output_file.write("A=A-1" + "\n")
            op = "M=D+M" if command == "add" else "M=M-D"
            self.output_file.write(op + "\n")
            self.output_file.write("@SP" + "\n")
            self.output_file.write("M=M-1" + "\n")
        elif command == "neg":
            self.output_file.write("@SP" + "\n")
            self.output_file.write("A=M-1" + "\n")
            self.output_file.write("M=-M" + "\n")
        elif command in ["and", "or"]:
            cond = "&" if command == "and" else "|"
            self.output_file.write("@SP" + "\n")
            self.output_file.write("A=M-1" + "\n")
            self.output_file.write("D=M" + "\n")
            self.output_file.write("A=A-1" + "\n")
            self.output_file.write(f"M=D{cond}M" + "\n")
            self.output_file.write("@SP" + "\n")
            self.output_file.write("M=M-1" + "\n")
        elif command in ["not", "shiftright", "shiftleft"]:
            self.output_file.write("@SP" + "\n")
            self.output_file.write("A=M-1" + "\n")
            if command == "not":
                self.output_file.write("M=!M" + "\n")
            elif command == "shiftleft":
                self.output_file.write("M=M<<" + "\n")
            else:
                self.output_file.write("M=M>>" + "\n")
        else:
            true_label = f"CONDITIONAL_TRUE.{self.conditional_counter}"
            false_label = f"CONDITIONAL_FALSE.{self.conditional_counter}"
            end_label = f"CONDITIONAL_END.{self.conditional_counter}"

            if command == "eq":
                self.output_file.write("@SP" + "\n")
                self.output_file.write("A=M-1" + "\n")
                self.output_file.write("D=M" + "\n")
                self.output_file.write("A=A-1" + "\n")
                self.output_file.write("D=M-D" + "\n")
                self.output_file.write(f"@{true_label}" + "\n")
                self.output_file.write("D;JEQ" + "\n")
            else:
                same_sign_label = f"CONDITIONAL_SAME_SIGN.{self.conditional_counter}"
                x_negative_label = f"CONDITIONAL_X_NEGATIVE.{self.conditional_counter}"

                self.output_file.write("@SP" + "\n")
                self.output_file.write("A=M-1" + "\n")
                self.output_file.write("D=M" + "\n")
                self.output_file.write("@R13" + "\n")
                self.output_file.write("M=D" + "\n")
                self.output_file.write("@SP" + "\n")
                self.output_file.write("A=M-1" + "\n")
                self.output_file.write("A=A-1" + "\n")
                self.output_file.write("D=M" + "\n")
                self.output_file.write(f"@{x_negative_label}" + "\n")
                self.output_file.write("D;JLT" + "\n")
                self.output_file.write("@R13" + "\n")
                self.output_file.write("D=M" + "\n")
                self.output_file.write(f"@{same_sign_label}" + "\n")
                self.output_file.write("D;JGE" + "\n")
                self.output_file.write(
                    f"@{true_label if command == 'gt' else false_label}" + "\n"
                )
                self.output_file.write("0;JMP" + "\n")
                self.output_file.write(f"({x_negative_label})" + "\n")
                self.output_file.write("@R13" + "\n")
                self.output_file.write("D=M" + "\n")
                self.output_file.write(f"@{same_sign_label}" + "\n")
                self.output_file.write("D;JLT" + "\n")
                self.output_file.write(
                    f"@{true_label if command == 'lt' else false_label}" + "\n"
                )
                self.output_file.write("0;JMP" + "\n")
                self.output_file.write(f"({same_sign_label})" + "\n")
                self.output_file.write("@SP" + "\n")
                self.output_file.write("A=M-1" + "\n")
                self.output_file.write("D=M" + "\n")
                self.output_file.write("A=A-1" + "\n")
                self.output_file.write("D=M-D" + "\n")
                self.output_file.write(f"@{true_label}" + "\n")
                self.output_file.write(("D;JGT" if command == "gt" else "D;JLT") + "\n")

            self.output_file.write(f"({false_label})" + "\n")
            self.output_file.write("@SP" + "\n")
            self.output_file.write("A=M-1" + "\n")
            self.output_file.write("A=A-1" + "\n")
            self.output_file.write("M=0" + "\n")
            self.output_file.write(f"@{end_label}" + "\n")
            self.output_file.write("0;JMP" + "\n")
            self.output_file.write(f"({true_label})" + "\n")
            self.output_file.write("@SP" + "\n")
            self.output_file.write("A=M-1" + "\n")
            self.output_file.write("A=A-1" + "\n")
            self.output_file.write("M=-1" + "\n")
            self.output_file.write(f"({end_label})" + "\n")
            self.output_file.write("@SP" + "\n")
            self.output_file.write("M=M-1" + "\n")
            self.conditional_counter += 1
        return

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        if command == COMMAND_TYPE.C_PUSH:
            self.output_file.write(f"// push {segment} {index}" + "\n")
            if segment == "constant":
                self.output_file.write(f"@{index}" + "\n")
                self.output_file.write("D=A" + "\n")
                self.output_file.write("@SP" + "\n")
                self.output_file.write("A=M" + "\n")
                self.output_file.write("M=D" + "\n")
                self.output_file.write("@SP" + "\n")
                self.output_file.write("M=M+1" + "\n")
                return

            if segment in self.segment_dict:
                comp = "A" if segment == "temp" else "M"
                self.output_file.write(f"@{self.segment_dict[segment]}\n")
                self.output_file.write(f"D={comp}" + "\n")
                self.output_file.write(f"@{index}" + "\n")
                self.output_file.write(f"A=D+A" + "\n")
                self.output_file.write("D=M" + "\n")
                self.output_file.write("@SP" + "\n")
                self.output_file.write("A=M" + "\n")
                self.output_file.write("M=D" + "\n")
                self.output_file.write("@SP" + "\n")
                self.output_file.write("M=M+1" + "\n")
                return

            if segment in ["pointer", "static"]:
                address = (
                    f"{self.filename}.{index}"
                    if segment == "static"
                    else ("THAT" if index == 1 else "THIS")
                )
                self.output_file.write(f"@{address}" + "\n")
                self.output_file.write("D=M" + "\n")
                self.output_file.write("@SP" + "\n")
                self.output_file.write("A=M" + "\n")
                self.output_file.write("M=D" + "\n")
                self.output_file.write("@SP" + "\n")
                self.output_file.write("M=M+1" + "\n")
                return

        elif command == COMMAND_TYPE.C_POP:
            self.output_file.write(f"// pop {segment} {index}" + "\n")
            comp = "A" if segment == "temp" else "M"
            if segment in self.segment_dict:
                self.output_file.write(f"@{self.segment_dict[segment]}" + "\n")
                self.output_file.write(f"D={comp}" + "\n")
                self.output_file.write(f"@{index}" + "\n")
                self.output_file.write(f"D=D+A" + "\n")
                self.output_file.write("@R13" + "\n")
                self.output_file.write("M=D" + "\n")
                self.output_file.write("@SP" + "\n")
                self.output_file.write("AM=M-1" + "\n")
                self.output_file.write("D=M" + "\n")
                self.output_file.write("@R13" + "\n")
                self.output_file.write("A=M" + "\n")
                self.output_file.write("M=D" + "\n")
                return

            if segment in ["pointer", "static"]:
                address = (
                    f"{self.filename}.{index}"
                    if segment == "static"
                    else ("THAT" if index == 1 else "THIS")
                )
                self.output_file.write("@SP" + "\n")
                self.output_file.write("AM=M-1" + "\n")
                self.output_file.write("D=M" + "\n")
                self.output_file.write(f"@{address}" + "\n")
                self.output_file.write("M=D" + "\n")
                return
        return

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command.
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        self.output_file.write(f"// label {label}" + "\n")
        self.output_file.write(f"({self.current_function}${label})" + "\n")
        return

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        self.output_file.write(f"// goto {label}" + "\n")
        self.output_file.write(f"@{self.current_function}${label}" + "\n")
        self.output_file.write("0;JMP" + "\n")
        return

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        self.output_file.write(f"//if goto {label}" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("AM=M-1" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write(f"@{self.current_function}${label}" + "\n")
        self.output_file.write("D;JNE" + "\n")
        return

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command.
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self.current_function = function_name
        self.current_function_ret_counter = 0
        self.output_file.write(f"//write function {function_name} {n_vars}" + "\n")
        self.output_file.write(f"({function_name})" + "\n")
        if n_vars != 0:
            self.output_file.write(f"@{n_vars}" + "\n")
            self.output_file.write("D=A" + "\n")
            self.output_file.write("@R13" + "\n")
            self.output_file.write("M=D" + "\n")
            self.output_file.write(f"({function_name}.setup_loop)" + "\n")
            self.output_file.write("@R13" + "\n")
            self.output_file.write("D=M" + "\n")
            self.output_file.write("@SP" + "\n")
            self.output_file.write("A=M" + "\n")
            self.output_file.write("M=0" + "\n")
            self.output_file.write("@SP" + "\n")
            self.output_file.write("M=M+1" + "\n")
            self.output_file.write("@R13" + "\n")
            self.output_file.write("M=M-1" + "\n")
            self.output_file.write("D=M" + "\n")
            self.output_file.write(f"@{function_name}.setup_loop" + "\n")
            self.output_file.write("D;JGT" + "\n")

        return

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command.
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        self.output_file.write(f"// call {function_name}" + "\n")
        # push return_address   // generates a label and pushes it to the stack
        self.output_file.write(
            f"@{self.current_function}$ret.{self.current_function_ret_counter}" + "\n"
        )
        self.output_file.write("D=A" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("A=M" + "\n")
        self.output_file.write("M=D" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("M=M+1" + "\n")
        # push LCL              // saves LCL of the caller
        self.output_file.write("@LCL" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("A=M" + "\n")
        self.output_file.write("M=D" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("M=M+1" + "\n")
        # push ARG              // saves ARG of the caller
        self.output_file.write("@ARG" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("A=M" + "\n")
        self.output_file.write("M=D" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("M=M+1" + "\n")
        # push THIS             // saves THIS of the caller
        self.output_file.write("@THIS" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("A=M" + "\n")
        self.output_file.write("M=D" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("M=M+1" + "\n")
        # push THAT             // saves THAT of the caller
        self.output_file.write("@THAT" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("A=M" + "\n")
        self.output_file.write("M=D" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("M=M+1" + "\n")
        # ARG = SP-5-n_args     // repositions ARG
        self.output_file.write("@SP" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@5" + "\n")
        self.output_file.write("D=D-A" + "\n")
        self.output_file.write(f"@{n_args}" + "\n")
        self.output_file.write("D=D-A" + "\n")
        self.output_file.write("@ARG" + "\n")
        self.output_file.write("M=D" + "\n")
        # LCL = SP              // repositions LCL
        self.output_file.write("@SP" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@LCL" + "\n")
        self.output_file.write("M=D" + "\n")
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        self.output_file.write(f"@{function_name}" + "\n")
        self.output_file.write("0;JMP" + "\n")
        self.output_file.write(
            f"({self.current_function}$ret.{self.current_function_ret_counter})" + "\n"
        )
        self.current_function_ret_counter += 1
        return

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        self.output_file.write("@LCL" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@R13" + "\n")
        self.output_file.write("M=D" + "\n")
        # return_address = *(frame-5)   // puts the return address in a temp var
        self.output_file.write("@5" + "\n")
        self.output_file.write("A=D-A" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@R14" + "\n")
        self.output_file.write("M=D" + "\n")
        # *ARG = pop()                  // repositions the return value for the caller
        self.output_file.write("@SP" + "\n")
        self.output_file.write("AM=M-1" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@ARG" + "\n")
        self.output_file.write("A=M" + "\n")
        self.output_file.write("M=D" + "\n")
        # SP = ARG + 1                  // repositions SP for the caller
        self.output_file.write("@ARG" + "\n")
        self.output_file.write("D=M+1" + "\n")
        self.output_file.write("@SP" + "\n")
        self.output_file.write("M=D" + "\n")
        # THAT = *(frame-1)             // restores THAT for the caller
        self.output_file.write("@R13" + "\n")
        self.output_file.write("AM=M-1" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@THAT" + "\n")
        self.output_file.write("M=D" + "\n")
        # THIS = *(frame-2)             // restores THIS for the caller
        self.output_file.write("@R13" + "\n")
        self.output_file.write("AM=M-1" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@THIS" + "\n")
        self.output_file.write("M=D" + "\n")
        # ARG = *(frame-3)              // restores ARG for the caller
        self.output_file.write("@R13" + "\n")
        self.output_file.write("AM=M-1" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@ARG" + "\n")
        self.output_file.write("M=D" + "\n")
        # LCL = *(frame-4)              // restores LCL for the caller
        self.output_file.write("@R13" + "\n")
        self.output_file.write("AM=M-1" + "\n")
        self.output_file.write("D=M" + "\n")
        self.output_file.write("@LCL" + "\n")
        self.output_file.write("M=D" + "\n")
        # goto return_address           // go to the return address
        self.output_file.write("@R14" + "\n")
        self.output_file.write("A=M" + "\n")
        self.output_file.write("0;JMP" + "\n")
        return
